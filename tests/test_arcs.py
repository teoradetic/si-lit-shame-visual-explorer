import pandas as pd

from emotion_explorer.analysis import arcs


def test_curves_keep_the_shape_of_novels_with_enough_passages():
    bins = pd.DataFrame(
        {
            "novel_id": ["N1"] * 20 + ["N2"] * 20,
            "position_bin": list(range(20)) * 2,
            "n_paragraphs": 10,
            # N1: all its 20 passages in the last tenth; N2: too few.
            "n_broad": [0] * 18 + [10, 10] + [1] + [0] * 19,
        }
    )
    shapes = arcs.curves(bins, "broad")
    assert shapes.index.tolist() == ["N1"]
    assert shapes.loc["N1"].tolist() == [0.0] * 9 + [1.0]


def test_cluster_numbers_arcs_from_early_to_late(monkeypatch):
    monkeypatch.setattr(arcs, "N_ARCS", 2)
    late, early = [0.0] * 9 + [1.0], [1.0] + [0.0] * 9
    shapes = pd.DataFrame([late, early, late], index=["A", "B", "C"])
    assert arcs.cluster(shapes).to_dict() == {"A": 2, "B": 1, "C": 2}
