"""AN-01: detected shame per novel against the year of publication.

Six chart types answer the same question in different ways: every novel
(scatter), the trend (moving average), the spread per decade (box plots),
authors, the novels with most shame (ranked bars) and the groups side by
side. Every chart draws the groups of the comparison set in the sidebar.
"""

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

CHART_TYPES = ("scatter", "trend", "decades", "authors", "top", "groups")
WINDOW = 10
MIN_IN_WINDOW = 3
# Loess lines need this many novels in a group.
MIN_FOR_TREND = 10
# Rank correlations weaker than this are reported as no clear trend.
CLEAR_TREND = 0.2
# Height per row of the charts with one row per author or novel, in pixels.
ROW = 22

f = filters.current()
st.title(t("time.title"))
st.write(t("time.intro"))
filters.stop_if_empty()
groups = compare.require()
shame_mode = compare.mode() == "shame"
findings_box = st.container()

measures = ["share", "per_10k_words"] + ([] if shame_mode else ["mean_score"])
if st.session_state.get("time_metric") not in measures:
    st.session_state["time_metric"] = "share"
c1, c2 = st.columns([2, 3])
chart_type = c1.selectbox(
    t("chart.type"),
    CHART_TYPES,
    format_func=lambda v: t(f"time.type.{v}"),
    key="time_type",
)
measure = c2.segmented_control(
    t("time.metric"),
    measures,
    required=True,
    format_func=lambda v: t(f"time.metric.{v}"),
    key="time_metric",
)
with st.expander(t("time.measures_help_title")):
    st.markdown(t("time.measures_help"))


def value_column(set_name: str) -> tuple[str, float]:
    """The novels column of the measure for one set, and its display factor."""
    counted = f.tier if set_name == "emotion" else "low"
    return {
        "share": (f"share_{counted}", 100),
        "per_10k_words": (f"per_10k_words_{counted}", 1),
        "mean_score": ("mean_score", 100),
    }[measure]


y_title = t(f"time.axis.{measure}")
selected = filters.filtered_novels().assign(
    novel_label=lambda d: (
        d["author"] + ": " + d["title"] + " (" + d["year"].astype(str) + ")"
    )
)
if shame_mode:
    # The same novels twice: once counting the passages with shame, once
    # those clearly without.
    frames = []
    for g in groups:
        column, factor = value_column(g.set_name)
        counted = f.tier if g.set_name == "emotion" else "low"
        frames.append(
            selected.assign(
                group=g.label,
                value=selected[column] * factor,
                tagged=selected[f"n_{counted}"],
            )
        )
    novels = pd.concat(frames, ignore_index=True)
else:
    column, factor = value_column("emotion")
    novels = compare.with_group(selected).assign(
        value=lambda d: d[column] * factor, tagged=lambda d: d[f"n_{f.tier}"]
    )
novels = novels.assign(group_size=novels.groupby("group")["novel_id"].transform("size"))
first, last = int(novels["year"].min()), int(novels["year"].max())
x_year = alt.X(
    "year:Q",
    title=t("time.x"),
    scale=alt.Scale(domain=[first - 2, last + 2], nice=False),
    axis=alt.Axis(format="d"),
)
color = compare.color()
novel_tooltip = [
    alt.Tooltip("novel_label:N", title=t("field.novel")),
    alt.Tooltip("group:N", title=t("field.group")),
    alt.Tooltip("n_paragraphs:Q", title=t("field.paragraphs"), format=","),
    alt.Tooltip("tagged:Q", title=t("field.counted"), format=","),
    alt.Tooltip("value:Q", title=y_title, format=".1f"),
]
pick_novel = alt.selection_point(
    name="novel", fields=["novel_id", "group"], on="click", toggle="event.shiftKey"
)


def novel_points(data=alt.Undefined, **encodings) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_point(filled=True, size=60, strokeWidth=0)
        .encode(
            color=color,
            opacity=alt.condition(pick_novel, alt.value(0.85), alt.value(0.2)),
            tooltip=novel_tooltip,
            **encodings,
        )
        .add_params(pick_novel)
    )


def chosen_from(event, param: str = "novel") -> list[tuple[str, str]]:
    """(novel_id, group) pairs of the clicked marks."""
    points = (event.selection.get(param) if event else None) or []
    return [(p["novel_id"], p["group"]) for p in points if "novel_id" in p]


chosen: list[tuple[str, str]] = []

if chart_type == "scatter":
    trend = st.toggle(t("time.trend"), value=True, key="time_trend")
    y = alt.Y("value:Q", title=y_title, scale=alt.Scale(domainMin=0, clamp=True))
    layers = [novel_points(x=x_year, y=y)]
    if trend:
        layers.append(
            alt.Chart()
            .transform_filter(f"datum.group_size >= {MIN_FOR_TREND}")
            .transform_loess("year", "value", groupby=["group"], bandwidth=0.5)
            .mark_line(strokeWidth=2.5)
            .encode(x="year:Q", y="value:Q", color=color, detail="group:N")
        )
    chart = compare.panels(alt.layer(*layers, data=novels).properties(height=380))
    chosen = chosen_from(charts.show_chart(chart, key="time_scatter"))

