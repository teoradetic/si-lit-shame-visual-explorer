import numpy as np

from emotion_explorer.comparison import build_comparison, near_tagged
from emotion_explorer.emotion import SHAME
from emotion_explorer.paragraphs import build_paragraphs


def test_near_tagged():
    ids = np.arange(10)
    assert near_tagged(ids, np.array([5]), 2).nonzero()[0].tolist() == [3, 4, 5, 6, 7]


def test_partners_are_low_far_and_similar_in_length(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    comparison = build_comparison(paragraphs, "broad")
    by_key = paragraphs.set_index(["novel_id", "para_id"])
    assert set(comparison["matched_para_id"]) <= {2, 5}
    for row in comparison.itertuples():
        partner = by_key.loc[(row.novel_id, row.para_id)]
        tagged = by_key.loc[(row.novel_id, row.matched_para_id)]
        assert partner["low"]
        # Paragraphs 0-7 are within two of a tagged one; 8 and 9 are free.
        assert row.para_id in (8, 9)
        assert 0.5 <= partner["n_chars"] / tagged["n_chars"] <= 2
