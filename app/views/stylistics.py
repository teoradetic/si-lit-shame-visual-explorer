"""AN-08 (basic): style of the detected passages against the comparison set.

Three chart types: every measure indexed so that passages without shame are
100, the raw values side by side in one small panel per measure, and one
measure over the years of publication. Each group of the comparison in the
sidebar is tested on its own (`stats.compare_novels`).
"""

import html

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import charts
import compare
import filters
import notes
import reader
import stats
import tables
from language import num, t

CHART_TYPES = ("index", "raw", "time")
# Over time: the same sliding window and trend threshold as on Over time.
WINDOW = 10
MIN_IN_WINDOW = 3
CLEAR_TREND = 0.2

# How each feature is read off one paragraph, to rank passages by it.
PARAGRAPH_VALUE = {
    "sentence_words": lambda d: d["n_words"] / d["n_sentences"],
    "mattr": None,
    "repetition": lambda d: d["n_repeats"] / d["n_eligible"].clip(lower=1),
    **{
        f"{name}_per_1k": (
            lambda d, n=name: d[f"n_{n}"] / d["n_chars"].clip(lower=1) * 1000
        )
        for name in (
            "exclamation",
            "question",
            "semicolon",
            "comma",
            "ellipsis",
            "dash",
        )
    },
}

f = filters.current()
st.title(t("style.title"))
st.write(t("style.intro"))
filters.stop_if_empty()
groups = compare.require()
split = compare.is_split()
findings_box = st.container()

c1, c2 = st.columns([2, 3])
chart_type = c1.selectbox(
    t("chart.type"),
    CHART_TYPES,
    format_func=lambda v: t(f"style.type.{v}"),
    key="style_type",
)
paragraph_split = c2.segmented_control(
    t("style.split"),
    ["all", "narration", "dialogue"],
    default="all",
    required=True,
    format_func=lambda v: t(f"paragraphs.{v}"),
    key="style_split",
)
if compare.mode() == "shame":
    st.caption(t("style.shame_mode"))
with st.expander(t("style.measures_title")):
    st.markdown(t("style.measures_help"))

features = tables.meta()["style"]["features"]
feature_labels = {feat: t(f"style.feature.{feat}") for feat in features}
if chart_type == "time":
    time_feature = st.selectbox(
        t("style.col.feature"),
        features,
        index=features.index("ellipsis_per_1k"),
        format_func=feature_labels.get,
        key="style_time_feature",
    )
order = [feature_labels[feat] for feat in features]
# Without a split, one group: every selected novel.
analysed = (
    groups
    if split
    else [
        compare.Group(
            "all",
            t("compare.everyone"),
            charts.set_color("emotion"),
            groups[0].novel_ids,
        )
    ]
)
tables_by_group = []
too_few = []
for g in analysed:
    table = tables.group_style(f.tier, paragraph_split, g.novel_ids, tuple(features))
    if table.empty:
        too_few.append(g.label)
    else:
        tables_by_group.append(table.assign(who=g.label))
if too_few:
    st.caption(
        t(
            "style.too_few",
            groups=", ".join(too_few),
            n=stats.MIN_NOVELS,
            p=stats.MIN_PARAGRAPHS,
        )
    )
if not tables_by_group:
    st.info(t("reader.none"))
    st.stop()
kept = [g for g in analysed if g.label not in too_few]
rows = pd.concat(tables_by_group, ignore_index=True).assign(
    feature_label=lambda d: d["feature"].map(feature_labels),
    index=lambda d: 100 * (1 + d["rel_diff"]),
    lo=lambda d: 100 * (1 + d["rel_ci_low"]),
    hi=lambda d: 100 * (1 + d["rel_ci_high"]),
    tested=lambda d: d["p_holm"] < 0.05,
    verdict=lambda d: d["p_holm"].map(
        lambda p: t("style.verdict.clear") if p < 0.05 else t("style.verdict.chance")
    ),
)
who_order = [g.label for g in kept]
color = alt.Color(
    "who:N",
    scale=alt.Scale(domain=who_order, range=[g.color for g in kept]),
    legend=alt.Legend(orient="top", title=None) if split else None,
)
select = alt.selection_point(name="feature", fields=["feature", "who"], on="click")

tooltip = [
    alt.Tooltip("feature_label:N", title=t("style.col.feature")),
    alt.Tooltip("who:N", title=t("field.group")),
    alt.Tooltip("mean_emotion:Q", title=t("style.col.mean_emotion"), format=".3f"),
    alt.Tooltip(
        "mean_comparison:Q", title=t("style.col.mean_comparison"), format=".3f"
    ),
    alt.Tooltip("index:Q", title=t("style.x"), format=".0f"),
    alt.Tooltip("verdict:N", title=t("style.col.verdict")),
    alt.Tooltip("n_novels:Q", title=t("style.col.n_novels")),
]

