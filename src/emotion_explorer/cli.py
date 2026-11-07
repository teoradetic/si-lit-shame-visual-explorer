"""Data CLI: rebuilds data/processed from data/raw and data/tokens.

uv run emotion-explorer all | paragraphs | ...
uv run emotion-explorer corpora                  # download the source corpora
uv run --group corpus emotion-explorer tokens [--novels SHAME_086]
"""

import argparse
from collections.abc import Callable

import pandas as pd

from emotion_explorer.analysis.arcs import (
    MIN_TAGGED,
    N_ARCS,
    N_PARTS,
    cluster,
    curves,
)
from emotion_explorer.analysis.overview import (
    N_POSITION_BINS,
    build_novels,
    build_position_bins,
)
from emotion_explorer.analysis.pairs import (
    MIN_NOVELS,
    MIN_PMI,
    MIN_SENTENCES,
    count_pairs,
    keep_strong,
    strong,
)
from emotion_explorer.analysis.slices import matched_sets
from emotion_explorer.analysis.style import (
    FEATURES,
    MATTR_WINDOW,
    REPEAT_WINDOW,
    paragraph_features,
    pool,
)
from emotion_explorer.analysis.text import split_speech, words
from emotion_explorer.analysis.themes import (
    MAX_SHARE,
    MIN_PARAGRAPHS,
    N_THEMES,
    THEME_POS,
    fit_themes,
)
from emotion_explorer.analysis.words import (
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
from emotion_explorer.emotion import SHAME
from emotion_explorer.meta import write_meta_section
from emotion_explorer.paths import (
    ARCS,
    COMPARISON,
    EXCERPTS,
    NAME_COUNTS,
    NOVELS,
    PARAGRAPHS,
    POSITION_BINS,
    PROCESSED_DIR,
    STYLE_NOVELS,
    STYLE_PARAGRAPHS,
    SUBJECTS,
    TEXTS,
    THEME_PARAGRAPHS,
    THEME_WORDS,
    THEMES,
    TOKENS_DIR,
    WORD_COUNTS,
    WORD_FORMS,
    WORD_PAIRS,
    WORD_PRIOR,
)
from emotion_explorer.prep.comparison import build_comparison, summarize_comparison
from emotion_explorer.prep.corpora import SOURCES, download_corpora, tei_path
from emotion_explorer.prep.excerpts import CONTEXT, build_excerpts, excerpt_texts
from emotion_explorer.prep.paragraphs import OVER_CONTEXT_CHARS, build_paragraphs
from emotion_explorer.prep.raw import load_annotations, load_metadata
from emotion_explorer.prep.tokens import (
    assign_paragraphs,
    load_tagger,
    read_tei,
    tagged_rows,
    to_table,
    write_table,
)

EMOTION = SHAME
SIDES = ("emotion", "comparison")


def write_parquet(df: pd.DataFrame, path) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, compression="zstd")
    print(f"wrote {path.name}: {len(df):,} rows, {path.stat().st_size / 1e6:.1f} MB")


def step_paragraphs() -> None:
    paragraphs = build_paragraphs(load_annotations(), load_metadata(), EMOTION)
    write_parquet(paragraphs, PARAGRAPHS)
    novels = paragraphs.drop_duplicates("novel_id")
    write_meta_section(
        "paragraphs",
        {
            "emotion": EMOTION.name,
            "stem": EMOTION.stem,
            "minimum": EMOTION.minimum,
            "low": EMOTION.low,
            "over_context_chars": OVER_CONTEXT_CHARS,
            "n_paragraphs": len(paragraphs),
            "n_novels": len(novels),
            "n_authors": int(novels["author"].nunique()),
            "year_range": [int(novels["year"].min()), int(novels["year"].max())],
            "novels_by_period": novels["period"].value_counts().to_dict(),
            "novels_by_gender": novels["gender"].value_counts().to_dict(),
            "n_emotion": int(paragraphs["emotion"].sum()),
            "low_count": int(paragraphs["low"].sum()),
            "over_context_count": int(paragraphs["over_context"].sum()),
        },
    )


def step_comparison() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = build_comparison(paragraphs)
    write_parquet(comparison, COMPARISON)
    write_meta_section("comparison", summarize_comparison(paragraphs, comparison))


