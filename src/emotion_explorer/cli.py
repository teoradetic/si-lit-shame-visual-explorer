"""Data CLI: rebuilds every file in data/processed from data/raw.

uv run emotion-explorer all          # every step, in order
uv run emotion-explorer paragraphs   # one step
"""

import argparse
from collections.abc import Callable

import pandas as pd

from emotion_explorer.emotion import SHAME
from emotion_explorer.meta import write_meta_section
from emotion_explorer.paragraphs import OVER_CONTEXT_CHARS, build_paragraphs
from emotion_explorer.paths import PARAGRAPHS, PROCESSED_DIR
from emotion_explorer.raw import load_annotations, load_metadata

EMOTION = SHAME


def write_parquet(df: pd.DataFrame, path) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, compression="zstd")
    size_mb = path.stat().st_size / 1e6
    print(
        f"wrote {path.relative_to(PROCESSED_DIR.parent.parent)}: "
        f"{len(df):,} rows, {size_mb:.1f} MB"
    )


def step_paragraphs() -> None:
    paragraphs = build_paragraphs(load_annotations(), load_metadata(), EMOTION)
    write_parquet(paragraphs, PARAGRAPHS)
    novels = paragraphs.drop_duplicates("novel_id")
    write_meta_section(
        "paragraphs",
        {
            "emotion": EMOTION.name,
            "stem": EMOTION.stem,
            "tiers": EMOTION.tiers,
            "low": EMOTION.low,
            "over_context_chars": OVER_CONTEXT_CHARS,
            "n_paragraphs": len(paragraphs),
            "n_novels": len(novels),
            "n_authors": int(novels["author"].nunique()),
            "year_range": [int(novels["year"].min()), int(novels["year"].max())],
            "novels_by_period": novels["period"].value_counts().to_dict(),
            "novels_by_gender": novels["gender"].value_counts().to_dict(),
            "tier_counts": {t: int(paragraphs[t].sum()) for t in EMOTION.tiers},
            "low_count": int(paragraphs["low"].sum()),
            "over_context_count": int(paragraphs["over_context"].sum()),
        },
    )


STEPS: dict[str, Callable[[], None]] = {
    "paragraphs": step_paragraphs,
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="emotion-explorer", description=__doc__)
    parser.add_argument("step", choices=[*STEPS, "all"])
    args = parser.parse_args()
    steps = STEPS if args.step == "all" else {args.step: STEPS[args.step]}
    for name, step in steps.items():
        print(f"== {name}")
        step()