if chart_type == "index":
    # The legend is drawn by hand: Vega-Lite has no legend for a condition,
    # nor for marks of a fixed colour.
    ink = charts.ink()

    def dot(fill: str, border: str = ink) -> str:
        # Spans, not SVG: st.html strips inline SVG.
        return (
            '<span style="display:inline-block;width:0.75rem;height:0.75rem;'
            f"border-radius:50%;border:2px solid {border};background:{fill};"
            'vertical-align:-0.1rem;margin-right:0.35rem"></span>'
        )

    without = charts.set_color("comparison")
    items = [(dot(without, without), t("style.legend.without"))]
    if not split:
        shame = charts.set_color("emotion")
        items.append((dot(shame, shame), t("style.legend.with")))
    items += [
        (dot(ink), t("style.legend.filled")),
        (dot("transparent"), t("style.legend.hollow")),
    ]
    st.html(
        '<div class="reader-legend">'
        + "".join(f"<span>{d} {html.escape(text)}</span>" for d, text in items)
        + "</div>"
    )
    y = alt.Y(
        "feature_label:N",
        sort=order,
        title=None,
        axis=alt.Axis(labelFontSize=13, labelLimit=260, labelOverlap=False),
    )
    offset = alt.YOffset("who:N", sort=who_order)
    # Each row is a dumbbell: the passages without shame at 100 (grey), a
    # line to the passages with shame, and their 95 % interval.
    baseline = (
        alt.Chart(pd.DataFrame({"x": [100]}))
        .mark_rule(strokeWidth=1, strokeDash=[4, 3], color=without)
        .encode(x="x:Q")
    )
    reference = rows.assign(base=100.0)
    connector = (
        alt.Chart(reference)
        .mark_rule(strokeWidth=1, color=without)
        .encode(y=y, yOffset=offset, x="base:Q", x2="index:Q")
    )
    without_dots = (
        alt.Chart(reference)
        .mark_point(size=80, filled=True, color=without, opacity=1)
        .encode(
            y=y,
            yOffset=offset,
            x="base:Q",
            tooltip=[
                alt.Tooltip("feature_label:N", title=t("style.col.feature")),
                alt.Tooltip(
                    "mean_comparison:Q",
                    title=t("style.col.mean_comparison"),
                    format=".3f",
                ),
            ],
        )
    )
    ci = (
        alt.Chart(rows)
        .mark_rule(strokeWidth=2)
        .encode(
            y=y,
            yOffset=offset,
            x=alt.X("lo:Q", title=t("style.x")),
            x2="hi:Q",
            color=color,
        )
    )
    dots = (
        alt.Chart(rows)
        .mark_point(size=100, strokeWidth=2)
        .encode(
            y=y,
            yOffset=offset,
            x="index:Q",
            color=color,
            fill=alt.condition("datum.tested", color, alt.value("transparent")),
            opacity=alt.condition(select, alt.value(1), alt.value(0.35)),
            tooltip=tooltip,
        )
        .add_params(select)
    )
    chart = alt.layer(baseline, connector, without_dots, ci, dots).properties(
        height=(26 + 18 * len(kept)) * len(order)
    )
    event = charts.show_chart(chart, key="style_index")
    st.caption(t("style.read.index"))
