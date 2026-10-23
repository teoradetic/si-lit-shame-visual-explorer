"""DATA-01: one row per paragraph, without its text."""

import pandas as pd

from emotion_explorer.emotion import SCALE_MAX, SCALES, Emotion

# Paragraphs longer than this overflowed the LLM's 4,096-token context during
# scoring, so the model saw only their end. The rule reproduces the
# reproducibility record of the first project exactly: 20 paragraphs from
# 5 novels, 14 of them in the core tier (the 21st longest has 9,356 chars).
OVER_CONTEXT_CHARS = 9_400


def tier_mask(scores: pd.DataFrame, minimums: dict[str, float]) -> pd.Series:
    """True where every score range reaches its minimum."""
    mask = pd.Series(True, index=scores.index)
    for scale, minimum in minimums.items():
        mask &= scores[f"score_{scale}"] >= minimum
    return mask


def low_mask(scores: pd.DataFrame, maximums: dict[str, float]) -> pd.Series:
    """True where every score range stays at or below its maximum."""
    mask = pd.Series(True, index=scores.index)
    for scale, maximum in maximums.items():
        mask &= scores[f"score_{scale}"] <= maximum
    return mask


def build_paragraphs(
    annotations: dict, metadata: pd.DataFrame, emotion: Emotion
) -> pd.DataFrame:
    records = []
    for novel_id, novel in annotations.items():
        paragraphs = novel["paragraphs"]
        n = len(paragraphs)
        for key, par in paragraphs.items():
            para_id = int(key)
            records.append(
                {
                    "novel_id": novel_id,
                    "para_id": para_id,
                    "rel_position": (para_id + 0.5) / n,
                    "n_chars": len(par["text"]),
                    "has_stem": par[emotion.stem_key],
                    **{
                        f"score_{scale}": par[emotion.score_key.format(scale=scale)]
                        for scale in SCALES
                    },
                }
            )
    df = pd.DataFrame.from_records(records)
    # The scores are not intensity; this mean of the three ranges, each
    # rescaled to 0-1, is just a single number to sort and average by.
    df["score"] = sum(df[f"score_{s}"] / SCALE_MAX[s] for s in SCALES) / len(SCALES)
    for tier, minimums in emotion.tiers.items():
        df[tier] = tier_mask(df, minimums)
    df["low"] = low_mask(df, emotion.low)
    df["over_context"] = df["n_chars"] > OVER_CONTEXT_CHARS

    novel_cols = ["novel_id", "author", "title", "year", "period", "gender"]
    df = df.merge(metadata[novel_cols], on="novel_id", how="left", validate="m:1")
    if df["author"].isna().any():
        missing = sorted(df.loc[df["author"].isna(), "novel_id"].unique())
        raise ValueError(f"Novels missing from the metadata: {missing}")

    df = df.astype(
        {
            "para_id": "int32",
            "n_chars": "int32",
            "rel_position": "float32",
            "score": "float32",
            **{f"score_{s}": "float32" for s in SCALES},
            **{c: "category" for c in novel_cols if c != "year"},
        }
    )
    return df.sort_values(["novel_id", "para_id"], ignore_index=True)
