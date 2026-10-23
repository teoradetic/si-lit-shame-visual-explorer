from emotion_explorer.emotion import SHAME
from emotion_explorer.paragraphs import build_paragraphs


def test_one_row_per_paragraph_in_order(annotations, metadata):
    df = build_paragraphs(annotations, metadata, SHAME)
    assert len(df) == 14
    assert df.loc[df.novel_id == "N1", "para_id"].tolist() == list(range(10))


def test_tiers_are_nested(annotations, metadata):
    df = build_paragraphs(annotations, metadata, SHAME).set_index(
        ["novel_id", "para_id"]
    )
    assert df.loc[("N1", 2), ["core", "broad"]].tolist() == [True, True]
    assert df.loc[("N1", 5), ["core", "broad"]].tolist() == [False, True]
    assert not (df["core"] & ~df["broad"]).any()
    assert df["broad"].sum() == 2


def test_low_excludes_tagged(annotations, metadata):
    df = build_paragraphs(annotations, metadata, SHAME)
    assert not (df["low"] & df["broad"]).any()
    assert df["low"].sum() == 12


def test_position_and_metadata(annotations, metadata):
    df = build_paragraphs(annotations, metadata, SHAME)
    first = df.iloc[0]
    assert first["rel_position"] == 0.05
    assert first["period"] == "Realism"
    assert df["has_stem"].sum() == 1
