"""Every language file has the same strings, with the same placeholders."""

import re
import string
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from helpers.language import DEFAULT, FILES, LANGUAGE_DIR  # noqa: E402


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_every_language_has_the_same_strings_and_placeholders():
    reference = FILES[DEFAULT]["strings"]
    for code, file in FILES.items():
        strings = file["strings"]
        assert set(strings) == set(reference), code
        for key, text in strings.items():
            assert placeholders(text) == placeholders(reference[key]), (code, key)


def test_every_language_has_its_settings_and_method_page():
    for code, file in FILES.items():
        assert set(file["language"]) == {"name", "flag", "decimal", "thousands"}
        assert (LANGUAGE_DIR / f"method.{code}.md").exists(), code


def test_every_literal_key_exists():
    used = set()
    for path in APP_DIR.rglob("*.py"):
        used |= set(re.findall(r'\bt\(\s*"([\w.]+)"', path.read_text(encoding="utf-8")))
    assert used - set(FILES[DEFAULT]["strings"]) == set()