def step_excerpts() -> None:
    paragraphs = pd.read_parquet(PARAGRAPHS)
    cols = ["novel_id", "para_id"]
    sets = {
        "emotion": paragraphs.loc[paragraphs["emotion"], cols],
        "comparison": pd.read_parquet(COMPARISON)[cols],
    }
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
    write_parquet(build_novels(paragraphs, load_metadata()), NOVELS)
    bins = build_position_bins(paragraphs)
    write_parquet(bins, POSITION_BINS)
    shapes = curves(bins)
    arcs = (
        shapes.stack()
        .rename("share")
        .reset_index()
        .merge(cluster(shapes).reset_index(), on="novel_id")
        .round({"share": 5})
    )
    write_parquet(arcs.astype({"part": "int8", "arc": "int8"}), ARCS)
    write_meta_section(
        "overview",
        {
            "n_position_bins": N_POSITION_BINS,
            "n_arcs": N_ARCS,
            "arc_parts": N_PARTS,
            "arc_min_tagged": MIN_TAGGED,
        },
    )


def add_text(paragraphs: pd.DataFrame, annotations: dict) -> pd.DataFrame:
    return paragraphs.assign(
        text=[
            annotations[n]["paragraphs"][str(p)]["text"]
            for n, p in zip(paragraphs["novel_id"], paragraphs["para_id"], strict=True)
        ]
    )


def read_sets() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """The words of each side, and per-lemma stats of the corpus."""
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = pd.read_parquet(COMPARISON)
    by_novel = {
        side: frame.groupby("novel_id")["para_id"]
        for side, frame in zip(SIDES, matched_sets(paragraphs, comparison), strict=True)
    }
    stats = []
    in_sets: dict[str, list[pd.DataFrame]] = {k: [] for k in by_novel}
    for novel_id in sorted(paragraphs["novel_id"].unique()):
        words = read_words(TOKENS_DIR / f"{novel_id}.parquet")
        stats.append(lemma_stats(words))
        for key, para_ids in by_novel.items():
            if novel_id in para_ids.groups:
                inside = words["para_id"].isin(para_ids.get_group(novel_id))
                in_sets[key].append(words[inside].assign(novel_id=novel_id))
    sets = {k: pd.concat(v, ignore_index=True) for k, v in in_sets.items()}
    return sets, lexicon(pd.concat(stats, ignore_index=True))


def step_words() -> None:
    sets, corpus = read_sets()
    names = set(corpus.index[corpus["name"]])
    both = pd.concat(sets.values(), ignore_index=True)
    frequency = both["word"].value_counts()
    keep = vocabulary(frequency, names)
    # Names counted on their own, for the People page. A name none of
    # whose forms is mostly its own is a tagging slip (*bola*).
    people = {w for w in names if frequency.get(w, 0) >= MIN_COUNT}
    forms = word_forms(both, keep | people)
    people &= set(forms["word"])
    counts = pd.concat(
        [count_words(frame, keep).assign(side=side) for side, frame in sets.items()],
        ignore_index=True,
    )
    categories = {c: "category" for c in ("novel_id", "word", "case", "side")}
    write_parquet(counts.astype({**categories, "n": "int32"}), WORD_COUNTS)
    name_counts = pd.concat(
        [
            count_words(frame, people)
            .groupby(["novel_id", "word"], observed=True)["n"]
            .sum()
            .reset_index()
            .assign(side=side)
            for side, frame in sets.items()
        ],
        ignore_index=True,
    )
    categories = {c: "category" for c in ("novel_id", "word", "side")}
    write_parquet(name_counts.astype({**categories, "n": "int32"}), NAME_COUNTS)
    subjects = pd.concat(
        [
            frame.groupby(["novel_id", "subject"], observed=True)
            .size()
            .rename("n")
            .reset_index()
            .assign(side=side)
            for side, frame in sets.items()
        ],
        ignore_index=True,
    )
    categories = {c: "category" for c in ("novel_id", "subject", "side")}
    write_parquet(subjects.astype({**categories, "n": "int32"}), SUBJECTS)
    vocab = corpus.loc[sorted(keep | people)]
    write_parquet(
        pd.DataFrame(
            {
                "word": vocab.index,
                "n_corpus": vocab["n_corpus"].to_numpy(),
                "pos": vocab["pos"].to_numpy(),
                "function_word": vocab["pos"].isin(FUNCTION_POS).to_numpy(),
                "contains_stem": [EMOTION.stem in w for w in vocab.index],
                "name": vocab["name"].to_numpy(),
            }
        ),
        WORD_PRIOR,
    )
    write_parquet(forms, WORD_FORMS)
    # Pairs in the passages with the emotion only: that is what the network
    # shows, and the comparison set would double the table.
    content = {w for w in keep if corpus.loc[w, "pos"] not in FUNCTION_POS}
    pairs = count_pairs(sets["emotion"], content)
    pairs = keep_strong(pairs, strong(pairs))
    categories = {c: "category" for c in ("novel_id", "a", "b")}
    write_parquet(pairs.astype({**categories, "n": "int32"}), WORD_PAIRS)
    write_meta_section(
        "words",
        {
            "function_pos": sorted(FUNCTION_POS),
            "name_share": NAME_SHARE,
            "n_names_removed": len(names),
            "min_count": MIN_COUNT,
            "vocabulary": len(keep),
            "n_names": len(people),
            "pair_min_sentences": MIN_SENTENCES,
            "pair_min_novels": MIN_NOVELS,
            "pair_min_pmi": MIN_PMI,
        },
    )


