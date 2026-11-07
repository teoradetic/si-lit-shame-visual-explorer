"""How much detected emotion each novel has, and where.

Both tables also count the low-score paragraphs (`low`), for "without".
"""

import numpy as np
import pandas as pd

N_POSITION_BINS = 20


# Detected paragraphs, and the low-score ones.
SETS = ("emotion", "low")


def build_novels(paragraphs: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    """One row per novel. Shares are normalized by novel length."""
    by_novel = paragraphs.groupby("novel_id", observed=True)
    novels = by_novel.agg(
        n_paragraphs=("para_id", "size"),
        n_chars=("n_chars", "sum"),
        mean_score=("score", "mean"),
        **{f"n_{s}": (s, "sum") for s in SETS},
    ).reset_index()
    novels = metadata.merge(novels, on="novel_id", validate="1:1")
    for s in SETS:
        novels[f"share_{s}"] = novels[f"n_{s}"] / novels["n_paragraphs"]
        novels[f"per_10k_words_{s}"] = novels[f"n_{s}"] / novels["word_count"] * 10_000
    return novels.drop(columns=["original_id", "doc_link"])


def build_position_bins(paragraphs: pd.DataFrame) -> pd.DataFrame:
    """Paragraph counts per novel and twentieth of the novel."""
    bins = np.minimum(
        (paragraphs["rel_position"] * N_POSITION_BINS).astype(int),
        N_POSITION_BINS - 1,
    )
    counts = (
        paragraphs.assign(position_bin=bins)
        .groupby(["novel_id", "position_bin"], observed=True)
        .agg(n_paragraphs=("para_id", "size"), **{f"n_{s}": (s, "sum") for s in SETS})
        .reset_index()
    )
    counts["position_bin"] = counts["position_bin"].astype("int8")
    return counts
