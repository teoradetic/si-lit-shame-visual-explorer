"""How the passages were found, and what the app cannot show."""

import streamlit as st

from helpers import tables
from helpers.language import LANGUAGE_DIR, lang, localize, num, t


def number(value: float) -> str:
    return num(value, 0)


def decimal(value: float) -> str:
    return localize(f"{value:g}")


meta = tables.meta()
par, comp, exc = meta["paragraphs"], meta["comparison"], meta["excerpts"]
values = {
    "n_novels": par["n_novels"],
    "n_authors": par["n_authors"],
    "first": par["year_range"][0],
    "last": par["year_range"][1],
    "n_paragraphs": number(par["n_paragraphs"]),
    "n_low": number(par["low_count"]),
    "n_over_context": par["over_context_count"],
    "over_context_chars": number(par["over_context_chars"]),
    "context": exc["context"],
    "max_length_ratio": comp["max_length_ratio"],
    "n_matched": number(comp["n_matched"]),
    "n_novels_with_pairs": comp["n_novels_with_pairs"],
    "n_realism": par["novels_by_period"].get("Realism", 0),
    "n_modernism": par["novels_by_period"].get("Modernism", 0),
    "n_period_unknown": par["novels_by_period"].get("unknown", 0),
}
values["n_emotion"] = number(par["n_emotion"])
for scale, minimum in par["minimum"].items():
    values[f"min_{scale}"] = decimal(minimum)
for scale, maximum in par["low"].items():
    values[f"low_{scale}"] = decimal(maximum)

st.title(t("method.title"))
text = (LANGUAGE_DIR / f"method.{lang()}.md").read_text(encoding="utf-8")
st.markdown(text.format(**values))
