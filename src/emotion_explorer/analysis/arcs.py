"""Shapes of the emotion's course through a novel: each novel's curve is
matched to a few named shapes."""

import numpy as np
import pandas as pd

# The position bins are pooled into tenths: fewer, steadier points.
N_PARTS = 10
# A novel needs this many detected paragraphs for a usable curve.
MIN_TAGGED = 20
# The best shape must correlate at least this well, or the novel has none.
MIN_FIT = 0.5
_X = (np.arange(N_PARTS) + 0.5) / N_PARTS
SHAPES = {
    "rising": _X,
    "falling": 1 - _X,
    "peak": np.sin(np.pi * _X),
    "dip": -np.sin(np.pi * _X),
    "two_peaks": np.sin(2 * np.pi * _X) ** 2,
}
NO_SHAPE = "none"


def curves(bins: pd.DataFrame) -> pd.DataFrame:
    """Each novel's curve: the rate of detected paragraphs per tenth, scaled
    to sum to 1, so that only its shape counts; novels by tenth."""
    n_bins = bins["position_bin"].max() + 1
    part = bins["position_bin"].astype(int) * N_PARTS // n_bins
    sums = (
        bins.assign(part=part)
        .groupby(["novel_id", "part"], observed=True)[["n_emotion", "n_paragraphs"]]
        .sum()
    )
    rate = (sums["n_emotion"] / sums["n_paragraphs"]).unstack("part")
    tagged = sums["n_emotion"].groupby("novel_id", observed=True).sum()
    rate = rate[tagged.reindex(rate.index) >= MIN_TAGGED]
    return rate.div(rate.sum(axis=1), axis=0)


def _centred(rows: np.ndarray) -> np.ndarray:
    rows = rows - rows.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(rows, axis=1, keepdims=True)
    return np.divide(rows, norm, out=np.zeros_like(rows), where=norm > 0)


def classify(shapes: pd.DataFrame) -> pd.DataFrame:
    """Each novel's shape (`arc`) and its correlation with it (`fit`), on the
    curve averaged over three neighbouring tenths, which damps the noise."""
    padded = np.pad(shapes.to_numpy(), ((0, 0), (1, 1)), mode="edge")
    smooth = (padded[:, :-2] + padded[:, 1:-1] + padded[:, 2:]) / 3
    fits = _centred(smooth) @ _centred(np.array(list(SHAPES.values()))).T
    best = fits.argmax(axis=1)
    fit = fits.max(axis=1)
    arc = np.where(fit >= MIN_FIT, np.array(list(SHAPES))[best], NO_SHAPE)
    return pd.DataFrame({"arc": arc, "fit": fit.round(3)}, index=shapes.index)
