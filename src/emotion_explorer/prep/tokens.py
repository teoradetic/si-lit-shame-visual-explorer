"""DATA-04: every token of a novel with its lemma and tags.

Novels from the annotated corpora keep the annotation they came with, which
CLASSLA produced. The others are tagged here with CLASSLA, so that all novels
go through the same kind of tool.

The annotated corpora divide the text into paragraphs differently from the
annotated corpus (the model's scores), but without whitespace the two hold the
same characters, so a word's position in that text gives its paragraph.
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
# CLASSLA's model for each step. The standard tagger reads predicative "sram
# ga je", the commonest way to say it, as an adjective or a verb, which gives
# the lemmas "sra" and "srati". The nonstandard one reads it as a noun, as the
# annotated corpora do, and the tokens stay the same as with the standard model.
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
    """Index of the paragraph each token starts in; len(texts) if past the end.

    The tokens may run past the paragraphs, as in one ELTeC novel with a few
    words more at its end. Any other difference is an error.
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
