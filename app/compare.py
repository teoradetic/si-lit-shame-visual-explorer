"""The comparison every chart is broken down by, set once in the sidebar.

The filters choose the novels; the comparison splits them into groups,
each with a fixed colour, and every view draws those groups:

- nothing: all selected novels together;
- with against without shame: the detected passages against those the
  model rated clearly not about shame, in the same novels;
- periods, author gender, two authors, or up to three novels of one author.
"""

from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st

import charts
import filters
from language import label, t

MODES = ("none", "shame", "period", "gender", "authors", "novels")
MAX_NOVELS = 3


@dataclass(frozen=True)
class Group:
    key: str
    label: str
    color: str
    novel_ids: frozenset[str]
    # "comparison": the passages without shame (only in the "shame" mode).
    set_name: str = "emotion"


def mode() -> str:
    return st.session_state.get("cmp_mode", "none")


def _authors(novels: pd.DataFrame) -> list[str]:
    """Authors with the most novels first, so the defaults are informative."""
    counts = novels.groupby("author").size().reset_index(name="n")
    return counts.sort_values(["n", "author"], ascending=[False, True])[
        "author"
    ].tolist()


def _keep_valid(key: str, options: list, default) -> None:
    """Reset a picker whose value the filters have just removed."""
    if st.session_state.get(key) not in options:
        st.session_state[key] = default


def sidebar() -> None:
    novels = filters.filtered_novels()
    authors = _authors(novels)
    with st.sidebar:
        st.header(t("compare.header"))
        st.selectbox(
            t("compare.mode"),
            MODES,
            format_func=lambda v: t(f"compare.mode.{v}"),
            key="cmp_mode",
            help=t("compare.help"),
        )
        if not authors:
            return
        if mode() == "authors":
            _keep_valid("cmp_author_a", authors, authors[0])
            _keep_valid("cmp_author_b", authors, authors[min(1, len(authors) - 1)])
            st.selectbox(t("compare.author_a"), authors, key="cmp_author_a")
            st.selectbox(t("compare.author_b"), authors, key="cmp_author_b")
        elif mode() == "novels":
            _keep_valid("cmp_author", authors, authors[0])
            st.selectbox(t("compare.author"), authors, key="cmp_author")
            own = novels[novels["author"] == st.session_state["cmp_author"]]
            ids = own.sort_values("year")["novel_id"].tolist()
            chosen = [i for i in st.session_state.get("cmp_novels", []) if i in ids]
            if not chosen:
                tier = filters.current().tier
                top = own.nlargest(MAX_NOVELS, f"n_{tier}")["novel_id"]
                chosen = [i for i in ids if i in set(top)]
            st.session_state["cmp_novels"] = chosen
            titles = filters.novel_titles()
            st.multiselect(
                t("compare.novels"),
                ids,
                format_func=titles.get,
                max_selections=MAX_NOVELS,
                key="cmp_novels",
            )


def _short_title(row) -> str:
    return f"{row.title} ({row.year})"


def groups() -> list[Group]:
    """The groups of the current comparison, in their fixed order."""
    novels = filters.filtered_novels()
    ids = frozenset(novels["novel_id"])
    m = mode()
    if m == "none":
        return [Group("all", t("compare.everyone"), charts.set_color("emotion"), ids)]
    if m == "shame":
        return [
            Group("emotion", t("set.emotion"), charts.set_color("emotion"), ids),
            Group(
                "comparison",
                t("set.comparison"),
                charts.set_color("comparison"),
                ids,
                "comparison",
            ),
        ]
    if m == "period":
        found = [
            Group(
                p,
                label("period", p),
                charts.period_color(p),
                frozenset(novels.loc[novels["period"] == p, "novel_id"]),
            )
            for p in ("Realism", "Modernism")
        ]
    elif m == "gender":
        found = [
            Group(
                g,
                label("gender", g),
                charts.group_color(i),
                frozenset(novels.loc[novels["gender"] == g, "novel_id"]),
            )
            for i, g in enumerate(("F", "M"))
        ]
    elif m == "authors":
        names = dict.fromkeys(
            [st.session_state.get("cmp_author_a"), st.session_state.get("cmp_author_b")]
        )
        found = [
            Group(
                a,
                a,
                charts.group_color(i),
                frozenset(novels.loc[novels["author"] == a, "novel_id"]),
            )
            for i, a in enumerate(n for n in names if n)
        ]
    else:
        chosen = novels.set_index("novel_id").reindex(
            st.session_state.get("cmp_novels", [])
        )
        found = [
            Group(nid, _short_title(row), charts.group_color(i), frozenset([nid]))
            for i, (nid, row) in enumerate(chosen.dropna(subset=["title"]).iterrows())
        ]
    return [g for g in found if g.novel_ids]


def is_split() -> bool:
    """Whether the groups are different novels (not the shame mode)."""
    return mode() not in ("none", "shame")


def novel_groups() -> pd.Series:
    """Group label by novel_id, for the novels inside a group.

    Without a split (nothing, or with against without shame) every selected
    novel takes the first group's label.
    """
    gs = groups() if is_split() else groups()[:1]
    return pd.Series({nid: g.label for g in gs for nid in g.novel_ids}, dtype=object)


def with_group(df: pd.DataFrame) -> pd.DataFrame:
    """Rows of novels in a group, with the group's label in `group`."""
    by_novel = novel_groups()
    return df[df["novel_id"].isin(by_novel.index)].assign(
        group=lambda d: d["novel_id"].map(by_novel).astype(str)
    )


def order() -> list[str]:
    return [g.label for g in groups()]


def color(field: str = "group", legend: bool = True) -> alt.Color:
    gs = groups()
    return alt.Color(
        f"{field}:N",
        scale=alt.Scale(domain=[g.label for g in gs], range=[g.color for g in gs]),
        legend=alt.Legend(title=None) if legend else None,
    )


def left_out_note() -> str | None:
    """Selected novels that belong to no group, e.g. those of unknown period."""
    if not is_split():
        return None
    inside = set().union(*(g.novel_ids for g in groups())) if groups() else set()
    n = len(filters.novel_ids() - inside)
    if n and mode() in ("period", "gender"):
        return t(f"compare.left_out.{mode()}", n=n)
    return None


def require(min_groups: int = 1) -> list[Group]:
    """The groups, or a warning and a stop when there are too few."""
    gs = groups()
    if mode() == "authors" and len(gs) < 2:
        st.warning(t("compare.need_two_authors"))
    if len(gs) < min_groups:
        st.warning(t("compare.need_groups", n=min_groups))
        st.stop()
    if not gs:
        st.warning(t("filters.empty"))
        st.stop()
    note = left_out_note()
    if note:
        st.caption(note)
    return gs


def panels(chart, axis: str = "y", width: int = 360):
    """With against without shame: one panel per set, each with its own scale.

    The shares of paragraphs with and without shame differ about tenfold, so
    on one axis one of them would lie flat.
    """
    if mode() != "shame":
        return chart
    return (
        chart.properties(width=width)
        .facet(
            column=alt.Column(
                "group:N", sort=order(), title=None, header=alt.Header(labelFontSize=13)
            )
        )
        .resolve_scale(**{axis: "independent"})
    )


def set_of(group_label: str, tier: str) -> str:
    """The excerpt set behind a group: the tier, or the comparison set."""
    for g in groups():
        if g.label == group_label and g.set_name == "comparison":
            return "comparison"
    return tier
