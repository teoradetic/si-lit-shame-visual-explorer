"""AN-06: lemmas that come together in a sentence, per novel and set."""

import numpy as np
import pandas as pd

# A pair is kept when it comes together in at least this many sentences of at
# least this many novels, and at least 2^MIN_PMI times as often as chance.
MIN_SENTENCES = 10
MIN_NOVELS = 5
MIN_PMI = 1
# Stands for any sentence: the pair (ANY, w) counts the sentences with w, and
# (ANY, ANY) all sentences, which is what PMI needs besides the pairs.
ANY = ""


def count_pairs(words: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """Sentences per novel in which lemmas a < b come together."""
    keys = ["novel_id", "para_id", "sentence"]
    kept = words.loc[words["word"].isin(keep), [*keys, "word"]].astype({"word": str})
    unique = pd.concat(
        [kept.drop_duplicates(), words[keys].drop_duplicates().assign(word=ANY)]
    )
    pairs = unique.merge(unique, on=keys, suffixes=("_a", "_b"))
    a, b = pairs["word_a"], pairs["word_b"]
    pairs = pairs[(a < b) | ((a == ANY) & (b == ANY))]
    return (
        pairs.groupby(["novel_id", "word_a", "word_b"])
        .size()
        .rename("n")
        .reset_index()
        .rename(columns={"word_a": "a", "word_b": "b"})
    )


def pmi(n_ab, n_a, n_b, n):
    """Pointwise mutual information, log2: 1 is twice as often as chance."""
    return np.log2(n_ab * n / (n_a * n_b))


def strong(pairs: pd.DataFrame) -> pd.MultiIndex:
    """The (a, b) that pass the floor."""
    sentences = pairs[pairs["a"] == ANY].groupby("b")["n"].sum()
    totals = (
        pairs[pairs["a"] != ANY]
        .groupby(["a", "b"])
        .agg(n=("n", "sum"), novels=("novel_id", "nunique"))
        .reset_index()
    )
    score = pmi(
        totals["n"],
        totals["a"].map(sentences),
        totals["b"].map(sentences),
        sentences[ANY],
    )
    keep = (
        (totals["n"] >= MIN_SENTENCES)
        & (totals["novels"] >= MIN_NOVELS)
        & (score >= MIN_PMI)
    )
    return pd.MultiIndex.from_frame(totals.loc[keep, ["a", "b"]])


def keep_strong(pairs: pd.DataFrame, kept: pd.MultiIndex) -> pd.DataFrame:
    """The kept pairs, with the sentence counts of their words."""
    in_pairs = set(kept.get_level_values(0)) | set(kept.get_level_values(1)) | {ANY}
    is_kept = pd.MultiIndex.from_frame(pairs[["a", "b"]]).isin(kept)
    return pairs[is_kept | ((pairs["a"] == ANY) & pairs["b"].isin(in_pairs))]
