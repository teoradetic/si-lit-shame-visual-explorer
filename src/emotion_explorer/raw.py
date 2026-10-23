"""Readers for the two raw entry points."""

import json
from pathlib import Path

import pandas as pd
import zstandard

from emotion_explorer.paths import ANNOTATIONS_JSON_ZST, CORPUS_METADATA_CSV


def load_annotations(path: Path = ANNOTATIONS_JSON_ZST) -> dict:
    """The annotated corpus: novel id -> {author, title, paragraphs}.

    Paragraph ids are string keys ("0", "1", ...) in reading order.
    """
    with path.open("rb") as f:
        return json.loads(zstandard.ZstdDecompressor().stream_reader(f).read())


def load_metadata(path: Path = CORPUS_METADATA_CSV) -> pd.DataFrame:
    """One row per novel, with generic column names."""
    meta = pd.read_csv(path)
    return pd.DataFrame(
        {
            "novel_id": meta["shame_id"],
            "author": meta["author"],
            "title": meta["title"],
            "year": meta["publ_year"].astype("int16"),
            "period": meta["time_period"],
            "gender": meta["author_gender"],
            "word_count": meta["word_count"].astype("int32"),
            "source_corpus": meta["source_corpus"],
            "doc_link": meta["doc_link"],
        }
    )
