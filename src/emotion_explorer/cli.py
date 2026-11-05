"""Data CLI: rebuilds every file in data/processed from data/raw.

uv run emotion-explorer all          # every step, in order
uv run emotion-explorer paragraphs   # one step

Lemmas and tags are not part of `all`: they need the optional `corpus` group.

uv run emotion-explorer corpora                   # download the source corpora
uv run --group corpus emotion-explorer tokens     # data/tokens, one file per novel
uv run --group corpus emotion-explorer tokens --novels SHAME_086   # only these
"""

import argparse
from collections.abc import Callable

import pandas as pd

from emotion_explorer.comparison import build_comparison, summarize_comparison
from emotion_explorer.corpora import SOURCES, download_corpora, tei_path
from emotion_explorer.emotion import SHAME
from emotion_explorer.excerpts import CONTEXT, build_excerpts, excerpt_texts
from emotion_explorer.meta import write_meta_section
from emotion_explorer.overview import (
    N_POSITION_BINS,
    build_novels,
    build_position_bins,
)
from emotion_explorer.paragraphs import OVER_CONTEXT_CHARS, build_paragraphs
from emotion_explorer.paths import (
    COMPARISON,
    EXCERPTS,
    NOVELS,
    PARAGRAPHS,
    POSITION_BINS,
    PROCESSED_DIR,
    STYLE_NOVELS,
    STYLE_PARAGRAPHS,
    TEXTS,
    TOKENS_DIR,
    WORD_COUNTS,
    WORD_FORMS,
    WORD_PRIOR,
)
from emotion_explorer.raw import load_annotations, load_metadata
from emotion_explorer.slices import tier_sets
from emotion_explorer.style import (
    FEATURES,
    MATTR_WINDOW,
    REPEAT_WINDOW,
    paragraph_features,
    pool,
)
from emotion_explorer.text import words
from emotion_explorer.tokens import (
    assign_paragraphs,
    load_tagger,
    read_tei,
    tagged_rows,
    to_table,
    write_table,
)
from emotion_explorer.words import (
    CONTENT_POS,
    FUNCTION_POS,
    MIN_COUNT,
    NAME_SHARE,
    count_words,
    lemma_stats,
    lexicon,
    read_words,
    vocabulary,
    word_forms,
)

EMOTION = SHAME
# The tier the comparison set is matched to, and the app's default tier.
MATCHED_TIER = "broad"


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


def step_comparison() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = build_comparison(paragraphs, MATCHED_TIER)
    write_parquet(comparison, COMPARISON)
    write_meta_section(
        "comparison", summarize_comparison(paragraphs, comparison, MATCHED_TIER)
    )


def step_excerpts() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    cols = ["novel_id", "para_id"]
    sets = {tier: paragraphs.loc[paragraphs[tier], cols] for tier in EMOTION.tiers}
    sets["comparison"] = pd.read_parquet(COMPARISON)[cols]
    excerpts = build_excerpts(paragraphs, sets)
    write_parquet(excerpts, EXCERPTS)
    texts = excerpt_texts(load_annotations(), excerpts)
    write_parquet(texts, TEXTS)
    by_set = excerpts.groupby("set", observed=True)
    write_meta_section(
        "excerpts",
        {
            "context": CONTEXT,
            "n_excerpts": by_set.size().to_dict(),
            "n_chars": by_set["n_chars"].sum().astype(int).to_dict(),
            "n_text_paragraphs": len(texts),
        },
    )


def step_overview() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    tiers = tuple(EMOTION.tiers)
    write_parquet(build_novels(paragraphs, load_metadata(), tiers), NOVELS)
    write_parquet(build_position_bins(paragraphs, tiers), POSITION_BINS)
    write_meta_section("overview", {"n_position_bins": N_POSITION_BINS})


def add_text(paragraphs: pd.DataFrame, annotations: dict) -> pd.DataFrame:
    return paragraphs.assign(
        text=[
            annotations[n]["paragraphs"][str(p)]["text"]
            for n, p in zip(paragraphs["novel_id"], paragraphs["para_id"], strict=True)
        ]
    )


