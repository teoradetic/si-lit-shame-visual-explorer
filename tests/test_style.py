import numpy as np

from emotion_explorer.style import count_repeats, mattr, paragraph_features


def test_count_repeats_within_window():
    assert count_repeats(["sram", "ga", "je", "sram"]) == (1, 2)


def test_mattr():
    assert mattr(["a", "b"] * 60, window=4) == 0.5
    assert np.isnan(mattr(["a"], window=4))


def test_paragraph_features():
    f = paragraph_features("»Ne!« je rekel... Kaj?")
    assert f["n_exclamation"] == 1
    assert f["n_question"] == 1
    assert f["n_ellipsis"] == 1
    assert f["dialogue"]
