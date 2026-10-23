import pandas as pd

from emotion_explorer.emotion import SHAME
from emotion_explorer.excerpts import build_excerpts, excerpt_texts, merge_spans
from emotion_explorer.paragraphs import build_paragraphs


def test_merge_spans_clips_and_merges_overlaps():
    assert merge_spans([1], 10) == [(0, 3, [1])]
    assert merge_spans([8, 3], 10) == [(1, 5, [3]), (6, 9, [8])]
    # Spans 1-5 and 5-9 overlap at paragraph 5.
    assert merge_spans([3, 7], 10) == [(1, 9, [3, 7])]


def test_excerpts_and_their_texts(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    focus = paragraphs.loc[paragraphs["broad"], ["novel_id", "para_id"]]
    excerpts = build_excerpts(paragraphs, {"broad": focus})
    assert len(excerpts) == 1
    row = excerpts.iloc[0]
    assert (row.start, row.end, list(row.focus_ids)) == (0, 7, [2, 5])
    texts = excerpt_texts(annotations, excerpts)
    assert texts["para_id"].tolist() == list(range(8))
    assert texts.iloc[2]["text"] == "Sram ga je bilo."
    assert isinstance(texts, pd.DataFrame)
