"""Statistics the views compute for whichever novels are being compared.

The data pipeline only counts: words per novel and set, style features
pooled per novel and set. Comparing a group is done here, so that every
filter and every comparison in the sidebar applies to it.
"""

import math

import numpy as np
import pandas as pd

# Words: prior strength relative to the size of the two compared sets.
PRIOR_WEIGHT = 1.0
SIDES = ["emotion", "comparison"]
MIN_COUNT = 10
# Style: novels need this many paragraphs in each set to be compared, and a
# group needs this many such novels.
MIN_PARAGRAPHS = 5
MIN_NOVELS = 3
N_PERMUTATIONS = 10_000
N_BOOTSTRAP = 2_000
SEED = 20261030


def spread_rule(n_novels: int, n_authors: int) -> tuple[int, int]:
    """In how many novels, by how many authors, a typical word must recur.

    5 novels by 3 authors for large groups, relaxed for small ones, so that
    one novel's vocabulary cannot top the list of a group of many.
    """
    return (
        int(np.clip(math.ceil(n_novels / 10), 1, 5)),
        int(np.clip(math.ceil(n_authors / 5), 1, 3)),
    )


def log_odds(ya: np.ndarray, yb: np.ndarray, prior: np.ndarray) -> pd.DataFrame:
    """Weighted log-odds of each word, A against B (Monroe et al. 2008).

    Informative Dirichlet prior from `prior` counts, scaled to the size of
    the two sets; `z` is the log-odds over its standard error.
    """
    na, nb = ya.sum(), yb.sum()
    a0 = PRIOR_WEIGHT * (na + nb)
    alpha = prior / prior.sum() * a0
    delta = np.log((ya + alpha) / (na + a0 - ya - alpha)) - np.log(
        (yb + alpha) / (nb + a0 - yb - alpha)
    )
    variance = 1 / (ya + alpha) + 1 / (yb + alpha)
    return pd.DataFrame(
        {
            "z": delta / np.sqrt(variance),
            "log_odds": delta,
            "n_emotion": ya.astype(int),
            "n_comparison": yb.astype(int),
            "per_10k_emotion": ya / na * 10_000,
            "per_10k_comparison": yb / nb * 10_000,
            # How many times more frequent in A: the plain ratio of the two
            # frequencies, with half a count added to each side so that a word
            # absent from one side stays finite. e^delta is not this ratio:
            # the prior pulls it towards 1, the more so the rarer the word.
            "ratio": ((ya + 0.5) / na) / ((yb + 0.5) / nb),
        }
    )


def word_table(
    counts: pd.DataFrame, prior: pd.Series, authors: pd.Series
) -> pd.DataFrame:
    """Typical words of one group's detected passages against its comparison set.

    `counts` has one row per novel, word and side (emotion or comparison)
    for the group's novels; `prior` is the corpus count by word and
    `authors` the author by novel. A word typical of either side must recur
    on that side (`spread_rule`).
    """
    if counts.empty:
        return pd.DataFrame()
    counts = counts.assign(author=counts["novel_id"].map(authors))
    by_side = (
        counts.groupby(["word", "side"], observed=True)
        .agg(
            n=("n", "sum"),
            n_novels=("novel_id", "nunique"),
            n_authors=("author", "nunique"),
        )
        .unstack("side", fill_value=0)
        .reindex(columns=SIDES, level="side", fill_value=0)
    )
    by_side = by_side[by_side["n"].sum(axis=1) >= MIN_COUNT]
    if by_side.empty:
        return pd.DataFrame()
    table = log_odds(
        by_side[("n", "emotion")].to_numpy(float),
        by_side[("n", "comparison")].to_numpy(float),
        prior.reindex(by_side.index).to_numpy(float),
    ).assign(
        word=by_side.index.astype(str),
        n_novels=by_side[("n_novels", "emotion")].to_numpy(),
        n_novels_comparison=by_side[("n_novels", "comparison")].to_numpy(),
    )
    min_novels, min_authors = spread_rule(
        counts["novel_id"].nunique(), counts["author"].nunique()
    )
    recurs = (by_side["n_novels"] >= min_novels) & (by_side["n_authors"] >= min_authors)
    side = np.where(table["z"] > 0, "emotion", "comparison")
    keep = np.where(
        side == "emotion", recurs["emotion"].to_numpy(), recurs["comparison"]
    )
    return table[keep].reset_index(drop=True)


def sign_flip_p(diffs: np.ndarray, rng: np.random.Generator) -> float:
    """Two-sided p-value of the mean difference under random sign flips."""
    observed = abs(diffs.mean())
    signs = rng.choice([-1.0, 1.0], size=(N_PERMUTATIONS, len(diffs)))
    null = np.abs((signs * diffs).mean(axis=1))
    return float((1 + (null >= observed - 1e-12).sum()) / (N_PERMUTATIONS + 1))


