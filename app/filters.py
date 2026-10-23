"""APP-01: global filters, kept in session state and applied to every view.

The widgets live in the entrypoint's sidebar, which runs on every page, so
their values survive page changes.
"""

from dataclasses import dataclass

import pandas as pd
import streamlit as st

import tables
from charts import GENDERS, PERIODS
from language import label, num, t

DEFAULT_TIER = "broad"


@dataclass(frozen=True)
class Filters:
    tier: str
    periods: list[str]
    genders: list[str]
    authors: list[str]
    novels: list[str]
    years: tuple[int, int]


def _year_bounds() -> tuple[int, int]:
    years = tables.novels()["year"]
    return int(years.min()), int(years.max())


def _reset() -> None:
    st.session_state["f_tier"] = DEFAULT_TIER
    st.session_state["f_periods"] = list(PERIODS)
    st.session_state["f_genders"] = list(GENDERS)
    st.session_state["f_authors"] = []
    st.session_state["f_novels"] = []
    st.session_state["f_years"] = _year_bounds()


def sidebar() -> None:
    if "f_tier" not in st.session_state:
        _reset()
    novels = tables.novels()
    with st.sidebar:
        st.header(t("filters.header"))
        tiers = list(tables.meta()["paragraphs"]["tiers"])
        st.radio(
            t("filters.tier"),
            tiers,
            format_func=lambda v: label("tier", v),
            key="f_tier",
            help=t("filters.tier_help"),
        )
        st.pills(
            t("filters.period"),
            list(PERIODS),
            selection_mode="multi",
            format_func=lambda v: label("period", v),
            key="f_periods",
        )
        st.pills(
            t("filters.gender"),
            list(GENDERS),
            selection_mode="multi",
            format_func=lambda v: label("gender_short", v),
            key="f_genders",
        )
        st.multiselect(
            t("filters.authors"),
            sorted(novels["author"].unique()),
            key="f_authors",
            placeholder=t("filters.authors_placeholder"),
        )
        titles = novel_titles()
        st.multiselect(
            t("filters.novels"),
            sorted(titles, key=titles.get),
            format_func=titles.get,
            key="f_novels",
            placeholder=t("filters.novels_placeholder"),
        )
        low, high = _year_bounds()
        st.slider(t("filters.years"), low, high, key="f_years")
        st.button(t("filters.reset"), on_click=_reset)

        selected = filtered_novels()
        n_tagged = int(selected[f"n_{current().tier}"].sum())
        st.caption(
            t("filters.summary", novels=len(selected), paragraphs=num(n_tagged, 0))
        )


def current() -> Filters:
    s = st.session_state
    return Filters(
        tier=s.get("f_tier", DEFAULT_TIER),
        periods=list(s.get("f_periods", PERIODS)),
        genders=list(s.get("f_genders", GENDERS)),
        authors=list(s.get("f_authors", [])),
        novels=list(s.get("f_novels", [])),
        years=tuple(s.get("f_years", _year_bounds())),
    )


def filtered_novels() -> pd.DataFrame:
    f = current()
    novels = tables.novels()
    mask = (
        novels["period"].isin(f.periods)
        & novels["gender"].isin(f.genders)
        & novels["year"].between(*f.years)
    )
    if f.authors:
        mask &= novels["author"].isin(f.authors)
    if f.novels:
        mask &= novels["novel_id"].isin(f.novels)
    return novels[mask]


def novel_titles() -> dict[str, str]:
    """novel_id -> "Author: Title (year)", the label used in pickers."""
    novels = tables.novels()
    labels = (
        novels["author"]
        + ": "
        + novels["title"]
        + " ("
        + novels["year"].astype(str)
        + ")"
    )
    return dict(zip(novels["novel_id"], labels, strict=True))


def novel_ids() -> set[str]:
    return set(filtered_novels()["novel_id"])


def stop_if_empty() -> None:
    if not novel_ids():
        st.warning(t("filters.empty"))
        st.stop()
