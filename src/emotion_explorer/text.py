"""Surface text processing without a tagger: words, sentences, dialogue.

These rules are rough on historical spelling, and the views that use them
say so. DATA-04 (CLASSLA) will replace the word and sentence parts.
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
# What may stand between a sentence end and the next word.
GAP_CHARS = " \n\t\"'»«„“”‚‘(–—-"
SENTENCE_END_CHARS = ".!?…:"


def words(text: str) -> list[str]:
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_END_RE.split(text.strip()) if s]


def has_dialogue(text: str) -> bool:
    return any(c in text for c in QUOTE_CHARS) or bool(SPEECH_DASH_RE.match(text))


def capitalization(text: str) -> list[tuple[str, bool]]:
    """(lower-case word, is capitalized) for every word that does not start
    a sentence, since only there do capitals mark a name."""
    out = []
    prev_end = 0
    for i, m in enumerate(WORD_RE.finditer(text)):
        before = text[prev_end : m.start()].rstrip(GAP_CHARS)
        starts_sentence = i == 0 or (before != "" and before[-1] in SENTENCE_END_CHARS)
        if not starts_sentence:
            out.append((m.group().lower(), m.group()[0].isupper()))
        prev_end = m.end()
    return out
