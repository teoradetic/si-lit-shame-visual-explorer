"""What is specific to one emotion: raw field names, tiers and the low-score rule.

Everything downstream works on the generic column names defined here, so a
new emotion (or corpus) only needs a new `Emotion` instance.
"""

from dataclasses import dataclass, field

# The three score ranges the LLM was asked for, as suffixes of the raw keys.
SCALES = ("0_1", "0_10", "0_100")
SCALE_MAX = {"0_1": 1.0, "0_10": 10.0, "0_100": 100.0}


@dataclass(frozen=True)
class Emotion:
    name: str
    # Word stem whose presence the raw corpus flags per paragraph.
    stem: str
    stem_key: str
    # Raw key of a score, with `{scale}` standing for one of SCALES.
    score_key: str
    # Tier name -> minimum score on every range (all three must be met).
    tiers: dict[str, dict[str, float]] = field(default_factory=dict)
    # Maximum score on every range for a paragraph to count as "low"
    # (the pool the comparison set is drawn from).
    low: dict[str, float] = field(default_factory=dict)


SHAME = Emotion(
    name="shame",
    stem="sram",
    stem_key="text_contains_root_sram",
    score_key="mistral_instruct_{scale}_shame_score",
    tiers={
        # The paper's rule: top 1% on all three ranges.
        "core": {"0_1": 0.95, "0_10": 8, "0_100": 85},
        # Top 5% on all three ranges.
        "broad": {"0_1": 0.85, "0_10": 8, "0_100": 85},
    },
    # Provisional (23 Oct 2026): the bottom cluster of each range. Each range
    # has a gap above these values (0-1: 0.30 -> 0.35, 0-10: 3 -> 5,
    # 0-100: 30 -> 50). 37% of paragraphs qualify; only 0.1% of them
    # contain the stem, against 1.5% in the corpus.
    low={"0_1": 0.30, "0_10": 3, "0_100": 30},
)

TIERS = tuple(SHAME.tiers)
