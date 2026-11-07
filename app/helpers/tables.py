"""Cached readers for data/processed; callers must not modify the tables."""

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from helpers import stats

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"


@st.cache_resource
def meta() -> dict:
    return json.loads((PROCESSED_DIR / "meta.json").read_text(encoding="utf-8"))


@st.cache_resource
def table(name: str) -> pd.DataFrame:
    return pd.read_parquet(PROCESSED_DIR / f"{name}.parquet")


def novels() -> pd.DataFrame:
    return table("novels")


@st.cache_resource
def paragraphs() -> pd.DataFrame:
    """Every paragraph without text, indexed by (novel_id, para_id)."""
    return table("paragraphs").set_index(["novel_id", "para_id"]).sort_index()


@st.cache_resource
def texts() -> pd.Series:
    """Text by (novel_id, para_id), for every paragraph inside an excerpt."""
    return table("texts").set_index(["novel_id", "para_id"])["text"].sort_index()


@st.cache_resource
def excerpts(set_name: str) -> pd.DataFrame:
    """The excerpts of one set, with the novel's metadata."""
    df = table("excerpts")
    df = df[df["set"] == set_name]
    novel_cols = [
        "novel_id",
        "author",
        "title",
        "year",
        "period",
        "gender",
        "n_paragraphs",
    ]
    return df.merge(novels()[novel_cols], on="novel_id", validate="m:1")


def tagged() -> pd.DataFrame:
    """The detected paragraphs, as columns."""
    df = paragraphs()
    return df[df["emotion"]].reset_index()


def ranked_excerpts(set_name: str, ranked: pd.DataFrame) -> pd.DataFrame:
    """The excerpts whose focus paragraphs are in `ranked` (novel_id, para_id,
    value), with the best value of each as `rank`."""
    df = excerpts(set_name)
    exploded = df[["excerpt_id", "novel_id", "focus_ids"]].explode("focus_ids")
    exploded["para_id"] = exploded["focus_ids"].astype(int)
    hits = exploded.merge(ranked, on=["novel_id", "para_id"])
    best = hits.groupby("excerpt_id")["value"].max()
    return df[df["excerpt_id"].isin(best.index)].assign(
        rank=lambda d: d["excerpt_id"].map(best)
    )


def excerpts_with(
    word: str, set_name: str, novel_ids: frozenset[str]
) -> tuple[pd.DataFrame, list[str]]:
    """The excerpts of these novels whose focus paragraphs hold a form of the
    word, and its forms."""
    df = excerpts(set_name)
    df = df[df["novel_id"].isin(novel_ids)]
    forms = word_forms().get(word, [word])
    alternatives = "|".join(map(re.escape, sorted(forms, key=len, reverse=True)))
    has_word = focus_texts(set_name).str.contains(
        rf"(?<!\w)(?:{alternatives})(?!\w)", case=False, regex=True
    )
    return df[df["excerpt_id"].map(has_word).fillna(False).astype(bool)], forms


@st.cache_resource
def focus_texts(set_name: str) -> pd.Series:
    """The focus paragraphs of each excerpt joined, by excerpt_id, for search."""
    all_texts = texts()
    df = excerpts(set_name)
    joined = [
        "\n".join(all_texts.loc[(novel_id, pid)] for pid in focus_ids)
        for novel_id, focus_ids in zip(df["novel_id"], df["focus_ids"], strict=True)
    ]
    return pd.Series(joined, index=df["excerpt_id"])


@st.cache_resource
def word_cases(split: str) -> pd.DataFrame:
    """Word counts per novel, side and case (null for no case), in all text,
    narration or speech (`dialogue`)."""
    df = table("word_counts")
    if split != "all":
        df = df[df["speech"] == (split == "dialogue")]
    return df.drop(columns="speech")


@st.cache_resource
def word_counts(split: str) -> pd.DataFrame:
    """Word counts per novel and side (emotion or comparison)."""
    keys = ["novel_id", "word", "side"]
    cases = word_cases(split)
    return cases.groupby(keys, observed=True)["n"].sum().reset_index()


@st.cache_resource
def word_prior() -> pd.DataFrame:
    """Corpus counts and flags of every word that can enter a list."""
    return table("word_prior").set_index("word")


@st.cache_data(max_entries=64)
def group_words(split: str, novel_ids: frozenset[str]) -> pd.DataFrame:
    """Typical words of the detected passages of these novels, with flags."""
    counts = word_counts(split)
    counts = counts[counts["novel_id"].isin(novel_ids)]
    authors = novels().set_index("novel_id")["author"]
    prior = word_prior()
    table_ = stats.word_table(counts, prior["n_corpus"], authors)
    if table_.empty:
        return table_
    return table_.join(prior[["pos", "function_word"]], on="word")


@st.cache_data(max_entries=64)
def group_pairs(novel_ids: frozenset[str]) -> pd.DataFrame:
    """Words a, b in the same sentence of the detected passages of these novels:
    sentences together (n) and PMI. An empty `a` counts the sentences of `b`."""
    df = table("word_pairs")
    df = df[df["novel_id"].isin(novel_ids)]
    df = df.groupby(["a", "b"], observed=True)["n"].sum().reset_index()
    df = df.astype({"a": str, "b": str})
    sentences = df[df["a"] == ""].set_index("b")["n"]
    pairs = df[df["a"] != ""]
    return pairs.assign(
        pmi=stats.pmi(
            pairs["n"],
            pairs["a"].map(sentences),
            pairs["b"].map(sentences),
            sentences.get("", 0),
        )
    )


@st.cache_resource
def word_forms() -> pd.Series:
    """The lower-cased forms of each lemma that can enter a word list."""
    return table("word_forms").groupby("word", observed=True)["form"].agg(list)


@st.cache_data(max_entries=64)
def group_style(
    split: str, novel_ids: frozenset[str], features: tuple[str, ...]
) -> pd.DataFrame:
    """Style of the detected passages of these novels against the comparison set."""
    df = table("style_novels")
    df = df[df["split"] == split]
    df = df[df["novel_id"].isin(novel_ids)]
    return stats.compare_novels(df.astype({"set": str}), list(features))