elif chart_type == "trend":
    ma = stats.moving_average(novels, first, last, WINDOW, MIN_IN_WINDOW)
    if ma.empty:
        st.info(t("time.trend_too_few", n=MIN_IN_WINDOW, window=WINDOW))
        st.stop()
    pick_year = alt.selection_point(
        name="year", fields=["year", "group"], on="click", empty=False
    )
    band = (
        alt.Chart()
        .mark_area(opacity=0.18)
        .encode(
            x=x_year,
            y=alt.Y("low:Q", title=y_title, scale=alt.Scale(domainMin=0)),
            y2="high:Q",
            color=compare.color(),
            detail="segment:N",
        )
    )
    line = (
        alt.Chart()
        .mark_line(strokeWidth=2.5)
        .encode(x=x_year, y="mean:Q", color=color, detail="segment:N")
    )
    # Invisible until clicked: the points only carry tooltips and clicks.
    dots = (
        alt.Chart()
        .mark_point(filled=True, size=90)
        .encode(
            x=x_year,
            y="mean:Q",
            color=color,
            opacity=alt.condition(pick_year, alt.value(0.9), alt.value(0.01)),
            tooltip=[
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("year:Q", title=t("time.window_centre")),
                alt.Tooltip("mean:Q", title=y_title, format=".1f"),
                alt.Tooltip("n:Q", title=t("field.novels")),
            ],
        )
        .add_params(pick_year)
    )
    chart = compare.panels(alt.layer(band, line, dots, data=ma).properties(height=380))
    event = charts.show_chart(chart, key="time_trend_chart")
    points = (event.selection.get("year") if event else None) or []
    if points:
        p = points[0]
        window = novels[
            (novels["group"] == p["group"])
            & novels["year"].between(p["year"] - WINDOW / 2, p["year"] + WINDOW / 2 - 1)
        ]
        chosen = [(n, p["group"]) for n in window["novel_id"]]

