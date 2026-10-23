"""The paragraph sets that the word and style counts are built for."""

import pandas as pd


def tier_sets(
    paragraphs: pd.DataFrame, comparison: pd.DataFrame, tier: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The tier's paragraphs and the comparison paragraphs matched to them."""
    emotion = paragraphs[paragraphs[tier]]
    keys = emotion[["novel_id", "para_id"]].rename(
        columns={"para_id": "matched_para_id"}
    )
    partners = comparison.merge(keys, on=["novel_id", "matched_para_id"])
    comp = paragraphs.merge(
        partners[["novel_id", "para_id"]], on=["novel_id", "para_id"]
    )
    return emotion, comp
