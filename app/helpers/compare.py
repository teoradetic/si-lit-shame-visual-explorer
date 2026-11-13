"""The comparison, chosen and run at the top of each analysis page; every
chart draws its groups."""

from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st

from helpers import charts, filters
from helpers.language import label, lang, t

MODES = ("shame", "period", "gender", "authors", "rest", "novels")
MAX_NOVELS = 3
# The picker edits a draft; "Run" copies it to the comparison the pages use.
DRAFT = ("cmp_mode", "cmp_author_a", "cmp_author_b", "cmp_author", "cmp_novels")


@dataclass(frozen=True)
class Group:
    key: str
    label: str
    color: str
    novel_ids: frozenset[str]
    # "comparison": the passages without shame (only in the "shame" mode).
    set_name: str = "emotion"

    @property
    def counted(self) -> str:
        """Its paragraphs in the novels and paragraph tables: those without
        shame count the low-score paragraphs."""
        return "low" if self.set_name == "comparison" else "emotion"


def _applied() -> dict:
    return st.session_state.get("cmp_applied", {})


def _draft() -> dict:
    return {k: st.session_state.get(k) for k in DRAFT}


def keep_draft() -> None:
    """Keep the pickers' values on pages and in modes that do not draw them;
    Streamlit drops a widget's value when the widget is not drawn."""
    for key in DRAFT[1:]:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def mode() -> str | None:
    """The comparison the pages show; None until the first run."""
    return _applied().get("cmp_mode")


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


def picker() -> None:
    """What to compare, at the top of every analysis page."""
    novels = filters.filtered_novels()
    authors = _authors(novels)
    with st.container(border=True):
        mode_col, pick_col = st.columns([3, 5])
        # One widget per language: a selectbox may keep showing its old
        # label after a language switch. "cmp_mode" holds the choice.
        key = f"cmp_mode_{lang()}"
        draft = st.session_state.get("cmp_mode")
        st.session_state[key] = draft
        mode_col.selectbox(
            t("compare.mode"),
            MODES,
            format_func=lambda v: t(f"compare.mode.{v}"),
            key=key,
            placeholder=t("compare.choose"),
            on_change=lambda: st.session_state.update(cmp_mode=st.session_state[key]),
            help=t("compare.help"),
        )
        if authors:
            with pick_col:
                _pickers(draft, novels, authors)
        pending = _draft() != _applied()
        mode_col.button(
            t("compare.run"),
            key="cmp_run",
            type="primary",
            icon=":material/play_arrow:",
            disabled=draft is None or not pending,
            on_click=lambda: st.session_state.update(cmp_applied=_draft()),
            width="stretch",
        )
        if mode() and pending:
            mode_col.caption(t("compare.pending"))


def _pickers(draft: str | None, novels: pd.DataFrame, authors: list[str]) -> None:
    """The authors or novels the drafted comparison needs, side by side."""
    first, second = st.columns(2, vertical_alignment="bottom")
    if draft == "authors":
        _keep_valid("cmp_author_a", authors, authors[0])
        _keep_valid("cmp_author_b", authors, authors[min(1, len(authors) - 1)])
        first.selectbox(t("compare.author_a"), authors, key="cmp_author_a")
        second.selectbox(t("compare.author_b"), authors, key="cmp_author_b")
    elif draft in ("rest", "novels"):
        _keep_valid("cmp_author", authors, authors[0])
        first.selectbox(t("compare.author"), authors, key="cmp_author")
    if draft == "novels":
        own = novels[novels["author"] == st.session_state["cmp_author"]]
        ids = own.sort_values("year")["novel_id"].tolist()
        chosen = [i for i in st.session_state.get("cmp_novels", []) if i in ids]
        if not chosen:
            top = own.nlargest(MAX_NOVELS, "n_emotion")["novel_id"]
            chosen = [i for i in ids if i in set(top)]
        st.session_state["cmp_novels"] = chosen
        titles = filters.novel_titles()
        second.multiselect(
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
    m, a = mode(), _applied()
    if m is None:
        return []
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
        names = dict.fromkeys([a.get("cmp_author_a"), a.get("cmp_author_b")])
        found = [
            Group(
                a,
                a,
                charts.group_color(i),
                frozenset(novels.loc[novels["author"] == a, "novel_id"]),
            )
            for i, a in enumerate(n for n in names if n)
        ]
    elif m == "rest":
        # By exact name: a namesake (another Cankar) falls into the rest.
        author = a.get("cmp_author")
        own = novels["author"] == author
        found = [
            Group(
                key,
                name,
                charts.group_color(i),
                frozenset(novels.loc[mask, "novel_id"]),
            )
            for i, (key, name, mask) in enumerate(
                [("author", author, own), ("rest", t("compare.rest"), ~own)]
            )
        ]
    else:
        chosen = novels.set_index("novel_id").reindex(a.get("cmp_novels") or [])
        found = [
            Group(nid, _short_title(row), charts.group_color(i), frozenset([nid]))
            for i, (nid, row) in enumerate(chosen.dropna(subset=["title"]).iterrows())
        ]
    return [g for g in found if g.novel_ids]


def is_split() -> bool:
    """Whether the groups are different novels (not the shame mode)."""
    return mode() != "shame"


def novel_groups() -> pd.Series:
    """Group label by novel_id; without a split, every novel gets the first group."""
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
    """The groups, or a prompt, a warning and a stop when there are none or
    too few."""
    picker()
    if mode() is None:
        st.info(t("compare.start"), icon=":material/arrow_upward:")
        st.stop()
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
    """With against without shame: one panel per set, each with its own scale."""
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


def set_of(group_label: str) -> str:
    """The excerpt set behind a group."""
    return next((g.set_name for g in groups() if g.label == group_label), "emotion")
