"""AN-10: the themes of the passages with and without shame."""

import altair as alt
import pandas as pd
import streamlit as st

from helpers import charts, compare, filters, notes, reader, tables
from helpers.language import num, t

N_LABEL_WORDS = 4
N_FINDINGS = 3

f = filters.current()
st.title(t("themes.title"))
st.write(t("themes.intro"))
filters.stop_if_empty()
groups = compare.require()
findings_box = st.container()

top_words = tables.table("themes")
names = (
    top_words[top_words["rank"] < N_LABEL_WORDS]
    .groupby("theme")["word"]
    .agg(" · ".join)
)
main = tables.table("theme_paragraphs")
if f.tier == "core":
    main = main[main["core"]]
pool_ids = frozenset().union(*(g.novel_ids for g in groups))
with_, without = (
    compare.Group(s, t(f"set.{s}"), charts.set_color(s), pool_ids, s)
    for s in ("emotion", "comparison")
)
# Each group's passages with shame, against all compared passages without.
series = [*(groups if compare.is_split() else [with_]), without]


def shares(g: compare.Group) -> pd.Series:
    """Share of the group's paragraphs whose main theme is each theme."""
    rows = main[(main["set"] == g.set_name) & main["novel_id"].isin(g.novel_ids)]
    counts = rows["theme"].value_counts().reindex(names.index, fill_value=0)
    return counts / max(counts.sum(), 1)


df = pd.concat(
    shares(g).rename("share").reset_index().assign(group=g.label, set=g.set_name)
    for g in series
)
ratio = (shares(with_) / shares(without)).replace(float("inf"), float("nan"))
df = df.assign(name=df["theme"].map(names), ratio=df["theme"].map(ratio))
order = names.reindex(ratio.sort_values(ascending=False).index).tolist()

pick = alt.selection_point(name="theme", fields=["theme", "set"], on="click")
y = alt.Y("name:N", sort=order, title=None, axis=alt.Axis(labelLimit=300))
rule = (
    alt.Chart(df)
    .mark_rule(color=charts.ink(), opacity=0.4)
    .encode(y=y, x="min(share):Q", x2="max(share):Q")
)
dots = (
    alt.Chart(df)
    .mark_point(filled=True, size=100, strokeWidth=0)
    .encode(
        y=y,
        x=alt.X("share:Q", title=t("themes.x"), axis=alt.Axis(format="%")),
        color=alt.Color(
            "group:N",
            scale=alt.Scale(
                domain=[g.label for g in series], range=[g.color for g in series]
            ),
            legend=alt.Legend(title=None),
        ),
        opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
        tooltip=[
            alt.Tooltip("name:N", title=t("themes.col.theme")),
            alt.Tooltip("group:N", title=t("field.group")),
            alt.Tooltip("share:Q", title=t("themes.x"), format=".1%"),
            alt.Tooltip("ratio:Q", title=t("themes.col.ratio"), format=".2f"),
        ],
    )
    .add_params(pick)
)
chart = alt.layer(rule, dots).properties(height=24 * len(order) + 60)
event = charts.show_chart(chart, key="themes_chart")
st.caption(t("themes.read"))
meta = tables.meta()["themes"]
notes.methodology(
    "themes",
    n=meta["n_themes"],
    min_paragraphs=meta["min_paragraphs"],
    max_share=round(meta["max_share"] * 100),
)
with st.expander(t("themes.words")):
    st.dataframe(
        top_words.groupby("theme")["word"]
        .agg(", ".join)
        .reindex(ratio.sort_values(ascending=False).index)
        .rename(t("themes.col.words"))
        .reset_index(drop=True),
        hide_index=True,
    )


def listing(themes: pd.Index) -> str:
    return "; ".join(f"*{names[i]}* ({num(ratio[i])}×)" for i in themes)


ranked = ratio.dropna().sort_values(ascending=False)
with findings_box:
    notes.findings(
        [
            t("themes.find.with", themes=listing(ranked.index[:N_FINDINGS])),
            t("themes.find.without", themes=listing(ranked.index[::-1][:N_FINDINGS])),
        ]
        if len(ranked) > 2 * N_FINDINGS
        else []
    )

points = charts.selected(event, "theme", "theme")
if points:
    theme = int(points[0])
    set_name = (charts.selected(event, "theme", "set") or ["emotion"])[0]
    rows = main[
        (main["theme"] == theme)
        & (main["set"] == set_name)
        & main["novel_id"].isin(pool_ids)
    ]
    reader.show_excerpts(
        tables.ranked_excerpts(
            f.tier if set_name == "emotion" else "comparison",
            rows[["novel_id", "para_id", "weight"]].rename(columns={"weight": "value"}),
        ),
        key="themes_reader",
        title=t("themes.selected", theme=names[theme]),
    )
else:
    st.info(t("reader.empty"))
