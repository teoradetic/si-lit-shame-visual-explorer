from emotion_explorer.emotion import SHAME, TIERS
from emotion_explorer.overview import build_novels, build_position_bins
from emotion_explorer.paragraphs import build_paragraphs


def test_novel_shares(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    novels = build_novels(paragraphs, metadata, TIERS).set_index("novel_id")
    assert novels.loc["N1", "n_broad"] == 2
    assert novels.loc["N1", "share_broad"] == 0.2
    assert novels.loc["N2", "share_core"] == 0
    assert novels.loc["N1", "n_low"] == 8


def test_position_bins_sum_to_novel(annotations, metadata):
    paragraphs = build_paragraphs(annotations, metadata, SHAME)
    bins = build_position_bins(paragraphs, TIERS)
    assert bins["n_paragraphs"].sum() == len(paragraphs)
    assert bins["n_broad"].sum() == 2
    assert bins["n_low"].sum() == paragraphs["low"].sum()
    assert bins["position_bin"].between(0, 19).all()
