"""Every token of a novel with its lemma and tags.

Novels from the annotated corpora keep their (CLASSLA) annotation; the others
are tagged here with CLASSLA. The TEI files split paragraphs differently, but
without whitespace hold the same characters, so position gives the paragraph.
"""

import re
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable
from pathlib import Path

import numpy as np
import pandas as pd

from emotion_explorer.paths import MODELS_DIR

TEI = "{http://www.tei-c.org/ns/1.0}"
WHITESPACE_RE = re.compile(r"\s+")
# Morphology keys that are no morphology, or repeat another column.
NOT_FEATS = {"UPosTag", "UposTag", "XPOS", "SpaceAfter"}
# The standard tagger reads predicative "sram ga je" as ADJ "sra" or VERB
# "srati"; the nonstandard one reads it as a noun, as the annotated corpora do.
PROCESSORS = {
    "tokenize": "standard",
    "pos": "nonstandard",
    "lemma": "standard",
    "ner": "standard",
}

COLUMNS = ["para_id", "sentence", "form", "lemma", "upos", "feats", "entity"]
Row = tuple


def split_msd(msd: str) -> tuple[str | None, str | None]:
    """(part of speech, morphology) from a TEI `msd` attribute."""
    pairs = [p.split("=", 1) for p in msd.split("|") if "=" in p]
    upos = next((v for k, v in pairs if k in ("UPosTag", "UposTag")), None)
    feats = "|".join(f"{k}={v}" for k, v in pairs if k not in NOT_FEATS)
    return upos, feats or None


def read_tei(path: Path) -> list[Row]:
    """Every token in reading order, punctuation included; para_id still unset."""
    rows = []
    sentence = -1
    entities = []
    for event, element in ET.iterparse(path, events=("start", "end")):
        tag = element.tag.removeprefix(TEI)
        if event == "start":
            if tag == "s":
                sentence += 1
            elif tag == "name":
                entities.append(element.get("type"))
        elif tag == "name":
            entities.pop()
        elif tag in ("w", "pc"):
            upos, feats = split_msd(element.get("msd", ""))
            rows.append(
                (
                    None,
                    sentence,
                    element.text or "",
                    element.get("lemma") or element.text or "",
                    element.get("pos") or upos,
                    feats,
                    entities[-1] if entities else None,
                )
            )
    return rows


def no_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub("", text)


def paragraph_of_tokens(forms: list[str], texts: list[str]) -> np.ndarray:
    """Index of the paragraph each token starts in; len(texts) past the end.

    Tokens may run past the paragraphs (one ELTeC novel); other differences fail.
    """
    tei = [no_whitespace(f) for f in forms]
    paragraphs = [no_whitespace(t) for t in texts]
    if not "".join(tei).startswith("".join(paragraphs)):
        raise ValueError("The tokens do not hold the text of the paragraphs")
    starts = np.cumsum([0, *map(len, tei)])[:-1]
    return np.searchsorted(np.cumsum(list(map(len, paragraphs))), starts, side="right")


def assign_paragraphs(rows: list[Row], texts: list[str]) -> list[Row]:
    """The rows with their para_id; tokens past the paragraphs are dropped."""
    paragraph = paragraph_of_tokens([row[2] for row in rows], texts)
    placed = ((int(p), *row[1:]) for p, row in zip(paragraph, rows, strict=True))
    return [row for row in placed if row[0] < len(texts)]


def load_tagger() -> Callable:
    """The CLASSLA pipeline. Its packages are in the optional `corpus` group."""
    import classla

    folder = str(MODELS_DIR / "classla")
    for package in sorted(set(PROCESSORS.values())):
        classla.download("sl", type=package, dir=folder, verbose=False)
    return classla.Pipeline("sl", dir=folder, processors=PROCESSORS, verbose=False)


def tagged_rows(tagger: Callable, texts: Iterable[str]) -> list[Row]:
    """Rows of the tokens CLASSLA finds in the paragraphs."""
    rows = []
    sentence = -1
    for para_id, text in enumerate(texts):
        if not text.strip():
            continue
        for tagged in tagger(text).sentences:
            sentence += 1
            for token in tagged.tokens:
                for word in token.words:
                    rows.append(
                        (
                            para_id,
                            sentence,
                            word.text,
                            word.lemma,
                            word.upos,
                            word.feats,
                            entity_of(token.ner),
                        )
                    )
    return rows


def entity_of(ner: str | None) -> str | None:
    """The entity type of a BIO label: B-PER -> PER, O -> nothing."""
    return None if ner in (None, "O") else ner.split("-", 1)[1]


def to_table(rows: list[Row]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=COLUMNS).astype(
        {"para_id": "int32", "sentence": "int32"}
    )


def write_table(table: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(path, index=False, compression="zstd", compression_level=19)
