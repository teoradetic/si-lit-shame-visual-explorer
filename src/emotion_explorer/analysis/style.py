"""AN-08: style features per paragraph, pooled per novel and set."""

import re

import numpy as np
import pandas as pd

from emotion_explorer.analysis.text import sentences, words

# Punctuation counted per 1,000 characters. Any run of two or more dots or
# ellipses, spaced or not (.. ... . . . …. !..), is one ellipsis.
PUNCTUATION = {
    name: re.compile(pattern)
    for name, pattern in {
        "exclamation": r"!",
        "question": r"\?",
        "semicolon": r";",
        "comma": r",",
        "ellipsis": r"[.…](?: ?[.…])+|…",
        "dash": r"[–—]| - ",
    }.items()
}
# A word repeats if it occurred within this many words before it.
REPEAT_WINDOW = 10
REPEAT_MIN_LENGTH = 3
MATTR_WINDOW = 100

FEATURES = (
    "sentence_words",
    "mattr",
    "repetition",
    *(f"{name}_per_1k" for name in PUNCTUATION),
)


def count_repeats(tokens: list[str]) -> tuple[int, int]:
    """(repeated words, eligible words) for one paragraph."""
    eligible = repeats = 0
    for i, word in enumerate(tokens):
        if len(word) < REPEAT_MIN_LENGTH:
            continue
        eligible += 1
        repeats += word in tokens[max(0, i - REPEAT_WINDOW) : i]
    return repeats, eligible


def paragraph_features(text: str) -> dict:
    """Raw counts; rates are formed only after pooling."""
    tokens = words(text)
    repeats, eligible = count_repeats(tokens)
    counts = {name: len(mark.findall(text)) for name, mark in PUNCTUATION.items()}
    return {
        "n_chars": len(text),
        "n_words": len(tokens),
        "n_sentences": max(len(sentences(text)), 1),
        "n_repeats": repeats,
        "n_eligible": eligible,
        **{f"n_{name}": n for name, n in counts.items()},
    }


def mattr(tokens: list[str], window: int = MATTR_WINDOW) -> float:
    """Moving-average type-token ratio; NaN for texts shorter than a window."""
    if len(tokens) < window:
        return float("nan")
    counts: dict[str, int] = {}
    for word in tokens[:window]:
        counts[word] = counts.get(word, 0) + 1
    ratios = [len(counts) / window]
    for i in range(window, len(tokens)):
        old, new = tokens[i - window], tokens[i]
        counts[old] -= 1
        if counts[old] == 0:
            del counts[old]
        counts[new] = counts.get(new, 0) + 1
        ratios.append(len(counts) / window)
    return float(np.mean(ratios))


def pool(group: pd.DataFrame) -> pd.Series:
    """Per-novel feature values from the paragraphs of one set."""
    total = group.sum(numeric_only=True)
    tokens = [w for ws in group["words"] for w in ws]
    return pd.Series(
        {
            "n_paragraphs": len(group),
            "sentence_words": total["n_words"] / total["n_sentences"],
            "mattr": mattr(tokens),
            "repetition": total["n_repeats"] / max(total["n_eligible"], 1),
            **{
                f"{name}_per_1k": total[f"n_{name}"] / total["n_chars"] * 1_000
                for name in PUNCTUATION
            },
        }
    )