elif chart_type == "time":
    style_novels = tables.table("style_novels")
    style_novels = style_novels[
        (style_novels["tier"] == f.tier) & (style_novels["split"] == paragraph_split)
    ]
    years = tables.novels().set_index("novel_id")["year"]
    set_labels = {"emotion": t("set.emotion"), "comparison": t("set.comparison")}
    frames = []
    for g in kept:
        df = style_novels[style_novels["novel_id"].isin(g.novel_ids)]
        # As in the comparison: both sets of a novel, each large enough.
        sizes = df.groupby("novel_id")["n_paragraphs"]
        enough = (sizes.transform("size") == 2) & (
            sizes.transform("min") >= stats.MIN_PARAGRAPHS
        )
        frames.append(df[enough].assign(who=g.label))
    values = pd.concat(frames, ignore_index=True)
    values = values.assign(
        year=values["novel_id"].map(years),
        value=values[time_feature],
        set_label=values["set"].astype(str).map(set_labels),
    )
    # One line per group and set.
    values["group"] = (
        values["who"] + " · " + values["set_label"] if split else values["set_label"]
    )
    series = values[["group", "who", "set_label"]].drop_duplicates()
    ma = stats.moving_average(
        values,
        int(values["year"].min()),
        int(values["year"].max()),
        WINDOW,
        MIN_IN_WINDOW,
    ).merge(series, on="group")
    if ma.empty:
        st.info(t("time.trend_too_few", n=MIN_IN_WINDOW, window=WINDOW))
        st.stop()
    y_title = feature_labels[time_feature]
    if time_feature.endswith("_per_1k"):
        y_title = t("style.per_1k", feature=y_title)
    set_order = list(set_labels.values())
    if split:
        line_color = color
        dash = alt.StrokeDash(
            "set_label:N",
            sort=set_order,
            scale=alt.Scale(domain=set_order, range=[[1, 0], [5, 4]]),
            legend=alt.Legend(orient="top", title=None),
        )
    else:
        line_color = alt.Color(
            "set_label:N",
            scale=alt.Scale(
                domain=set_order,
                range=[charts.set_color("emotion"), charts.set_color("comparison")],
            ),
            legend=alt.Legend(orient="top", title=None),
        )
        dash = alt.Undefined
    x_year = alt.X("year:Q", title=t("time.x"), axis=alt.Axis(format="d"))
    pick_year = alt.selection_point(
        name="year", fields=["year", "group"], on="click", empty=False
    )
    # Split, two bands per group would cover each other: only the passages
    # with shame get one.
    band = (
        alt.Chart()
        .transform_filter(
            alt.FieldEqualPredicate(field="set_label", equal=t("set.emotion"))
            if split
            else "true"
        )
        .mark_area(opacity=0.15)
        .encode(
            x=x_year,
            y=alt.Y("low:Q", title=y_title, scale=alt.Scale(domainMin=0)),
            y2="high:Q",
            color=line_color,
            detail="segment:N",
        )
    )
    line = (
        alt.Chart()
        .mark_line(strokeWidth=2.5)
        .encode(
            x=x_year, y="mean:Q", color=line_color, strokeDash=dash, detail="segment:N"
        )
    )
    # Invisible until clicked: the points only carry tooltips and clicks.
    dots = (
        alt.Chart()
        .mark_point(filled=True, size=90)
        .encode(
            x=x_year,
            y="mean:Q",
            color=line_color,
            opacity=alt.condition(pick_year, alt.value(0.9), alt.value(0.01)),
            tooltip=[
                alt.Tooltip("who:N", title=t("field.group")),
                alt.Tooltip("set_label:N", title=t("field.set")),
                alt.Tooltip("year:Q", title=t("time.window_centre")),
                alt.Tooltip("mean:Q", title=y_title, format=".2f"),
                alt.Tooltip("n:Q", title=t("field.novels")),
            ],
        )
        .add_params(pick_year)
    )
    chart = alt.layer(band, line, dots, data=ma).properties(height=380)
    event = charts.show_chart(chart, key="style_time")
    st.caption(
        t(
            "style.read.time_split" if split else "style.read.time",
            window=WINDOW,
            n=MIN_IN_WINDOW,
        )
    )
else:
    sets = pd.concat(
        [
            rows.assign(set=t("set.emotion"), value=rows["mean_emotion"]),
            rows.assign(set=t("set.comparison"), value=rows["mean_comparison"]),
        ]
    )
    set_order = [t("set.emotion"), t("set.comparison")]
    bars = (
        alt.Chart()
        .mark_bar(cornerRadiusEnd=4, size=14)
        .encode(
            x=alt.X(
                "who:N",
                sort=who_order,
                title=None,
                axis=alt.Axis(labelAngle=0, labels=split, ticks=False),
            ),
            xOffset=alt.XOffset("set:N", sort=set_order),
            y=alt.Y("value:Q", title=None),
            color=alt.Color(
                "set:N",
                scale=alt.Scale(
                    domain=set_order,
                    range=[
                        charts.set_color("emotion"),
                        charts.set_color("comparison"),
                    ],
                ),
                legend=alt.Legend(orient="top", title=None),
            ),
            opacity=alt.condition(select, alt.value(1), alt.value(0.35)),
            tooltip=tooltip,
        )
        .add_params(select)
        .properties(width=60 + 70 * len(kept), height=150)
    )
    chart = (
        alt.layer(bars, data=sets)
        .facet(
            facet=alt.Facet(
                "feature_label:N",
                sort=order,
                title=None,
                header=alt.Header(labelFontSize=13),
            ),
            columns=3,
        )
        .resolve_scale(y="independent")
    )
    event = charts.show_chart(chart, key="style_raw")
    st.caption(t("style.read.raw"))

