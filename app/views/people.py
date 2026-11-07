"""Who appears in the passages with shame: who acts, and which names."""

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
        if not n.sum():
            continue
        row = f"{g.label} · {t(f'set.{side}')}" if split else t(f"set.{side}")
        for subject in ("Fem", "Masc"):
            rows.append(
                {
                    "group": g.label,
                    "side": side,
                    "row": row,
                    "subject": t(f"people.subject.{subject}"),
                    "share": n.get(subject, 0) / n.sum(),
                    "n": int(n.sum()),
                }
            )
acts = pd.DataFrame(rows)
st.subheader(t("people.acts"))
st.write(t("people.acts.lead"))
if acts.empty:
    st.info(t("reader.none"))
else:
    # One bar per set, split into women and men; two shades of the accent,
    # since grey and the group colours already mean something else.
    subjects_order = [t("people.subject.Fem"), t("people.subject.Masc")]
    women = acts[acts["subject"] == subjects_order[0]].set_index("row")["share"]
    acts = acts.assign(edge=acts["row"].map(women))
    y = alt.Y(
        "row:N",
        sort=list(dict.fromkeys(acts["row"])),
        title=None,
        axis=alt.Axis(labelLimit=300),
    )
    bars = (
        alt.Chart(acts)
        .mark_bar(height=26)
        .encode(
            y=y,
            x=alt.X(
                "share:Q",
                stack="normalize",
                title=t("people.acts_x"),
                axis=alt.Axis(format="%"),
            ),
            order=alt.Order("subject_rank:Q"),
            color=alt.Color(
                "subject:N",
                scale=alt.Scale(domain=subjects_order, range=charts.two_shades()),
                legend=alt.Legend(title=None),
            ),
            tooltip=[
                alt.Tooltip("row:N", title=t("people.col.set")),
                alt.Tooltip("subject:N", title=t("people.col.subject")),
                alt.Tooltip("share:Q", title=t("people.acts_x"), format=".0%"),
                alt.Tooltip("n:Q", title=t("people.col.n")),
            ],
        )
        .transform_calculate(subject_rank=f"indexof({subjects_order!r}, datum.subject)")
    )
    # Both shares sit at the border between the two parts, one on each side.
    labels = [
        alt.Chart(acts)
        .transform_filter(alt.datum.subject == subject)
        .mark_text(align=align, dx=dx, color="white", fontWeight=600)
        .encode(y=y, x="edge:Q", text=alt.Text("share:Q", format=".0%"))
        for subject, align, dx in zip(
            subjects_order, ("right", "left"), (-6, 6), strict=True
        )
    ]
    # Room for the legend and the axis, which the height includes.
    chart = alt.layer(bars, *labels).properties(height=44 * acts["row"].nunique() + 100)
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
st.write(t("people.names.lead"))
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
        women = part[part["subject"] == t("people.subject.Fem")]
        share = women.set_index("side")["share"]
        if len(share) == 2:
            lines.append(
                t(
                    "people.find.acts",
                    group=label,
                    with_=num(share["emotion"] * 100, 0),
                    without=num(share["comparison"] * 100, 0),
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