def analysis_sets(annotations: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The matched tier and the comparison set, with their texts."""
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = pd.read_parquet(COMPARISON)
    emotion, comp = tier_sets(paragraphs, comparison, MATCHED_TIER)
    return add_text(emotion, annotations), add_text(comp, annotations)


def step_words() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = pd.read_parquet(COMPARISON)
    keys = ["novel_id", "para_id"]
    sets = {
        (tier, side): frame[keys]
        for tier in EMOTION.tiers
        for side, frame in zip(
            ["emotion", "comparison"],
            tier_sets(paragraphs, comparison, tier),
            strict=True,
        )
    }
    by_novel = {
        key: frame.groupby("novel_id")["para_id"] for key, frame in sets.items()
    }
    stats = []
    in_sets: dict[tuple[str, str], list[pd.DataFrame]] = {key: [] for key in sets}
    for novel_id in sorted(paragraphs["novel_id"].unique()):
        words = read_words(TOKENS_DIR / f"{novel_id}.parquet")
        stats.append(lemma_stats(words))
        for key, para_ids in by_novel.items():
            if novel_id in para_ids.groups:
                inside = words["para_id"].isin(para_ids.get_group(novel_id))
                in_sets[key].append(words[inside].assign(novel_id=novel_id))
    corpus = lexicon(pd.concat(stats, ignore_index=True))
    names = set(corpus.index[corpus["name"]])
    # The matched tier holds every other tier, so its two sides are the largest.
    largest = pd.concat(
        [
            pd.concat(in_sets[(MATCHED_TIER, side)])
            for side in ("emotion", "comparison")
        ],
        ignore_index=True,
    )
    keep = vocabulary(largest["word"].value_counts(), names)
    tables = [
        count_words(pd.concat(frames, ignore_index=True), keep).assign(
            tier=tier, side=side
        )
        for (tier, side), frames in in_sets.items()
    ]
    counts = pd.concat(tables, ignore_index=True)
    categories = {c: "category" for c in ("novel_id", "word", "tier", "side")}
    write_parquet(counts.astype({**categories, "n": "int32"}), WORD_COUNTS)
    vocab = corpus.loc[sorted(keep)]
    write_parquet(
        pd.DataFrame(
            {
                "word": vocab.index,
                "n_corpus": vocab["n_corpus"].to_numpy(),
                "pos": vocab["pos"].to_numpy(),
                "function_word": vocab["pos"].isin(FUNCTION_POS).to_numpy(),
                "contains_stem": [EMOTION.stem in w for w in vocab.index],
            }
        ),
        WORD_PRIOR,
    )
    write_parquet(word_forms(largest, keep), WORD_FORMS)
    write_meta_section(
        "words",
        {
            "method": "weighted log-odds, informative Dirichlet prior (Monroe 2008)",
            "unit": "lower-cased lemma (data/tokens)",
            "prior": "lemma counts of the whole corpus",
            "function_pos": sorted(FUNCTION_POS),
            "content_pos": sorted(CONTENT_POS),
            "name_share": NAME_SHARE,
            "n_names_removed": len(names),
            "min_count": MIN_COUNT,
            "vocabulary": len(keep),
        },
    )


def step_style() -> None:
    annotations = load_annotations()
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = pd.read_parquet(COMPARISON)
    emotion, comp = tier_sets(paragraphs, comparison, MATCHED_TIER)
    sets = pd.concat(
        [emotion.assign(set="emotion"), comp.assign(set="comparison")],
        ignore_index=True,
    )
    sets = add_text(sets, annotations)
    features = pd.DataFrame.from_records(sets["text"].map(paragraph_features).tolist())
    keep = ["novel_id", "para_id", "set", "author", "period", "gender", *EMOTION.tiers]
    style = pd.concat([sets[keep], features.drop(columns="n_chars")], axis=1)
    style["n_chars"] = sets["n_chars"]
    write_parquet(style.astype({"set": "category"}), STYLE_PARAGRAPHS)

    style["words"] = sets["text"].map(words)
    splits = {
        "all": style,
        "narration": style[~style["dialogue"]],
        "dialogue": style[style["dialogue"]],
    }
    tables = []
    for tier in EMOTION.tiers:
        # Comparison paragraphs belong to a tier through their partner.
        tier_keys = tier_sets(paragraphs, comparison, tier)
        in_tier = pd.concat(
            [
                k[["novel_id", "para_id"]].assign(set=s)
                for k, s in zip(tier_keys, ["emotion", "comparison"], strict=True)
            ]
        )
        for split, frame in splits.items():
            frame = frame.merge(in_tier, on=["novel_id", "para_id", "set"])
            per_novel = frame.groupby(["novel_id", "set"], observed=True).apply(
                pool, include_groups=False
            )
            tables.append(per_novel.reset_index().assign(tier=tier, split=split))
    per_novel = pd.concat(tables, ignore_index=True)
    categories = {c: "category" for c in ("novel_id", "set", "tier", "split")}
    write_parquet(
        per_novel.astype({**categories, "n_paragraphs": "int32"}), STYLE_NOVELS
    )
    write_meta_section(
        "style",
        {
            "features": list(FEATURES),
            "mattr_window": MATTR_WINDOW,
            "repeat_window": REPEAT_WINDOW,
        },
    )


def step_corpora() -> None:
    download_corpora(load_metadata())


def step_tokens(novel_ids: list[str] | None = None) -> None:
    """Write the missing token tables; the existing ones are kept as a cache."""
    annotations = load_annotations()
    novels = load_metadata()
    if novel_ids:
        novels = novels[novels["novel_id"].isin(novel_ids)]
    tagger = None
    for novel in novels.itertuples():
        path = TOKENS_DIR / f"{novel.novel_id}.parquet"
        if path.exists():
            continue
        texts = [p["text"] for p in annotations[novel.novel_id]["paragraphs"].values()]
        if novel.source_corpus in SOURCES:
            rows = read_tei(tei_path(novel.source_corpus, novel.original_id))
            rows = assign_paragraphs(rows, texts)
        else:
            tagger = tagger or load_tagger()
            rows = tagged_rows(tagger, texts)
        write_table(to_table(rows), path)
        size_kb = path.stat().st_size / 1e3
        print(f"wrote {path.name}: {len(rows):,} tokens, {size_kb:.0f} kB")


STEPS: dict[str, Callable[[], None]] = {
    "paragraphs": step_paragraphs,
    "comparison": step_comparison,
    "excerpts": step_excerpts,
    "overview": step_overview,
    "words": step_words,
    "style": step_style,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="emotion-explorer",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("step", choices=[*STEPS, "all", "corpora", "tokens"])
    parser.add_argument("--novels", nargs="+", help="tokens: only these novels")
    args = parser.parse_args()
    if args.step == "corpora":
        step_corpora()
        return
    if args.step == "tokens":
        step_tokens(args.novels)
        return
    steps = STEPS if args.step == "all" else {args.step: STEPS[args.step]}
    for name, step in steps.items():
        print(f"== {name}")
        step()
