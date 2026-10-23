"""Label placement for the scatter plots."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from charts import place_labels


def boxes(placed, domain, width, height, font_size=12):
    low, span = np.log(domain[0]), np.log(domain[1]) - np.log(domain[0])
    out = []
    for row in placed[placed["labelled"]].itertuples():
        x = width * (np.log(row.label_a) - low) / span
        y = height * (1 - (np.log(row.label_b) - low) / span)
        w = 0.58 * font_size * len(row.word)
        x0 = {"left": x, "right": x - w}.get(row.align, x - w / 2)
        out.append((x0, y - 7, x0 + w, y + 7))
    return out


def test_labels_do_not_overlap():
    rng = np.random.default_rng(1)
    df = pd.DataFrame(
        {
            "word": [f"beseda{i}" for i in range(40)],
            "a": np.exp(rng.uniform(0, 2, 40)),
            "b": np.exp(rng.uniform(0, 2, 40)),
        }
    )
    domain = (0.9, 8.0)
    placed = place_labels(df, domain, 720, 520)
    found = boxes(placed, domain, 720, 520)
    assert len(found) > 20
    for i, p in enumerate(found):
        for q in found[i + 1 :]:
            assert not (p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3])


def test_a_lone_point_is_labelled_beside_its_dot():
    df = pd.DataFrame({"word": ["sram"], "a": [2.0], "b": [2.0]})
    placed = place_labels(df, (1.0, 4.0), 400, 400)
    assert placed["labelled"].all()
    assert placed["align"].iloc[0] == "left"
    assert not placed["leader"].iloc[0]
