"""Readers for the precomputed tables in data/processed.

The app never runs NLP: everything here was built by the data CLI. Tables
are cached as shared resources, so callers must not modify them in place.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

import stats

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


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


def tagged(tier: str) -> pd.DataFrame:
    """The paragraphs of one tier, as columns."""
    df = paragraphs()
    return df[df[tier]].reset_index()


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
def word_counts(tier: str) -> pd.DataFrame:
    """Word counts per novel and side (emotion or comparison) of one tier."""
    df = table("word_counts")
    return df[df["tier"] == tier].drop(columns="tier")


@st.cache_resource
def word_prior() -> pd.DataFrame:
    """Corpus counts and flags of every word that can enter a list."""
    return table("word_prior").set_index("word")


@st.cache_data(max_entries=64)
def group_words(tier: str, novel_ids: frozenset[str]) -> pd.DataFrame:
    """Typical words of the detected passages of these novels, with flags."""
    counts = word_counts(tier)
    counts = counts[counts["novel_id"].isin(novel_ids)]
    authors = novels().set_index("novel_id")["author"]
    prior = word_prior()
    table_ = stats.word_table(counts, prior["n_corpus"], authors)
    if table_.empty:
        return table_
    return table_.join(prior[["function_word", "contains_stem"]], on="word")


@st.cache_data(max_entries=64)
def group_style(
    tier: str, split: str, novel_ids: frozenset[str], features: tuple[str, ...]
) -> pd.DataFrame:
    """Style of the detected passages of these novels against the comparison set."""
    df = table("style_novels")
    df = df[(df["tier"] == tier) & (df["split"] == split)]
    df = df[df["novel_id"].isin(novel_ids)]
    return stats.compare_novels(df.astype({"set": str}), list(features))
