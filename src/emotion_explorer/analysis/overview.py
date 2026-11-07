"""How much detected emotion each novel has, and where.

Both tables also count the low-score paragraphs (`low`), for "without".
"""

import numpy as np
import pandas as pd

N_POSITION_BINS = 20


def build_novels(
    paragraphs: pd.DataFrame, metadata: pd.DataFrame, tiers: tuple[str, ...]
) -> pd.DataFrame:
    """One row per novel. Shares are normalized by novel length."""
    sets = (*tiers, "low")
    by_novel = paragraphs.groupby("novel_id", observed=True)
    novels = by_novel.agg(
        n_paragraphs=("para_id", "size"),
        n_chars=("n_chars", "sum"),
        mean_score=("score", "mean"),
        **{f"n_{s}": (s, "sum") for s in sets},
    ).reset_index()
    novels = metadata.merge(novels, on="novel_id", validate="1:1")
    for tier in sets:
        novels[f"share_{tier}"] = novels[f"n_{tier}"] / novels["n_paragraphs"]
        novels[f"per_10k_words_{tier}"] = (
            novels[f"n_{tier}"] / novels["word_count"] * 10_000
        )
    return novels.drop(columns=["original_id", "doc_link"])


def build_position_bins(
    paragraphs: pd.DataFrame, tiers: tuple[str, ...]
) -> pd.DataFrame:
    """Paragraph counts per novel and twentieth of the novel."""
    sets = (*tiers, "low")
    bins = np.minimum(
        (paragraphs["rel_position"] * N_POSITION_BINS).astype(int),
        N_POSITION_BINS - 1,
    )
    counts = (
        paragraphs.assign(position_bin=bins)
        .groupby(["novel_id", "position_bin"], observed=True)
        .agg(n_paragraphs=("para_id", "size"), **{f"n_{s}": (s, "sum") for s in sets})
        .reset_index()
    )
    counts["position_bin"] = counts["position_bin"].astype("int8")
    return counts
