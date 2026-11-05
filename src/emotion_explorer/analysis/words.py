"""AN-03: lemma counts behind the lists of typical words.

The pipeline counts each lemma per novel in the detected set and in its
comparison set; the app compares any group of novels with a weighted
log-odds ratio (`app/helpers/stats.py`), with the whole corpus as the prior. Lemmas,
parts of speech and names come from the token tables (DATA-04).
"""

import unicodedata
from pathlib import Path

import pandas as pd

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
    """The words of one novel: para_id, lemma as `word`, form, POS, and `name`.

    Lemmas are lower-cased, because the sources differ in capitals, and lose
    stress marks. Forms keep them, since the app searches the text with them.
    Punctuation, symbols, foreign words and lemmas with digits are left out.
    """
    tokens = pd.read_parquet(
        path, columns=["para_id", "form", "lemma", "upos", "entity"]
    )
    tokens = tokens[tokens["upos"].isin(FUNCTION_POS | CONTENT_POS | {"PROPN"})]
    word = tokens["lemma"].str.lower().str.translate(UNACCENT)
    # isalpha, not a regex: pandas runs regexes through RE2, whose \w is ASCII-only.
    keep = word.str.isalpha() & (word.str.len() >= MIN_LENGTH)
    return pd.DataFrame(
        {
            "para_id": tokens["para_id"],
            "word": word,
            "form": tokens["form"].str.lower(),
            "pos": tokens["upos"],
            "name": (tokens["upos"] == "PROPN") | tokens["entity"].notna(),
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
    """Lemmas that can enter a word list.

    `counts` are the lemmas of the compared sets at their largest (the broad
    tier and its partners). Any slice of them counts a lemma at most as often,
    so a lemma below MIN_COUNT here can never pass it in a slice.
    """
    return {w for w, n in counts.items() if n >= MIN_COUNT and w not in names}


def count_words(words: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """Occurrences of each kept lemma per novel; `words` has novel_id and word."""
    kept = words[words["word"].isin(keep)]
    return (
        kept.groupby(["novel_id", "word"], observed=True)
        .size()
        .rename("n")
        .reset_index()
    )


def word_forms(words: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """The forms by which the app finds a lemma's passages.

    Each form goes to the lemma most of its occurrences have, so that no form
    finds the passages of two lemmas (*je*: *biti*, not *on*).
    """
    counts = words.groupby(["form", "word"], observed=True).size().rename("n")
    best = (
        counts.reset_index()
        .sort_values(["n", "word"], ascending=[False, True])
        .drop_duplicates("form")
    )
    best = best[best["word"].isin(keep)]
    return best[["word", "form"]].sort_values(["word", "form"]).reset_index(drop=True)
