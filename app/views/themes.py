"""The themes of the passages with and without shame."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from helpers import charts, compare, filters, notes, reader, stats, tables
from helpers.language import num, t

N_FINDINGS = 3
# Words on each side of the two-theme chart.
N_PAIR_WORDS = 15

st.title(t("themes.title"))
st.write(t("themes.intro"))
filters.stop_if_empty()
groups = compare.require()
findings_box = st.container()

top_words = tables.table("themes")
# Names and descriptions written once by an AI model; `tests/test_themes.py`
# fails when a refit changes the themes they were written for.
theme_ids = sorted(top_words["theme"].unique())
names = pd.Series({i: t(f"themes.name.{i}") for i in theme_ids}).rename_axis("theme")
about = pd.Series({i: t(f"themes.about.{i}") for i in theme_ids})
main = tables.table("theme_paragraphs")
pool_ids = frozenset().union(*(g.novel_ids for g in groups))
split = compare.is_split()


def shares(novel_ids, set_name: str) -> pd.Series:
    """Share of the paragraphs of a set whose main theme is each theme."""
    rows = main[(main["set"] == set_name) & main["novel_id"].isin(novel_ids)]
    counts = rows["theme"].value_counts().reindex(names.index, fill_value=0)
    return counts / max(counts.sum(), 1)


def ratio_in(novel_ids) -> pd.Series:
    """How many times as common each theme is with shame as without."""
    ratio = shares(novel_ids, "emotion") / shares(novel_ids, "comparison")
    return ratio.replace(float("inf"), float("nan"))


ratio = ratio_in(pool_ids)
order = names.reindex(ratio.sort_values(ascending=False).index).tolist()
y = alt.Y("name:N", sort=order, title=None, axis=alt.Axis(labelLimit=300))
pick = alt.selection_point(name="theme", fields=["theme", "set", "group"], on="click")
tooltip = [
    alt.Tooltip("name:N", title=t("themes.col.theme")),
    alt.Tooltip("about:N", title=t("themes.col.about")),
    alt.Tooltip("words:N", title=t("themes.col.words")),
    alt.Tooltip("group:N", title=t("field.group")),
]
all_words = top_words.groupby("theme")["word"].agg(", ".join)
if split:
    # Each group against its own passages without shame.
    df = (
        pd.concat(
            ratio_in(g.novel_ids).rename("ratio").reset_index().assign(group=g.label)
            for g in groups
        )
        .dropna(subset=["ratio"])
        .assign(set="emotion")
    )
    x = alt.X(
        "ratio:Q", title=t("themes.col.ratio"), scale=alt.Scale(type="log", nice=False)
    )
    marks = [
        alt.Chart(pd.DataFrame({"one": [1.0]}))
        .mark_rule(strokeDash=[4, 3], color=charts.ink(), opacity=0.6)
        .encode(x=alt.X("one:Q", scale=alt.Scale(type="log"))),
    ]
    tooltip.append(alt.Tooltip("ratio:Q", title=t("themes.col.ratio"), format=".2f"))
    color = compare.color()
    read_key = "themes.read.split"
else:
    series = [
        (s, t(f"set.{s}"), charts.set_color(s)) for s in ("emotion", "comparison")
    ]
    df = pd.concat(
        shares(pool_ids, s).rename("share").reset_index().assign(group=label, set=s)
        for s, label, _ in series
    )
    x = alt.X("share:Q", title=t("themes.x"), axis=alt.Axis(format="%"))
    marks = []
    tooltip.append(alt.Tooltip("share:Q", title=t("themes.x"), format=".1%"))
    color = alt.Color(
        "group:N",
        scale=alt.Scale(domain=[s[1] for s in series], range=[s[2] for s in series]),
        legend=alt.Legend(title=None),
    )
    read_key = "themes.read"
df = df.assign(
    name=df["theme"].map(names),
    about=df["theme"].map(about),
    words=df["theme"].map(all_words),
)
field = "ratio" if split else "share"
spread = (
    alt.Chart(df)
    .mark_rule(color=charts.ink(), opacity=0.4)
    .encode(y=y, x=f"min({field}):Q", x2=f"max({field}):Q")
)
dots = (
    alt.Chart(df)
    .mark_point(filled=True, size=100, strokeWidth=0)
    .encode(
        y=y,
        x=x,
        color=color,
        opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
        tooltip=tooltip,
    )
    .add_params(pick)
)
chart = alt.layer(*marks, spread, dots).properties(height=24 * len(order) + 60)
event = charts.show_chart(chart, key="themes_chart")
st.caption(t(read_key))


def listing(ratios: pd.Series, themes) -> str:
    return "; ".join(f"*{names[i]}* ({num(ratios[i])}×)" for i in themes)


def finding_lines() -> list[str]:
    if not split:
        ranked = ratio.dropna().sort_values(ascending=False)
        if len(ranked) <= 2 * N_FINDINGS:
            return []
        return [
            t("themes.find.with", themes=listing(ranked, ranked.index[:N_FINDINGS])),
            t(
                "themes.find.without",
                themes=listing(1 / ranked, ranked.index[::-1][:N_FINDINGS]),
            ),
        ]
    lines = []
    for g in groups:
        ranked = ratio_in(g.novel_ids).dropna().sort_values(ascending=False)
        if len(ranked) > N_FINDINGS:
            lines.append(
                t(
                    "themes.find.group",
                    group=g.label,
                    themes=listing(ranked, ranked.index[:N_FINDINGS]),
                )
            )
    return lines


with findings_box:
    notes.findings(finding_lines())

points = (event.selection.get("theme") if event else None) or []
if points:
    p = points[0]
    theme, set_name = int(p["theme"]), p.get("set", "emotion")
    ids = next((g.novel_ids for g in groups if g.label == p.get("group")), pool_ids)
    rows = main[
        (main["theme"] == theme)
        & (main["set"] == set_name)
        & main["novel_id"].isin(ids)
    ]
    reader.show_excerpts(
        tables.ranked_excerpts(
            set_name,
            rows[["novel_id", "para_id", "weight"]].rename(columns={"weight": "value"}),
        ),
        key="themes_reader",
        title=t("themes.selected", theme=names[theme]),
    )
else:
    st.info(t("reader.empty"))


def pair_words(a: int, b: int) -> pd.DataFrame:
    """The words that set theme a apart from theme b in the passages with
    shame, and the reverse; `x` is log2 of how many times as often."""
    counts = tables.table("theme_words")
    counts = counts[counts["novel_id"].isin(pool_ids) & counts["theme"].isin([a, b])]
    counts = counts.assign(side=np.where(counts["theme"] == a, "emotion", "comparison"))
    authors = tables.novels().set_index("novel_id")["author"]
    table = stats.word_table(counts, tables.word_prior()["n_corpus"], authors)
    if table.empty:
        return table
    return pd.concat(
        [
            table[table["z"] > 0].nlargest(N_PAIR_WORDS, "z").assign(theme=names[a]),
            table[table["z"] < 0].nsmallest(N_PAIR_WORDS, "z").assign(theme=names[b]),
        ]
    ).assign(x=lambda d: np.log2(d["ratio"]), times=lambda d: 2 ** d["x"].abs())


st.subheader(t("themes.pair"))
st.write(t("themes.pair.lead"))
by_ratio = ratio.sort_values(ascending=False).index.tolist()
c1, c2 = st.columns(2)
theme_a = c1.selectbox(
    t("themes.pair.a"), by_ratio, format_func=names.get, key="themes_a"
)
theme_b = c2.selectbox(
    t("themes.pair.b"),
    [i for i in by_ratio if i != theme_a],
    format_func=names.get,
    key="themes_b",
)
pair = pair_words(theme_a, theme_b)
if pair.empty:
    st.info(t("reader.none"))
else:
    pick_word = alt.selection_point(name="pair_word", fields=["word"], on="click")
    chart = (
        alt.Chart(pair)
        .mark_bar(height=14, cornerRadiusEnd=3)
        .encode(
            y=alt.Y("word:N", sort="-x", title=None),
            x=alt.X(
                "x:Q",
                title=t("themes.pair.x"),
                axis=alt.Axis(
                    tickMinStep=1,
                    labelExpr="format(pow(2, abs(datum.value)), '.0f') + '×'",
                ),
            ),
            color=alt.Color(
                "theme:N",
                scale=alt.Scale(
                    domain=[names[theme_a], names[theme_b]],
                    range=[charts.group_color(0), charts.group_color(1)],
                ),
                legend=alt.Legend(title=None),
            ),
            opacity=alt.condition(pick_word, alt.value(1), alt.value(0.5)),
            tooltip=[
                alt.Tooltip("word:N", title=t("words.col.word")),
                alt.Tooltip("theme:N", title=t("themes.col.theme")),
                alt.Tooltip("times:Q", title=t("themes.pair.times"), format=".1f"),
                alt.Tooltip("n_novels:Q", title=t("words.col.n_novels")),
            ],
        )
        .add_params(pick_word)
        .properties(height=18 * len(pair) + 80)
    )
    word = (
        charts.selected(
            charts.show_chart(chart, key="themes_pair"), "pair_word", "word"
        )
        or [None]
    )[0]
    st.caption(t("themes.pair.read"))
    if word:
        theme = theme_a if word in set(pair.loc[pair["x"] > 0, "word"]) else theme_b
        rows = main[
            (main["theme"] == theme)
            & (main["set"] == "emotion")
            & main["novel_id"].isin(pool_ids)
        ]
        in_theme = tables.ranked_excerpts(
            "emotion",
            rows[["novel_id", "para_id", "weight"]].rename(columns={"weight": "value"}),
        )
        with_word, forms = tables.excerpts_with(word, "emotion", pool_ids)
        reader.show_excerpts(
            in_theme[in_theme["excerpt_id"].isin(with_word["excerpt_id"])],
            key="themes_pair_reader",
            title=t("themes.pair.selected", word=word, theme=names[theme]),
            highlight_words=forms,
        )

meta = tables.meta()["themes"]
notes.methodology(
    "themes",
    n=meta["n_themes"],
    min_paragraphs=meta["min_paragraphs"],
    max_share=round(meta["max_share"] * 100),
    n_pair=N_PAIR_WORDS,
)
with st.expander(t("themes.words")):
    st.dataframe(
        pd.DataFrame(
            {
                t("themes.col.theme"): names,
                t("themes.col.about"): about,
                t("themes.col.words"): all_words,
            }
        ).reindex(by_ratio),
        hide_index=True,
    )
