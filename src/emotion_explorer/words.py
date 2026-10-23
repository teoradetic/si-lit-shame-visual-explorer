"""AN-03 (preliminary): word counts behind the lists of typical words.

The pipeline counts each word per novel in the detected set and in its
comparison set; the app compares any group of novels with a weighted
log-odds ratio (`app/stats.py`), with the whole corpus as the prior. Without
a tagger (DATA-04) the counts hold every part of speech and the forms are
not lemmatized; names are dropped by capitalization.
"""

from collections import Counter
from importlib.resources import files

import pandas as pd

from emotion_explorer.text import capitalization, words

# A word is a name if it is capitalized in more than this share of its
# occurrences that do not start a sentence.
NAME_CAPITAL_SHARE = 0.5
MIN_LENGTH = 2
MIN_COUNT = 10


def function_words() -> set[str]:
    text = files("emotion_explorer").joinpath("resources/function_words_sl.txt")
    lines = text.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.startswith("#")}


def corpus_counts(texts: pd.Series) -> tuple[Counter, set[str]]:
    """Word counts over the whole corpus, and the words that are names."""
    counts: Counter = Counter()
    seen: Counter = Counter()
    capitals: Counter = Counter()
    for text in texts:
        counts.update(words(text))
        for word, is_capital in capitalization(text):
            seen[word] += 1
            capitals[word] += is_capital
    names = {w for w, n in seen.items() if capitals[w] / n > NAME_CAPITAL_SHARE}
    return counts, names


def vocabulary(counts: Counter, names: set[str]) -> set[str]:
    """Words that can enter a word list.

    `counts` are the words of the compared sets at their largest (the broad
    tier and its partners). Any slice of them counts a word at most as often,
    so a word below MIN_COUNT here can never pass it in a slice.
    """
    return {
        w
        for w, n in counts.items()
        if n >= MIN_COUNT and len(w) >= MIN_LENGTH and w not in names
    }


def count_words(paragraphs: pd.DataFrame, keep: set[str]) -> pd.DataFrame:
    """Occurrences of each kept word per novel; `paragraphs` has a `words` column."""
    rows = [
        (novel_id, word, n)
        for novel_id, group in paragraphs.groupby("novel_id", observed=True)
        for word, n in Counter(
            w for ws in group["words"] for w in ws if w in keep
        ).items()
    ]
    return pd.DataFrame(rows, columns=["novel_id", "word", "n"])