st.caption(t("style.units") + " " + t("style.caveat"))
notes.methodology(
    "style",
    min_p=stats.MIN_PARAGRAPHS,
    min_n=stats.MIN_NOVELS,
    perms=num(stats.N_PERMUTATIONS, 0),
    boot=num(stats.N_BOOTSTRAP, 0),
    n_features=len(features),
    window=WINDOW,
    min_window=MIN_IN_WINDOW,
    clear=num(CLEAR_TREND, 1),
)


def finding_lines() -> list[str]:
    lines = []
    for who in who_order:
        clear = rows[(rows["who"] == who) & rows["tested"]].copy()
        if clear.empty:
            lines.append(t("style.find.none", group=who))
            continue
        clear["size"] = np.log(clear["index"] / 100).abs()
        parts = []
        for row in clear.nlargest(3, "size").itertuples():
            ratio = row.index / 100
            if ratio >= 1:
                parts.append(
                    t("style.find.more", feature=row.feature_label, x=num(ratio))
                )
            else:
                parts.append(
                    t(
                        "style.find.less",
                        feature=row.feature_label,
                        pct=round((1 - ratio) * 100),
                    )
                )
        lines.append(t("style.find.group", group=who, items="; ".join(parts)))
    if chart_type == "time":
        lines += time_finding_lines()
    return lines


def time_finding_lines() -> list[str]:
    """Whether the measure rises or falls with the year, with shame."""
    lines = []
    for who in who_order:
        own = values[(values["who"] == who) & (values["set"] == "emotion")]
        rho = stats.rank_correlation(own["year"], own["value"])
        if np.isnan(rho) or abs(rho) < CLEAR_TREND:
            trend = t("style.find.flat")
        else:
            trend = t("style.find.rise" if rho > 0 else "style.find.fall")
        lines.append(
            t(
                "style.find.time",
                group=who,
                feature=feature_labels[time_feature],
                trend=trend,
                rho=num(rho, 2) if not np.isnan(rho) else "–",
            )
        )
    return lines


with findings_box:
    notes.findings(finding_lines())

feature, ids = None, None
if chart_type == "time":
    points = (event.selection.get("year") if event else None) or []
    if points:
        # The novels behind the clicked point: its group, inside its window.
        p = points[0]
        who = series.loc[series["group"] == p["group"], "who"].iloc[0]
        inside = values[
            (values["who"] == who)
            & values["year"].between(p["year"] - WINDOW / 2, p["year"] + WINDOW / 2 - 1)
        ]
        feature, ids = time_feature, set(inside["novel_id"])
else:
    points = (event.selection.get("feature") if event else None) or []
    if points:
        who = points[0].get("who")
        feature = points[0].get("feature")
        ids = next((g.novel_ids for g in kept if g.label == who), kept[0].novel_ids)
if feature and PARAGRAPH_VALUE.get(feature):
    paragraphs = tables.table("style_paragraphs")
    paragraphs = paragraphs[
        (paragraphs["set"] == "emotion")
        & paragraphs[f.tier]
        & paragraphs["novel_id"].isin(ids)
    ]
    if paragraph_split == "narration":
        paragraphs = paragraphs[~paragraphs["dialogue"]]
    elif paragraph_split == "dialogue":
        paragraphs = paragraphs[paragraphs["dialogue"]]
    # Rank excerpts by their highest-scoring focus paragraph on this feature,
    # ignoring very short paragraphs, where rates are noisy.
    value = PARAGRAPH_VALUE[feature](paragraphs)
    ranked = paragraphs.assign(value=value)[paragraphs["n_words"] >= 20]
    top = ranked.nlargest(200, "value")[["novel_id", "para_id", "value"]]
    excerpts = tables.excerpts(f.tier)
    exploded = excerpts[["excerpt_id", "novel_id", "focus_ids"]].explode("focus_ids")
    exploded["para_id"] = exploded["focus_ids"].astype(int)
    hits = exploded.merge(top, on=["novel_id", "para_id"])
    best = hits.groupby("excerpt_id")["value"].max()
    picked = excerpts[excerpts["excerpt_id"].isin(best.index)].assign(
        rank=lambda d: d["excerpt_id"].map(best)
    )
    reader.show_excerpts(
        picked,
        key="style_reader",
        title=t("style.selected", feature=feature_labels[feature]),
    )
elif feature:
    st.info(t("style.no_paragraph"))
else:
    st.info(t("reader.empty"))