def step_themes() -> None:
    sets, _ = read_sets()
    prior = pd.read_parquet(WORD_PRIOR)
    # Without the emotion's own words, which would make a theme of themselves.
    usable = prior["pos"].isin(THEME_POS) & ~prior["contains_stem"] & ~prior["name"]
    vocabulary = set(prior.loc[usable, "word"])
    words = pd.concat(sets.values())
    themes, main = fit_themes(words[words["word"].isin(vocabulary)])
    write_parquet(themes.astype({"theme": "int8", "rank": "int8"}), THEMES)
    keys = ["novel_id", "para_id"]
    sides = pd.concat(
        [frame[keys].drop_duplicates().assign(set=s) for s, frame in sets.items()]
    )
    main = main.merge(sides, on=keys)
    write_parquet(
        main.astype({"novel_id": "category", "set": "category", "theme": "int8"}),
        THEME_PARAGRAPHS,
    )
    # The words of the passages with the emotion, per novel and main theme,
    # to set two themes side by side.
    emotion = sets["emotion"][[*keys, "word"]]
    theme_words = (
        emotion[emotion["word"].isin(vocabulary)]
        .merge(main.loc[main["set"] == "emotion", [*keys, "theme"]], on=keys)
        .groupby(["novel_id", "theme", "word"], observed=True)
        .size()
        .rename("n")
        .reset_index()
    )
    write_parquet(
        theme_words.astype(
            {"novel_id": "category", "theme": "int8", "word": "category", "n": "int32"}
        ),
        THEME_WORDS,
    )
    write_meta_section(
        "themes",
        {
            "n_themes": N_THEMES,
            "pos": list(THEME_POS),
            "min_paragraphs": MIN_PARAGRAPHS,
            "max_share": MAX_SHARE,
        },
    )


def step_style() -> None:
    annotations = load_annotations()
    paragraphs = pd.read_parquet(PARAGRAPHS)
    comparison = pd.read_parquet(COMPARISON)
    emotion, comp = matched_sets(paragraphs, comparison)
    sets = add_text(
        pd.concat(
            [emotion.assign(set="emotion"), comp.assign(set="comparison")],
            ignore_index=True,
        ),
        annotations,
    )
    keep = ["novel_id", "para_id", "set", "author", "period", "gender"]
    # One row per paragraph and split: all of it, its narration, its speech.
    parts = split_speech(sets["text"])
    frames = []
    for split, texts in parts.items():
        texts = texts[texts.str.len() > 0]
        features = pd.DataFrame.from_records(
            texts.map(paragraph_features).tolist(), index=texts.index
        )
        frames.append(
            sets.loc[texts.index, keep]
            .join(features)
            .assign(split=split, words=texts.map(words))
        )
    style = pd.concat(frames, ignore_index=True)
    categories = {"set": "category", "split": "category"}
    write_parquet(style.drop(columns="words").astype(categories), STYLE_PARAGRAPHS)

    per_novel = (
        style.groupby(["novel_id", "set", "split"], observed=True)
        .apply(pool, include_groups=False)
        .reset_index()
    )
    categories = {c: "category" for c in ("novel_id", "set", "split")}
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


def step_tokens(novel_ids: list[str] | None) -> None:
    """Write the missing token tables; existing ones are kept."""
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
        print(f"wrote {path.name}: {len(rows):,} tokens")


STEPS: dict[str, Callable[[], None]] = {
    "paragraphs": step_paragraphs,
    "comparison": step_comparison,
    "excerpts": step_excerpts,
    "overview": step_overview,
    "words": step_words,
    "themes": step_themes,
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
        download_corpora(load_metadata())
    elif args.step == "tokens":
        step_tokens(args.novels)
    else:
        for name in STEPS if args.step == "all" else [args.step]:
            print(f"== {name}")
            STEPS[name]()
