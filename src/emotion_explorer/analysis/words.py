"""Lemma counts per novel and set; the app compares them (`stats.py`)."""

import unicodedata
from pathlib import Path

import pandas as pd

from emotion_explorer.analysis.text import speech_flags

# Parts of speech that carry little meaning on their own; the app hides them
# by default. Interjections (ah, oh) stay visible: they may express emotion.
FUNCTION_POS = frozenset({"ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "SCONJ"})
CONTENT_POS = frozenset({"ADJ", "ADV", "INTJ", "NOUN", "VERB"})
# A lemma is a name if more than this share of its tokens are proper nouns or
# inside a named entity (which also covers adjectives from names, *Janezov*).
NAME_SHARE = 0.5
# Some editions mark stress on vowels (takó, očí), which would split a lemma
# in two. The marks are dropped from lemmas; č, š, ž and ć are letters and stay.
ACCENTED = "áàâäéèêëíìîïóòôöúùûüŕȁȃȅȇȉȋȍȏȑȓȕȗ"
UNACCENT = str.maketrans({c: unicodedata.normalize("NFD", c)[0] for c in ACCENTED})
MIN_LENGTH = 2
MIN_COUNT = 10


def read_words(path: Path) -> pd.DataFrame:
    """para_id, sentence, lemma (`word`, lower-cased, unaccented), form, POS,
    case, `speech` (or narration), `name`, and `subject`: Fem or Masc for a
    singular past-tense verb (*je rekla*, *je rekel*), whose gender is that of
    its subject.

    Forms keep their accents: the app searches the text with them.
    """
    tokens = pd.read_parquet(
        path,
        columns=["para_id", "sentence", "form", "lemma", "upos", "feats", "entity"],
    )
    # Before the filter below: it drops the quotation marks.
    tokens["speech"] = speech_flags(tokens.set_index("para_id")["form"]).to_numpy()
    tokens = tokens[tokens["upos"].isin(FUNCTION_POS | CONTENT_POS | {"PROPN"})]
    word = tokens["lemma"].str.lower().str.translate(UNACCENT)
    # isalpha, not a regex: pandas runs regexes through RE2, whose \w is ASCII-only.
    keep = word.str.isalpha() & (word.str.len() >= MIN_LENGTH)
    return pd.DataFrame(
        {
            "para_id": tokens["para_id"],
            "sentence": tokens["sentence"],
            "word": word,
            "form": tokens["form"].str.lower(),
            "pos": tokens["upos"],
            "case": tokens["feats"].str.extract(r"Case=(\w+)", expand=False),
            "speech": tokens["speech"],
            "name": (tokens["upos"] == "PROPN") | tokens["entity"].notna(),
            "subject": tokens["feats"]
            .str.extract(r"Gender=(Fem|Masc)\|Number=Sing\|VerbForm=Part", expand=False)
            .where(tokens["upos"].isin(["VERB", "AUX"])),
        }
    )[keep]


def lemma_stats(words: pd.DataFrame) -> pd.DataFrame:
    """Tokens and name tokens per lemma and POS, to be summed over novels."""
    return (
        words.groupby(["word", "pos"], observed=True)
        .agg(n=("name", "size"), n_name=("name", "sum"))
        .reset_index()
    )


def lexicon(stats: pd.DataFrame) -> pd.DataFrame:
    """Per lemma in the corpus: count, commonest POS, and whether it is a name."""
    stats = stats.groupby(["word", "pos"], observed=True)[["n", "n_name"]].sum()
    stats = stats.reset_index()
    totals = stats.groupby("word")[["n", "n_name"]].sum()
    # Ties go to the alphabetically first POS, so rebuilds are identical.
    pos = (
        stats.sort_values(["n", "pos"], ascending=[False, True])
        .drop_duplicates("word")
        .set_index("word")["pos"]
    )
    return pd.DataFrame(
        {
            "n_corpus": totals["n"],
            "pos": pos.reindex(totals.index),
            "name": totals["n_name"] / totals["n"] > NAME_SHARE,
        }
    )


def vocabulary(counts: pd.Series, names: set[str]) -> set[str]:
    """Lemmas that can enter a list; `counts` come from the largest sets."""
    return {w for w, n in counts.items() if n >= MIN_COUNT and w not in names}


def count_words(words: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """Occurrences of each kept lemma per novel, case (null for none) and
    speech or narration."""
    kept = words[words["word"].isin(keep)]
    keys = ["novel_id", "word", "case", "speech"]
    return (
        kept.groupby(keys, observed=True, dropna=False).size().rename("n").reset_index()
    )


def word_forms(words: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """Each form with the lemma most of its occurrences have (*je*: *biti*)."""
    counts = words.groupby(["form", "word"], observed=True).size().rename("n")
    best = (
        counts.reset_index()
        .sort_values(["n", "word"], ascending=[False, True])
        .drop_duplicates("form")
    )
    best = best[best["word"].isin(keep)]
    return best[["word", "form"]].sort_values(["word", "form"]).reset_index(drop=True)
