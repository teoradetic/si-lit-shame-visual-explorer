"""Every interface string exists in both languages with the same placeholders."""

import re
import string
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from language import LANGUAGES, STRINGS  # noqa: E402


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_both_languages_with_same_placeholders():
    for key, texts in STRINGS.items():
        assert set(texts) == set(LANGUAGES), key
        assert placeholders(texts["en"]) == placeholders(texts["sl"]), key


def test_every_literal_key_exists():
    used = set()
    for path in APP_DIR.rglob("*.py"):
        used |= set(re.findall(r'\bt\(\s*"([\w.]+)"', path.read_text(encoding="utf-8")))
    assert used - set(STRINGS) == set()
