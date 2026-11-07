"""What is specific to one emotion; a new emotion needs a new `Emotion`."""

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
    # Minimum score on every range for a paragraph to count as detected
    # (all three must be met).
    minimum: dict[str, float] = field(default_factory=dict)
    # Maximum score on every range for a paragraph to count as "low"
    # (the pool the comparison set is drawn from).
    low: dict[str, float] = field(default_factory=dict)


SHAME = Emotion(
    name="shame",
    stem="sram",
    stem_key="text_contains_root_sram",
    score_key="mistral_instruct_{scale}_shame_score",
    # Top 5% on all three ranges.
    minimum={"0_1": 0.85, "0_10": 8, "0_100": 85},
    # The bottom cluster of each range (agreed 30 Oct 2026).
    low={"0_1": 0.30, "0_10": 3, "0_100": 30},
)