elif chart_type == "decades":
    decades = novels.assign(decade=(novels["year"] // 10 * 10).astype(str) + "s")
    x = alt.X("decade:O", title=t("time.decade"))
    y = alt.Y("value:Q", title=y_title)
    boxes = (
        alt.Chart()
        .mark_boxplot(size=16, extent=1.5, opacity=0.5, median={"color": charts.ink()})
        .encode(
            x=x, y=y, color=color, xOffset=alt.XOffset("group:N", sort=compare.order())
        )
    )
    dots = novel_points(
        x=x, y=y, xOffset=alt.XOffset("group:N", sort=compare.order())
    ).mark_point(filled=True, size=20, strokeWidth=0)
    chart = compare.panels(alt.layer(boxes, dots, data=decades).properties(height=380))
    chosen = chosen_from(charts.show_chart(chart, key="time_decades"))

elif chart_type == "authors":
    min_novels = st.slider(t("time.min_novels"), 1, 10, 5, key="time_min_novels")
    counts = selected.groupby("author")["novel_id"].size()
    keep = counts[counts >= min_novels]
    shown = novels[novels["author"].isin(keep.index)].assign(
        author_label=lambda d: (
            d["author"] + " (" + d["author"].map(keep).astype(str) + ")"
        )
    )
    if shown.empty:
        st.info(t("reader.none"))
        st.stop()
    first_group = shown[shown["group"] == shown["group"].iloc[0]]
    author_order = (
        first_group.groupby("author_label")["value"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    y = alt.Y(
        "author_label:N",
        sort=author_order,
        title=None,
        axis=alt.Axis(labelOverlap=False, labelLimit=240),
    )
    x = alt.X("value:Q", title=y_title)
    medians = shown.groupby(["group", "author_label"], as_index=False)["value"].median()
    ticks = (
        alt.Chart(medians)
        .mark_tick(thickness=2, size=14, color=charts.ink())
        .encode(
            y=y,
            x="value:Q",
            tooltip=[alt.Tooltip("value:Q", title=t("time.median"), format=".1f")],
        )
    )
    points = novel_points(shown, x=x, y=y)
    # Layers with their own data cannot be faceted, so the shame mode draws
    # its two panels side by side by hand.
    if shame_mode:
        panes = [
            alt.layer(
                ticks.transform_filter(alt.datum.group == g.label),
                points.transform_filter(alt.datum.group == g.label),
            ).properties(title=g.label, width=300, height=ROW * len(author_order) + 80)
            for g in groups
        ]
        chart = alt.hconcat(*panes).resolve_scale(x="independent")
    else:
        chart = alt.layer(ticks, points).properties(height=ROW * len(author_order) + 80)
    chosen = chosen_from(charts.show_chart(chart, key="time_authors"))

elif chart_type == "top":
    n_top = st.slider(t("time.n_top"), 10, 40, 15, step=5, key="time_n_top")
    if shame_mode:
        st.caption(t("time.top_shame_only"))
    top = novels[novels["group"] == groups[0].label].nlargest(n_top, "value")
    y = alt.Y(
        "novel_label:N",
        sort="-x",
        title=None,
        axis=alt.Axis(labelOverlap=False, labelLimit=340),
    )
    bars = (
        alt.Chart(top)
        .mark_bar(cornerRadiusEnd=4, height=13)
        .encode(
            y=y,
            x=alt.X("value:Q", title=y_title),
            color=color,
            opacity=alt.condition(pick_novel, alt.value(1), alt.value(0.35)),
            tooltip=novel_tooltip,
        )
        .add_params(pick_novel)
        .properties(height=ROW * len(top) + 60)
    )
    chosen = chosen_from(charts.show_chart(bars, key="time_top"))

else:  # groups
    sized = novels.assign(
        row=novels["group"] + " (" + novels["group_size"].astype(str) + ")"
    )
    rng = np.random.default_rng(0)
    sized["jitter"] = rng.uniform(-0.3, 0.3, len(sized))
    rows = sized.drop_duplicates("group").set_index("group")["row"]
    row_order = [rows[g] for g in compare.order() if g in rows]
    y = alt.Y(
        "row:N",
        sort=row_order,
        title=None,
        axis=alt.Axis(labelLimit=300, labelOverlap=False),
    )
    x = alt.X("value:Q", title=y_title)
    ticks = (
        alt.Chart()
        .transform_aggregate(value="median(value)", groupby=["row", "group"])
        .mark_tick(thickness=3, size=34, color=charts.ink())
        .encode(
            y=y,
            x="value:Q",
            tooltip=[alt.Tooltip("value:Q", title=t("time.median"), format=".1f")],
        )
    )
    dots = novel_points(
        x=x,
        y=y,
        yOffset=alt.YOffset("jitter:Q", scale=alt.Scale(domain=[-0.5, 0.5])),
    )
    height = 60 * (1 if shame_mode else len(row_order)) + 30
    chart = compare.panels(
        alt.layer(ticks, dots, data=sized).properties(height=height), axis="x"
    )
    if shame_mode:
        chart = chart.resolve_scale(y="independent")
    chosen = chosen_from(charts.show_chart(chart, key="time_groups"))

st.caption(t(f"time.read.{chart_type}", window=WINDOW, n=MIN_IN_WINDOW))
st.caption(t("time.descriptive"))
notes.methodology(
    "time",
    half=WINDOW // 2,
    n=MIN_IN_WINDOW,
    trend=MIN_FOR_TREND,
    clear=num(CLEAR_TREND),
)


def finding_lines() -> list[str]:
    unit = " %" if measure == "share" else ""
    lines = []
    medians = {}
    for g in groups:
        members = novels[novels["group"] == g.label]
        if members.empty:
            continue
        medians[g.label] = members["value"].median()
        rho = stats.rank_correlation(members["year"], members["value"])
        if np.isnan(rho) or abs(rho) < CLEAR_TREND:
            trend = t("time.find.flat")
        else:
            trend = t("time.find.rise" if rho > 0 else "time.find.fall")
        lines.append(
            t(
                "time.find.group",
                group=g.label,
                median=num(medians[g.label]) + unit,
                n=len(members),
                trend=trend,
                rho=num(rho, 2) if not np.isnan(rho) else "–",
            )
        )
    if compare.is_split() and len(medians) >= 2:
        (a, va), (b, vb) = sorted(medians.items(), key=lambda kv: -kv[1])[:2]
        if vb > 0:
            lines.append(t("time.find.ratio", a=a, b=b, x=num(va / vb)))
    top = novels[novels["group"] == groups[0].label].nlargest(1, "value")
    if not top.empty and not shame_mode:
        row = top.iloc[0]
        lines.append(
            t("time.find.top", novel=row["novel_label"], value=num(row["value"]) + unit)
        )
    return lines


with findings_box:
    notes.findings(finding_lines())

if chosen:
    frames = []
    for group_label, pairs in pd.DataFrame(chosen, columns=["novel", "group"]).groupby(
        "group"
    ):
        excerpts = tables.excerpts(compare.set_of(group_label, f.tier))
        frames.append(excerpts[excerpts["novel_id"].isin(pairs["novel"])])
    reader.show_excerpts(
        pd.concat(frames),
        key="time",
        title=t("time.selected", n=len({n for n, _ in chosen})),
    )
else:
    st.info(t("reader.empty"))
