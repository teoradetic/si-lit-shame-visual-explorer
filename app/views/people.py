"""AN-11: who appears in the passages with shame: who acts, and which names."""

import altair as alt
import pandas as pd
import streamlit as st

from helpers import charts, compare, filters, notes, reader, stats, tables
from helpers.language import num, t

N_NAMES = 15

f = filters.current()
st.title(t("people.title"))
st.write(t("people.intro"))
filters.stop_if_empty()
groups = compare.require()
split = compare.is_split()
findings_box = st.container()
pool_ids = frozenset().union(*(g.novel_ids for g in groups))
shown = (
    groups
    if split
    else [
        compare.Group(
            "all", t("compare.everyone"), charts.set_color("emotion"), pool_ids
        )
    ]
)

# Who acts: the gender of the subject of singular past-tense verbs.
subjects = tables.table("subjects")
subjects = subjects[subjects["tier"] == f.tier]
rows = []
for g in shown:
    for side in stats.SIDES:
        mine = subjects[
            (subjects["side"] == side) & subjects["novel_id"].isin(g.novel_ids)
        ]
        n = mine.groupby("subject", observed=True)["n"].sum()
        if n.sum():
            rows.append(
                {
                    "group": g.label,
                    "set": t(f"set.{side}"),
                    "share": n.get("Fem", 0) / n.sum(),
                    "n": int(n.sum()),
                }
            )
acts = pd.DataFrame(rows)
st.subheader(t("people.acts"))
if acts.empty:
    st.info(t("reader.none"))
else:
    y = alt.Y("group:N", sort=[g.label for g in shown], title=None)
    sets = [t("set.emotion"), t("set.comparison")]
    chart = alt.layer(
        alt.Chart(acts)
        .mark_rule(color=charts.ink(), opacity=0.5)
        .encode(y=y, x="min(share):Q", x2="max(share):Q"),
        alt.Chart(acts)
        .mark_point(filled=True, size=120, strokeWidth=0)
        .encode(
            y=y,
            x=alt.X("share:Q", title=t("people.acts_x"), axis=alt.Axis(format="%")),
            color=alt.Color(
                "set:N",
                scale=alt.Scale(
                    domain=sets,
                    range=[charts.set_color("emotion"), charts.set_color("comparison")],
                ),
                legend=alt.Legend(title=None),
            ),
            tooltip=[
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("set:N", title=t("people.col.set")),
                alt.Tooltip("share:Q", title=t("people.acts_x"), format=".1%"),
                alt.Tooltip("n:Q", title=t("people.col.n")),
            ],
        ),
    ).properties(height=40 * len(shown) + 60)
    charts.show_chart(chart, key="people_acts", select=False)
    st.caption(t("people.acts.read"))

# Names: those most typical of the passages with shame, per group.
counts = tables.table("name_counts")
counts = counts[counts["tier"] == f.tier].drop(columns="tier")
prior = tables.word_prior()["n_corpus"]
authors = tables.novels().set_index("novel_id")["author"]
tops = []
for g in shown:
    table = stats.word_table(
        counts[counts["novel_id"].isin(g.novel_ids)], prior, authors
    )
    if not table.empty:
        tops.append(table[table["z"] > 0].nlargest(N_NAMES, "z").assign(group=g.label))
names = pd.concat(tops) if tops else pd.DataFrame()
st.subheader(t("people.names"))
chosen = None
if names.empty:
    st.info(t("reader.none"))
else:
    pick = alt.selection_point(name="name", fields=["word"], on="click")
    order = names.groupby("word")["ratio"].max().sort_values(ascending=False).index
    chart = (
        alt.Chart(names)
        .mark_point(filled=True, size=100, strokeWidth=0)
        .encode(
            y=alt.Y("word:N", sort=order.tolist(), title=None),
            x=alt.X(
                "ratio:Q",
                title=t("words.col.ratio"),
                scale=alt.Scale(type="log", nice=False),
            ),
            color=alt.Color(
                "group:N",
                scale=alt.Scale(
                    domain=[g.label for g in shown], range=[g.color for g in shown]
                ),
                legend=alt.Legend(title=None) if split else None,
            ),
            opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
            tooltip=[
                alt.Tooltip("word:N", title=t("people.col.name")),
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("ratio:Q", title=t("words.col.ratio"), format=".2f"),
                alt.Tooltip("n_novels:Q", title=t("words.col.n_novels")),
            ],
        )
        .add_params(pick)
        .properties(height=22 * len(order) + 60)
    )
    event = charts.show_chart(chart, key="people_names")
    chosen = (charts.selected(event, "name", "word") or [None])[0]
    st.caption(t("people.names.read"))

notes.methodology("people", min_count=stats.MIN_COUNT)


def finding_lines() -> list[str]:
    lines = []
    for label, part in acts.groupby("group", sort=False) if not acts.empty else []:
        share = part.set_index("set")["share"]
        if len(share) == 2:
            lines.append(
                t(
                    "people.find.acts",
                    group=label,
                    with_=num(share[t("set.emotion")] * 100, 0),
                    without=num(share[t("set.comparison")] * 100, 0),
                )
            )
    if not names.empty:
        top = names.drop_duplicates("word").nlargest(5, "z")
        lines.append(
            t("people.find.names", names=", ".join(f"*{w}*" for w in top["word"]))
        )
    return lines


with findings_box:
    notes.findings(finding_lines())

if chosen:
    picked, forms = tables.excerpts_with(chosen, f.tier, pool_ids)
    reader.show_excerpts(
        picked,
        key="people_reader",
        title=t("words.selected", word=chosen),
        highlight_words=forms,
    )
else:
    st.info(t("reader.empty"))
