from emotion_explorer.analysis.overview import build_novels, build_position_bins
from emotion_explorer.emotion import SHAME
from emotion_explorer.prep.paragraphs import build_paragraphs


def test_novel_shares(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    novels = build_novels(paragraphs, metadata).set_index("novel_id")
    assert novels.loc["N1", "n_emotion"] == 2
    assert novels.loc["N1", "share_emotion"] == 0.2
    assert novels.loc["N2", "share_emotion"] == 0
    assert novels.loc["N1", "n_low"] == 8


def test_position_bins_sum_to_novel(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    bins = build_position_bins(paragraphs)
    assert bins["n_paragraphs"].sum() == len(paragraphs)
    assert bins["n_emotion"].sum() == 2
    assert bins["n_low"].sum() == paragraphs["low"].sum()
    assert bins["position_bin"].between(0, 19).all()
