import pandas as pd

from emotion_explorer.analysis import arcs


def test_curves_keep_the_shape_of_novels_with_enough_passages():
    bins = pd.DataFrame(
        {
            "novel_id": ["N1"] * 20 + ["N2"] * 20,
            "position_bin": list(range(20)) * 2,
            "n_paragraphs": 10,
            # N1: all its 20 passages in the last tenth; N2: too few.
            "n_emotion": [0] * 18 + [10, 10] + [1] + [0] * 19,
        }
    )
    shapes = arcs.curves(bins)
    assert shapes.index.tolist() == ["N1"]
    assert shapes.loc["N1"].tolist() == [0.0] * 9 + [1.0]


def test_classify_matches_named_shapes():
    rising = list(arcs._X)
    shapes = pd.DataFrame([rising, rising[::-1], [0.1] * 10], index=["A", "B", "C"])
    result = arcs.classify(shapes)
    assert result["arc"].to_dict() == {"A": "rising", "B": "falling", "C": "none"}
    assert result.loc["A", "fit"] > 0.95