def holm(p_values: pd.Series) -> pd.Series:
    order = p_values.sort_values()
    m = len(order)
    adjusted = np.maximum.accumulate(order.to_numpy() * (m - np.arange(m)))
    return pd.Series(np.minimum(adjusted, 1.0), index=order.index).reindex(
        p_values.index
    )


def compare_novels(per_novel: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """One row per feature: the detected set against the comparison set.

    `per_novel` has one row per novel and set (columns `novel_id`, `set`,
    `n_paragraphs` and the features). Each novel's two values are paired;
    the difference is tested with a sign-flip permutation test over novels,
    with a bootstrap interval for the relative difference and Holm's
    correction across the features.
    """
    rng = np.random.default_rng(SEED)
    wide = per_novel.pivot_table(
        index="novel_id", columns="set", values=["n_paragraphs", *features]
    )
    if wide.empty or "emotion" not in wide["n_paragraphs"]:
        return pd.DataFrame()
    enough = (wide["n_paragraphs"] >= MIN_PARAGRAPHS).all(axis=1)
    wide = wide[enough]
    rows = []
    for feature in features:
        pair = wide[feature].dropna()
        if len(pair) < MIN_NOVELS:
            continue
        a, b = pair["emotion"].to_numpy(), pair["comparison"].to_numpy()
        diffs = a - b
        boot = rng.integers(0, len(diffs), size=(N_BOOTSTRAP, len(diffs)))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = diffs[boot].mean(axis=1) / b[boot].mean(axis=1)
        rel = rel[np.isfinite(rel)]
        rows.append(
            {
                "feature": feature,
                "n_novels": len(pair),
                "mean_emotion": a.mean(),
                "mean_comparison": b.mean(),
                "rel_diff": diffs.mean() / b.mean(),
                "rel_ci_low": np.quantile(rel, 0.025),
                "rel_ci_high": np.quantile(rel, 0.975),
                "p_value": sign_flip_p(diffs, rng),
            }
        )
    table = pd.DataFrame(rows)
    if not table.empty:
        table["p_holm"] = holm(table["p_value"])
    return table


def moving_average(
    df: pd.DataFrame, first: int, last: int, window: int, min_n: int
) -> pd.DataFrame:
    """Mean `value` of the novels in a sliding window of years, per `group`.

    With a 95 % interval over novels. Years with fewer than `min_n` novels
    in the window are skipped, and `segment` numbers the runs of consecutive
    years, so that lines break across gaps instead of bridging decades with
    no data.
    """
    rows = []
    for group, members in df.groupby("group"):
        for year in range(first, last + 1):
            inside = members[
                members["year"].between(year - window / 2, year + window / 2 - 1)
            ]
            if len(inside) < min_n:
                continue
            mean = inside["value"].mean()
            half = 1.96 * inside["value"].std(ddof=1) / np.sqrt(len(inside))
            rows.append((group, year, mean, mean - half, mean + half, len(inside)))
    ma = pd.DataFrame(rows, columns=["group", "year", "mean", "low", "high", "n"])
    if ma.empty:
        return ma.assign(segment=[])
    gap = ma.groupby("group")["year"].diff().fillna(1) > 1
    run = gap.groupby(ma["group"]).cumsum()
    ma = ma.assign(
        segment=ma["group"] + "/" + run.astype(str), low=ma["low"].clip(lower=0)
    )
    # A single year draws no line, but its band would still stretch the axis.
    return ma[ma.groupby("segment")["year"].transform("size") > 1]


def rank_correlation(x: pd.Series, y: pd.Series) -> float:
    """Spearman's rank correlation; NaN with fewer than five pairs."""
    if len(x) < 5:
        return float("nan")
    return float(x.rank().corr(y.rank()))


def reflected_density(positions: np.ndarray, grid: np.ndarray, bandwidth: float):
    """Gaussian kernel density on 0–100, reflected at both ends.

    Scaled so that an even spread is 1. Positions are first binned to 0.1,
    so that the cost does not grow with the number of paragraphs.
    """
    edges = np.linspace(0, 100, 1001)
    counts, _ = np.histogram(positions, bins=edges)
    centres = (edges[:-1] + edges[1:]) / 2
    points = np.concatenate([centres, -centres, 200 - centres])
    weights = np.tile(counts, 3)
    kernel = np.exp(-0.5 * ((grid[:, None] - points[None, :]) / bandwidth) ** 2)
    density = (kernel * weights).sum(axis=1)
    return density / (counts.sum() * bandwidth * np.sqrt(2 * np.pi)) * 100
