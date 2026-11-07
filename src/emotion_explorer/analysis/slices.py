"""The paragraph sets that the word and style counts are built for."""

import pandas as pd


def matched_sets(
    paragraphs: pd.DataFrame, comparison: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The detected paragraphs and the comparison paragraphs matched to them."""
    emotion = paragraphs[paragraphs["emotion"]]
    keys = emotion[["novel_id", "para_id"]].rename(
        columns={"para_id": "matched_para_id"}
    )
    partners = comparison.merge(keys, on=["novel_id", "matched_para_id"])
    comp = paragraphs.merge(
        partners[["novel_id", "para_id"]], on=["novel_id", "para_id"]
    )
    return emotion, comp
