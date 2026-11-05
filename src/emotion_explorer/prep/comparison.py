"""DATA-03: the comparison set, paragraphs with low scores.

Each broad-tier paragraph gets one low-score partner from the same novel with
the closest length, if one is within a factor of MAX_LENGTH_RATIO. Long
low-score paragraphs are scarce (their median is 73 characters, against 381
in the broad tier), so without the caliper the comparison set would be much
shorter than the set it is compared with.

"All untagged paragraphs" would not do as a contrast: they still hold most of
the corpus's shame.
"""

import numpy as np
import pandas as pd

# Same as the excerpt context, so comparison excerpts never share paragraphs
# with the excerpts of the set they are matched to.
EXCLUSION_RADIUS = 2
SEED = 20261030
MAX_LENGTH_RATIO = 2.0


def near_tagged(
    para_ids: np.ndarray, tagged_ids: np.ndarray, radius: int
) -> np.ndarray:
    """True for paragraphs within `radius` of a tagged paragraph."""
    near = np.zeros(len(para_ids), dtype=bool)
    tagged = set(tagged_ids.tolist())
    for offset in range(-radius, radius + 1):
        near |= np.isin(para_ids + offset, list(tagged))
    return near


def match_novel(
    novel: pd.DataFrame, tagged_col: str, rng: np.random.Generator
) -> list[tuple[int, int]]:
    """(tagged para_id, comparison para_id) pairs for one novel."""
    ids = novel["para_id"].to_numpy()
    tagged = novel[novel[tagged_col]]
    candidate_mask = (
        novel["low"].to_numpy()
        & ~novel["over_context"].to_numpy()
        & (novel["n_chars"].to_numpy() > 0)
        & ~near_tagged(ids, tagged["para_id"].to_numpy(), EXCLUSION_RADIUS)
    )
    candidates = novel[candidate_mask]
    # Shuffle first, so that ties between equally long candidates are random.
    candidates = candidates.iloc[rng.permutation(len(candidates))]
    cand_ids = candidates["para_id"].to_numpy()
    cand_len = np.log1p(candidates["n_chars"].to_numpy())
    used = np.zeros(len(candidates), dtype=bool)

    pairs = []
    # Longest first: long low-score paragraphs are scarce.
    for row in tagged.sort_values("n_chars", ascending=False).itertuples():
        if used.all():
            break
        distance = np.abs(cand_len - np.log1p(row.n_chars))
        distance[used] = np.inf
        best = int(np.argmin(distance))
        if distance[best] > np.log(MAX_LENGTH_RATIO):
            continue
        used[best] = True
        pairs.append((row.para_id, int(cand_ids[best])))
    return pairs


def build_comparison(paragraphs: pd.DataFrame, tagged_col: str) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    cols = ["novel_id", "para_id", "n_chars", "low", "over_context", tagged_col]
    records = []
    for novel_id, novel in paragraphs[cols].groupby("novel_id", observed=True):
        for tagged_id, comp_id in match_novel(novel, tagged_col, rng):
            records.append((novel_id, comp_id, tagged_id))
    return pd.DataFrame.from_records(
        records, columns=["novel_id", "para_id", "matched_para_id"]
    ).astype({"para_id": "int32", "matched_para_id": "int32"})


def summarize_comparison(
    paragraphs: pd.DataFrame, comparison: pd.DataFrame, tagged_col: str
) -> dict:
    lengths = paragraphs[["novel_id", "para_id", "n_chars"]]
    pairs = comparison.merge(lengths, on=["novel_id", "para_id"]).merge(
        lengths.rename(columns={"para_id": "matched_para_id"}),
        on=["novel_id", "matched_para_id"],
        suffixes=("", "_tagged"),
    )
    comp_len = pairs["n_chars"].to_numpy()
    tagged_len = pairs["n_chars_tagged"].to_numpy()
    log_ratio = np.log2((comp_len + 1) / (tagged_len + 1))
    n_tagged = int(paragraphs[tagged_col].sum())
    return {
        "matched_to": tagged_col,
        "seed": SEED,
        "exclusion_radius": EXCLUSION_RADIUS,
        "max_length_ratio": MAX_LENGTH_RATIO,
        "n_tagged": n_tagged,
        "n_matched": len(comparison),
        "n_unmatched": n_tagged - len(comparison),
        "median_chars_tagged": float(
            paragraphs.loc[paragraphs[tagged_col], "n_chars"].median()
        ),
        "median_chars_tagged_matched": float(np.median(tagged_len)),
        "median_chars_comparison": float(np.median(comp_len)),
        "median_abs_log2_length_ratio": float(np.median(np.abs(log_ratio))),
        "share_within_25pct_length": float(np.mean(np.abs(log_ratio) <= np.log2(1.25))),
        "n_novels_with_pairs": int(comparison["novel_id"].nunique()),
    }
