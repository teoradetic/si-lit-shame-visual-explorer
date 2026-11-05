"""AN-15: typical shapes of the emotion's course through a novel."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

N_ARCS = 4
# The position bins are pooled into tenths: fewer, steadier points.
N_PARTS = 10
# A novel needs this many detected paragraphs for a usable curve.
MIN_TAGGED = 20


def curves(bins: pd.DataFrame, tier: str) -> pd.DataFrame:
    """Each novel's curve: the rate of detected paragraphs per tenth, scaled
    to sum to 1, so that only its shape counts; novels by tenth."""
    n_bins = bins["position_bin"].max() + 1
    part = bins["position_bin"].astype(int) * N_PARTS // n_bins
    sums = (
        bins.assign(part=part)
        .groupby(["novel_id", "part"], observed=True)[[f"n_{tier}", "n_paragraphs"]]
        .sum()
    )
    rate = (sums[f"n_{tier}"] / sums["n_paragraphs"]).unstack("part")
    tagged = sums[f"n_{tier}"].groupby("novel_id", observed=True).sum()
    rate = rate[tagged.reindex(rate.index) >= MIN_TAGGED]
    return rate.div(rate.sum(axis=1), axis=0)


def cluster(shapes: pd.DataFrame) -> pd.Series:
    """Arc of each novel (k-means), numbered 1.. from the earliest centre of
    mass of the arc's mean curve to the latest."""
    model = KMeans(N_ARCS, n_init=20, random_state=0).fit(shapes.to_numpy())
    centre = model.cluster_centers_ @ np.arange(N_PARTS)
    number = np.argsort(np.argsort(centre)) + 1
    return pd.Series(number[model.labels_], index=shapes.index, name="arc")
