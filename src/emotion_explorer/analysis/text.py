"""Surface text processing without a tagger: words, sentences, speech.

These rules are rough on historical spelling, and the views that use them
say so. The word lists use the lemmas of the token tables instead; Style
still uses these rules.
"""

import re

import pandas as pd

# Letters only: digits, underscores and punctuation split words.
WORD_RE = re.compile(r"[^\W\d_]+")
# A sentence ends at . ! ? or an ellipsis, followed by space and an
# upper-case letter, possibly behind quotes, dashes or brackets.
SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+(?=[\"'»«„“”‚‘(–—-]*\s*[^\W\d_])")
# Opening and closing quotes used in the corpus, and the speech dash.
QUOTES = frozenset('»«„“”"')
QUOTE_RE = re.compile(f"([{''.join(QUOTES)}])")
SPEECH_DASH_RE = re.compile(r"^\s*[–—-]")


def words(text: str) -> list[str]:
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END_RE.split(text.strip()) if s]


def speech_flags(pieces: pd.Series) -> pd.Series:
    """Which pieces (tokens, or the text between quotes) are speech.

    `pieces` is indexed by paragraph, in reading order. Each quotation mark
    opens or closes speech, whatever its shape, since editions differ (»…«,
    «…», „…“). Without quotes, a paragraph that opens with a dash is all
    speech; dashes inside it also mark pauses, so they cannot tell speech from
    the narration around it.
    """
    marks = pieces.isin(QUOTES)
    by_paragraph = marks.groupby(level=0, sort=False)
    inside = (by_paragraph.cumsum() % 2 == 1) | marks
    opens_with_dash = (
        pieces.groupby(level=0, sort=False)
        .transform("first")
        .map(lambda p: bool(SPEECH_DASH_RE.match(p)))
    )
    return inside.where(by_paragraph.transform("any"), opens_with_dash)


def split_speech(texts: pd.Series) -> pd.DataFrame:
    """Each paragraph whole (`all`), its narration and its speech (`dialogue`)."""
    pieces = texts.map(QUOTE_RE.split).explode()
    speech = speech_flags(pieces)
    parts = {
        split: pieces[speech == flag]
        .groupby(level=0)
        .agg(" ".join)
        .str.strip()
        .reindex(texts.index, fill_value="")
        for split, flag in (("narration", False), ("dialogue", True))
    }
    return pd.DataFrame({"all": texts, **parts})
