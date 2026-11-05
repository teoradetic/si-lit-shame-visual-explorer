"""Interface strings, one file per language in assets/languages/; adding a
language means adding a file. The excerpts stay in Slovene.

The texts are written for readers outside literary studies and statistics;
technical detail lives on the method page and in "how is this calculated"
boxes. Slovene strings avoid number agreement ("Romanov: 5" rather than
"5 romanov") so that one template fits every count.
"""

from pathlib import Path

import streamlit as st
import yaml

LANGUAGE_DIR = Path(__file__).resolve().parents[1] / "assets" / "languages"
DEFAULT = "en"
# Code -> {"language": name, flag, decimal and thousands marks; "strings": ...}
FILES = {
    path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
    for path in sorted(LANGUAGE_DIR.glob("*.yaml"))
}
LANGUAGES = (DEFAULT, *sorted(set(FILES) - {DEFAULT}))


def lang() -> str:
    return st.session_state.get("lang") or DEFAULT


def setting(name: str, code: str | None = None) -> str:
    """A language's own setting: name, flag, decimal or thousands."""
    return FILES[code or lang()]["language"][name]


def t(key: str, **values) -> str:
    text = FILES[lang()]["strings"][key]
    return text.format(**values) if values else text


def label(prefix: str, value: str) -> str:
    """Translated label of a data value, e.g. label("period", "Realism")."""
    return t(f"{prefix}.{value}")


def labels(prefix: str, values) -> dict[str, str]:
    return {v: label(prefix, v) for v in values}


def localize(text: str) -> str:
    """A number written the English way (1,234.5), in the reader's marks."""
    marks = {",": setting("thousands"), ".": setting("decimal")}
    return "".join(marks.get(c, c) for c in text)


def num(value: float, digits: int = 1) -> str:
    """A number in the reader's language: 1,234.5 in English, 1.234,5 in Slovene."""
    return localize(f"{value:,.{digits}f}")
