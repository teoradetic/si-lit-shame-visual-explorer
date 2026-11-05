"""Surface text processing without a tagger: words, sentences, dialogue.

These rules are rough on historical spelling, and the views that use them
say so. The word lists use the lemmas of DATA-04 instead; Style still uses
these rules.
"""

import re

# Letters only: digits, underscores and punctuation split words.
WORD_RE = re.compile(r"[^\W\d_]+")
# A sentence ends at . ! ? or an ellipsis, followed by space and an
# upper-case letter, possibly behind quotes, dashes or brackets.
SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+(?=[\"'»«„“”‚‘(–—-]*\s*[^\W\d_])")
# Opening and closing quotes used in the corpus, and the speech dash.
QUOTE_CHARS = '»«„“”"'
SPEECH_DASH_RE = re.compile(r"^\s*[–—-]")


def words(text: str) -> list[str]:
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END_RE.split(text.strip()) if s]


def has_dialogue(text: str) -> bool:
    return any(c in text for c in QUOTE_CHARS) or bool(SPEECH_DASH_RE.match(text))
