"""The statistics the app computes for any group of novels."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from stats import (
    compare_novels,
    holm,
    log_odds,
    moving_average,
    rank_correlation,
    reflected_density,
    spread_rule,
    word_table,
)


def test_log_odds_sign_follows_overuse():
    a = np.array([30.0, 100.0])
    b = np.array([1.0, 100.0])
    table = log_odds(a, b, a + b)
    assert table.loc[0, "z"] > 0
    assert table.loc[1, "z"] < 0
    # The plain ratio of frequencies, not the shrunk e^delta.
    assert table.loc[0, "ratio"] == pytest.approx((30.5 / 130) / (1.5 / 101))


def test_word_table_requires_spread():
    counts = pd.DataFrame(
        {
            "novel_id": ["N1", "N2"],
            "word": ["sram", "dan"],
            "side": ["emotion", "comparison"],
            "n": [20, 20],
        }
    )
    prior = pd.Series({"sram": 20, "dan": 20})
    authors = pd.Series({"N1": "X", "N2": "Y"})
    table = word_table(counts, prior, authors)
    assert set(table["word"]) == {"sram", "dan"}
    # With 30 novels, a word must recur in 3 of them.
    many = pd.Series({f"N{i}": f"A{i}" for i in range(30)})
    padding = pd.DataFrame(
        {"novel_id": many.index[2:], "word": "je", "side": "emotion", "n": 1}
    )
    table = word_table(pd.concat([counts, padding]), prior, many)
    assert "sram" not in set(table["word"])


def test_spread_rule():
    assert spread_rule(305, 88) == (5, 3)
    assert spread_rule(1, 1) == (1, 1)


def test_holm():
    p = pd.Series([0.01, 0.04, 0.03])
    assert holm(p).round(2).tolist() == [0.03, 0.06, 0.06]


def test_compare_novels_detects_a_shift():
    rows = [
        {
            "novel_id": f"N{i}",
            "set": s,
            "n_paragraphs": 10,
            "sentence_words": 12.0 if s == "emotion" else 10.0 + i % 2 * 0.1,
        }
        for i in range(20)
        for s in ("emotion", "comparison")
    ]
    table = compare_novels(pd.DataFrame(rows), ["sentence_words"])
    row = table.set_index("feature").loc["sentence_words"]
    assert 0.18 < row["rel_diff"] < 0.2
    assert row["p_value"] < 0.001


def test_rank_correlation():
    x = pd.Series(range(10))
    assert rank_correlation(x, x**2) == pytest.approx(1)
    assert np.isnan(rank_correlation(x[:3], x[:3]))


def test_moving_average_breaks_across_gaps():
    years = [1870, 1871, 1872, 1873, 1900, 1901, 1902, 1903]
    df = pd.DataFrame({"group": "a", "year": years, "value": [1.0] * 8})
    ma = moving_average(df, 1870, 1903, window=4, min_n=2)
    assert (ma["mean"] == 1).all()
    assert ma["segment"].nunique() == 2
    assert not ma["year"].between(1880, 1890).any()


def test_reflected_density_is_one_for_an_even_spread():
    grid = np.linspace(0, 100, 11)
    density = reflected_density(np.linspace(0, 100, 10_001), grid, 4.0)
    assert np.allclose(density, 1, atol=0.02)
