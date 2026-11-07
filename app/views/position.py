"""Where in the novel the detected paragraphs fall (five chart types)."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from helpers import charts, compare, filters, notes, reader, stats, tables
from helpers.language import num, t

CHART_TYPES = (
    "concentration",
    "share",
    "violin",
    "heatmap",
    "heatmap_novels",
    "novels",
    "arcs",
)
# Novels with fewer counted paragraphs make the relative measure noisy.
MIN_TAGGED = 5
DEFAULT_ROWS = 30
ROW_HEIGHT = 18
# Wide enough to read, narrow enough to fit beside 300 px of labels.
STRIP_WIDTH = 480
# The line of each novel's share beside the strip.
SHARE_WIDTH = 160
GRID = np.linspace(0, 100, 51)
BANDWIDTH = 4.0
# The parts of the novel the findings compare: the first and last fifth.
FIFTH = 4

st.title(t("position.title"))
st.write(t("position.intro"))
st.info(t("position.explain"), icon=":material/menu_book:")
filters.stop_if_empty()
groups = compare.require()
shame_mode = compare.mode() == "shame"
split = compare.is_split()
rank = {g: i for i, g in enumerate(compare.order())}
findings_box = st.container()

chart_type = st.selectbox(
    t("chart.type"),
    CHART_TYPES,
    format_func=lambda v: t(f"position.type.{v}"),
    key="pos_type",
)

n_bins = tables.meta()["overview"]["n_position_bins"]
part = 100 / n_bins
novels = filters.filtered_novels()
novels = novels.assign(novel_label=novels["novel_id"].map(filters.novel_titles()))
bins = tables.table("position_bins")
bins = bins[bins["novel_id"].isin(set(novels["novel_id"]))].merge(
    novels[["novel_id", "novel_label", "year"]], on="novel_id"
)
# position_bin is int8: widen it before multiplying, or 15 * 100 wraps around.
position_bin = bins["position_bin"].astype(int)
bins = bins.assign(
    position_bin=position_bin,
    start=position_bin * part,
    mid=(position_bin + 0.5) * part,
)
if shame_mode:
    # Each novel twice: counting the detected paragraphs, and those with a
    # low score on every range.
    bins = pd.concat(
        [
            bins.assign(
                group=g.label,
                hits=bins["n_emotion" if g.set_name == "emotion" else "n_low"],
            )
            for g in groups
        ],
        ignore_index=True,
    )
else:
    bins = compare.with_group(bins).assign(hits=lambda d: d["n_emotion"])
x_position = alt.X(
    "mid:Q",
    title=t("position.x"),
    scale=alt.Scale(domain=[0, 100]),
    axis=alt.Axis(values=list(range(0, 101, 10))),
)
color = compare.color()


def concentration(df: pd.DataFrame) -> pd.DataFrame:
    """Part's share over the novel's share, averaged over novels (95 % CI)."""
    totals = df.groupby(["novel_id", "group"])[["hits", "n_paragraphs"]].transform(
        "sum"
    )
    enough = totals["hits"] >= MIN_TAGGED
    ratio = (df["hits"] / df["n_paragraphs"]) / (
        totals["hits"] / totals["n_paragraphs"]
    )
    per_bin = (
        df[enough]
        .assign(value=ratio[enough])
        .groupby(["group", "position_bin", "start", "mid"])["value"]
        .agg(["mean", "std", "size"])
        .reset_index()
    )
    half = 1.96 * per_bin["std"] / np.sqrt(per_bin["size"])
    return per_bin.assign(low=per_bin["mean"] - half, high=per_bin["mean"] + half)


def smooth(df: pd.DataFrame, value: str) -> pd.DataFrame:
    """Average each part with its neighbours (a window of three parts)."""
    return df.assign(
        **{
            value: df.groupby("group")[value].transform(
                lambda s: s.rolling(3, center=True, min_periods=1).mean()
            )
        }
    )


def excerpts_in(set_name: str, novel_ids, low: float, high: float) -> pd.DataFrame:
    """Excerpts of these novels whose first focus paragraph is in [low, high)."""
    excerpts = tables.excerpts(set_name)
    return excerpts[
        excerpts["novel_id"].isin(novel_ids)
        & excerpts["rel_position"].ge(low / 100)
        & excerpts["rel_position"].lt(high / 100)
    ]


def group_novels(group_label: str) -> set[str]:
    return set(bins.loc[bins["group"] == group_label, "novel_id"])


picked = None
picked_title = None
arc_findings: list[str] = []
concentrated = concentration(bins)

if chart_type in ("concentration", "share"):
    smoothed = st.toggle(t("position.smooth"), value=False, key="pos_smooth")
    if chart_type == "concentration":
        per_bin = concentrated
        y_title = t("position.y.concentration")
    else:
        per_bin = (
            bins.groupby(["group", "position_bin", "start", "mid"])[
                ["hits", "n_paragraphs"]
            ]
            .sum()
            .reset_index()
        )
        per_bin = per_bin.assign(mean=per_bin["hits"] / per_bin["n_paragraphs"] * 100)
        per_bin = per_bin.assign(low=per_bin["mean"], high=per_bin["mean"])
        y_title = t("position.y.share")
    if smoothed:
        per_bin = smooth(smooth(smooth(per_bin, "mean"), "low"), "high")

    pick_bin = alt.selection_point(
        name="bin", fields=["position_bin", "group"], on="click"
    )
    y = alt.Y("mean:Q", title=y_title, scale=alt.Scale(zero=chart_type == "share"))
    layers = []
    if chart_type == "concentration":
        layers.append(
            # A computed field rather than its own data: facets need one dataset.
            alt.Chart()
            .transform_calculate(reference="1")
            .mark_rule(strokeWidth=1.5, opacity=0.6, color=charts.ink())
            .encode(y="reference:Q")
        )
        layers.append(
            alt.Chart()
            .mark_area(opacity=0.16)
            .encode(
                x=x_position,
                y="low:Q",
                y2="high:Q",
                color=compare.color(),
                detail="group:N",
            )
        )
    layers.append(
        alt.Chart()
        .mark_line(strokeWidth=2.5)
        .encode(x=x_position, y=y, color=color, detail="group:N")
    )
    layers.append(
        alt.Chart()
        .mark_point(filled=True, size=60, strokeWidth=0)
        .encode(
            x=x_position,
            y=y,
            color=color,
            opacity=alt.condition(pick_bin, alt.value(1), alt.value(0.35)),
            tooltip=[
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("start:Q", title=t("position.part_from"), format=".0f"),
                alt.Tooltip("mean:Q", title=y_title, format=".2f"),
            ],
        )
        .add_params(pick_bin)
    )
    chart = alt.layer(*layers, data=per_bin).properties(height=340)
    if chart_type == "share":
        # The shares with and without shame differ tenfold.
        chart = compare.panels(chart)
    event = charts.show_chart(chart, key=f"pos_{chart_type}")
    points = (event.selection.get("bin") if event else None) or []
    if points:
        p = points[0]
        low = p["position_bin"] * part
        picked = excerpts_in(
            compare.set_of(p["group"]),
            group_novels(p["group"]),
            low,
            low + part,
        )
        picked_title = t("position.bin_selected", a=round(low), b=round(low + part))

elif chart_type == "violin":
    paragraphs = tables.paragraphs().reset_index()
    paragraphs = paragraphs[paragraphs["novel_id"].isin(set(novels["novel_id"]))]
    if shame_mode:
        marks = pd.concat(
            [
                paragraphs[
                    paragraphs["emotion" if g.set_name == "emotion" else "low"]
                ].assign(group=g.label)
                for g in groups
            ]
        )
    else:
        marks = compare.with_group(paragraphs[paragraphs["emotion"]])
    rows = []
    for group, members in marks.groupby("group"):
        density = stats.reflected_density(
            members["rel_position"].to_numpy() * 100, GRID, BANDWIDTH
        )
        rows += [(group, g, d) for g, d in zip(GRID, density, strict=True)]
    dens = pd.DataFrame(rows, columns=["group", "position", "density"])
    dens = dens.assign(left=-dens["density"] / 2, right=dens["density"] / 2)
    half = float(dens["density"].max()) / 2 + 0.1
    x_scale = alt.Scale(domain=[-half, half])
    # An outline of the even spread (width 1) behind each shape.
    even = (
        alt.Chart()
        .transform_calculate(a="-0.5", b="0.5", top="0", bottom="100")
        .mark_rect(fillOpacity=0, stroke=charts.ink(), strokeOpacity=0.35)
        .encode(x=alt.X("a:Q", scale=x_scale), x2="b:Q", y="top:Q", y2="bottom:Q")
    )
    shape = (
        alt.Chart()
        .mark_area(orient="horizontal", opacity=0.8)
        .encode(
            y=alt.Y(
                "position:Q",
                title=t("position.x_down"),
                scale=alt.Scale(domain=[0, 100], reverse=True),
            ),
            x=alt.X(
                "left:Q",
                title=None,
                scale=x_scale,
                axis=alt.Axis(labels=False, ticks=False, grid=False),
            ),
            x2="right:Q",
            color=compare.color(legend=False),
            tooltip=[
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("position:Q", title=t("position.x"), format=".0f"),
                alt.Tooltip("density:Q", title=t("position.density"), format=".2f"),
            ],
        )
    )
    violin = (
        alt.layer(even, shape, data=dens)
        .properties(width=150, height=400)
        .facet(
            column=alt.Column(
                "group:N",
                title=None,
                sort=compare.order(),
                header=alt.Header(labelFontSize=13),
            )
        )
    )
    charts.show_chart(violin, key="pos_violin", select=False)

elif chart_type in ("heatmap", "heatmap_novels"):
    if shame_mode:
        st.caption(t("position.heatmap_shame_only"))
    columns = "novels" if chart_type == "heatmap_novels" else "decades"
    relative = st.toggle(t("position.relative"), value=False, key="pos_heat_rel")
    heat = bins[bins["group"] == groups[0].label] if shame_mode else bins
    prefix = heat["group"] + " · " if split else ""
    if columns == "novels":
        heat = heat.assign(column=prefix + heat["novel_label"])
        order = (
            heat.assign(rank=heat["group"].map(rank))
            .drop_duplicates("column")
            .sort_values(["rank", "year", "column"])["column"]
            .tolist()
        )
    else:
        decade = (heat["year"] // 10 * 10).astype(str) + "s"
        key = prefix + decade
        # How many novels each column pools, since a decade may hold only one.
        n_novels = heat.groupby(key)["novel_id"].transform("nunique")
        heat = (
            heat.assign(column=key + " (" + n_novels.astype(str) + ")")
            .groupby(["column", "group", "position_bin", "start"])[
                ["hits", "n_paragraphs"]
            ]
            .sum()
            .reset_index()
        )
        order = sorted(
            heat["column"].unique(),
            key=lambda c: (rank[heat.loc[heat["column"] == c, "group"].iloc[0]], c),
        )
    first_pct = heat["start"].round().astype(int)
    heat = heat.assign(
        share=heat["hits"] / heat["n_paragraphs"] * 100,
        part=first_pct.astype(str) + "–" + (first_pct + round(part)).astype(str) + " %",
    )
    if relative:
        mean_share = heat.groupby("column")[["hits", "n_paragraphs"]].transform("sum")
        heat["share"] = heat["share"] / (
            mean_share["hits"] / mean_share["n_paragraphs"] * 100
        )
    value_title = t("position.relative_title" if relative else "position.y.share")
    x = alt.X(
        "column:N",
        sort=order,
        title=None,
        axis=alt.Axis(
            labels=columns == "decades",
            ticks=False,
            labelAngle=-45,
            labelLimit=220,
            labelOverlap=False,
        ),
    )
    pick_cell = alt.selection_point(
        name="cell", fields=["column", "position_bin"], on="click"
    )
    cells = (
        alt.Chart(heat)
        .mark_rect()
        .encode(
            x=x,
            y=alt.Y(
                "part:N",
                title=t("position.x_down"),
                sort=alt.EncodingSortField("start", order="ascending"),
            ),
            color=alt.Color(
                "share:Q",
                title=value_title,
                scale=charts.sequential_scale(
                    clamp=True, domainMax=float(heat["share"].quantile(0.98))
                ),
                legend=alt.Legend(
                    orient="right",
                    title=t(
                        "position.legend_relative"
                        if relative
                        else "position.legend_share"
                    ),
                    gradientLength=200,
                ),
            ),
            opacity=alt.condition(pick_cell, alt.value(1), alt.value(0.55)),
            tooltip=[
                alt.Tooltip("column:N", title=t("field.novel")),
                alt.Tooltip("start:Q", title=t("position.part_from"), format=".0f"),
                alt.Tooltip("share:Q", title=value_title, format=".2f"),
                alt.Tooltip("hits:Q", title=t("field.tagged")),
            ],
        )
        .add_params(pick_cell)
        .properties(height=16 * n_bins)
    )
    chart = cells
    if split:
        tag = (
            alt.Chart(heat.drop_duplicates("column"))
            .mark_rect()
            .encode(
                x=alt.X("column:N", sort=order, axis=None),
                color=compare.color(),
                tooltip=[alt.Tooltip("group:N", title=t("field.group"))],
            )
            .properties(height=10)
        )
        chart = alt.vconcat(tag, cells, spacing=2).resolve_scale(color="independent")
    event = charts.show_chart(chart, key=f"pos_heat_{columns}")
    points = (event.selection.get("cell") if event else None) or []
    if points:
        p = points[0]
        low = p["position_bin"] * part
        if columns == "novels":
            label = p["column"].split(" · ", 1)[-1] if split else p["column"]
            group_ids = set(novels.loc[novels["novel_label"] == label, "novel_id"])
        else:
            column = p["column"].rsplit(" (", 1)[0]
            group_label, _, decade = (
                column.rpartition(" · ") if split else ("", "", column)
            )
            members = bins[(bins["year"] // 10 * 10).astype(str) + "s" == decade]
            if split:
                members = members[members["group"] == group_label]
            group_ids = set(members["novel_id"])
        picked = excerpts_in("emotion", group_ids, low, low + part)
        picked_title = t("position.bin_selected", a=round(low), b=round(low + part))

elif chart_type == "arcs":
    # The arcs come from the pipeline; with shame only, so the shame
    # mode shows one group.
    arcs = tables.table("arcs")
    arcs = arcs[arcs["novel_id"].isin(novels["novel_id"])]
    shown = groups if split else groups[:1]
    arcs = compare.with_group(arcs) if split else arcs.assign(group=shown[0].label)
    arcs = arcs.astype({"arc": str})
    sizes = arcs.drop_duplicates("novel_id")["arc"].value_counts()
    arc_names = {
        a: t("position.arc", arc=t(f"position.arc.{a}"), n=sizes[a])
        for a in [*tables.meta()["overview"]["arc_shapes"], "none"]
        if a in sizes
    }
    parts = tables.meta()["overview"]["arc_parts"]
    arcs = arcs.assign(
        position=(arcs["part"].astype(int) + 0.5) * 100 / parts,
        arc_name=arcs["arc"].map(arc_names),
        novel_label=arcs["novel_id"].map(filters.novel_titles()),
    )
    arc_color = alt.Color(
        "group:N",
        scale=alt.Scale(
            domain=[g.label for g in shown], range=[g.color for g in shown]
        ),
        legend=alt.Legend(title=None) if split else None,
    )
    pick = alt.selection_point(name="novel", fields=["novel_id"], on="click")
    base = alt.Chart(arcs).encode(
        x=alt.X("position:Q", title=t("position.x"), scale=alt.Scale(domain=[0, 100])),
        color=arc_color,
    )
    lines = (
        base.mark_line(strokeWidth=1)
        .encode(
            y=alt.Y("share:Q", title=t("position.arc_y"), axis=alt.Axis(format="%")),
            detail="novel_id:N",
            opacity=alt.condition(pick, alt.value(0.35), alt.value(0.08)),
            tooltip=[alt.Tooltip("novel_label:N", title=t("field.novel"))],
        )
        .add_params(pick)
    )
    means = base.mark_line(strokeWidth=3).encode(y="mean(share):Q")
    chart = (
        alt.layer(lines, means)
        .properties(width=210, height=220)
        .facet(
            facet=alt.Facet(
                "arc_name:N",
                sort=list(arc_names.values()),
                title=None,
                header=alt.Header(labelFontSize=13),
            ),
            columns=3,
        )
    )
    event = charts.show_chart(chart, key="pos_arcs")
    if split:
        counts = arcs.drop_duplicates("novel_id").groupby("group")["arc"]
        share = counts.value_counts(normalize=True).rename("share").reset_index()
        share = share.assign(shape=share["arc"].map(lambda a: t(f"position.arc.{a}")))
        bars = (
            alt.Chart(share)
            .mark_bar()
            .encode(
                y=alt.Y(
                    "shape:N",
                    sort=[t(f"position.arc.{a}") for a in arc_names],
                    title=None,
                ),
                yOffset=alt.YOffset("group:N", sort=[g.label for g in shown]),
                x=alt.X(
                    "share:Q",
                    title=t("position.arc_share"),
                    axis=alt.Axis(format="%", tickCount=5),
                ),
                color=arc_color,
                tooltip=[
                    alt.Tooltip("group:N", title=t("field.group")),
                    alt.Tooltip("share:Q", title=t("position.arc_share"), format=".0%"),
                ],
            )
            .properties(height=20 * len(share) + 80)
        )
        charts.show_chart(bars, key="pos_arc_shares", select=False)
    per_group = arcs.drop_duplicates("novel_id").groupby("group")["arc"]
    for g in shown:
        if g.label in per_group.groups:
            share = per_group.get_group(g.label).value_counts(normalize=True)
            arc_findings.append(
                t(
                    "position.find.arc",
                    group=g.label,
                    arc=t(f"position.arc.{share.idxmax()}"),
                    share=f"{share.max():.0%}",
                )
            )
    novel = (charts.selected(event, "novel", "novel_id") or [None])[0]
    if novel:
        picked = excerpts_in("emotion", [novel], 0, 100.1)
        picked_title = filters.novel_titles().get(novel)
else:  # novels
    c3, c4 = st.columns(2, vertical_alignment="bottom")
    order_by = c3.selectbox(
        t("position.order"),
        ["year", "count", "share", "author"],
        format_func=lambda v: t(f"position.order.{v}"),
        key="pos_order",
    )
    style = c4.segmented_control(
        t("position.marks"),
        ["marks", "smoothed"],
        default="marks",
        required=True,
        format_func=lambda v: t(f"position.marks.{v}"),
        key="pos_marks",
    )
    sort_cols, ascending = {
        "year": (["year", "author"], True),
        "count": (["n_emotion", "year"], False),
        "share": (["share_emotion", "year"], False),
        "author": (["author", "year"], True),
    }[order_by]
    in_groups = compare.with_group(novels)
    if split:
        in_groups = in_groups.assign(rank=in_groups["group"].map(rank))
        sort_cols, ascending = (
            ["rank", *sort_cols],
            [True] + [ascending] * len(sort_cols),
        )
    ranked = in_groups.sort_values(sort_cols, ascending=ascending)
    # The first rows of every group, so that no group falls off the list.
    per_group = max(DEFAULT_ROWS // len(groups), 1) if split else DEFAULT_ROWS
    shown = ranked.groupby("group", sort=False).head(per_group)
    if len(shown) < len(ranked):
        st.caption(t("position.limit", n=len(shown), total=len(ranked)))
    order = shown["novel_label"].tolist()
    # A fixed domain keeps a row for novels without a single mark.
    rows_scale = alt.Scale(domain=order)
    y = alt.Y(
        "novel_label:N",
        sort=order,
        scale=rows_scale,
        title=None,
        axis=alt.Axis(labelOverlap=False, labelLimit=300, labelFontSize=12),
    )
    marks = tables.tagged()
    marks = marks[marks["novel_id"].isin(shown["novel_id"])].merge(
        shown[["novel_id", "novel_label"]], on="novel_id"
    )
    marks = marks.assign(
        position=marks["rel_position"] * 100,
        shame=(marks["score"] * 100).round(),
        group=groups[0].label
        if shame_mode
        else marks["novel_id"].map(compare.novel_groups()),
    )
    x = alt.X(
        "position:Q",
        title=t("position.x"),
        scale=alt.Scale(domain=[0, 100]),
        axis=alt.Axis(values=list(range(0, 101, 10)), orient="top"),
    )
    height = ROW_HEIGHT * len(shown)
    # With groups, the labels sit on the tag column in front of the strip.
    strip_y = (
        alt.Y("novel_label:N", sort=order, scale=rows_scale, axis=None) if split else y
    )
    group_color = (
        compare.color(legend=False) if split else alt.value(charts.set_color("emotion"))
    )
    tick_tooltip = [
        alt.Tooltip("novel_label:N", title=t("field.novel")),
        alt.Tooltip("position:Q", title=t("position.x"), format=".0f"),
        alt.Tooltip("shame:Q", title=t("field.score")),
    ]
    if style == "marks":
        pick_mark = alt.selection_point(
            name="mark", fields=["novel_id", "para_id"], on="click"
        )
        layers = []
        if shame_mode:
            # The comparison paragraphs matched to these novels' shame passages.
            comparison = tables.table("comparison")
            comparison = comparison[comparison["novel_id"].isin(shown["novel_id"])]
            context = (
                tables.paragraphs()
                .reset_index()
                .merge(comparison[["novel_id", "para_id"]], on=["novel_id", "para_id"])
                .merge(shown[["novel_id", "novel_label"]], on="novel_id")
            )
            context = context.assign(
                position=context["rel_position"] * 100,
                shame=(context["score"] * 100).round(),
            )
            layers.append(
                alt.Chart(context)
                .mark_tick(
                    thickness=2,
                    size=ROW_HEIGHT - 5,
                    color=charts.set_color("comparison"),
                )
                .encode(
                    x=x,
                    y=strip_y,
                    tooltip=tick_tooltip,
                )
            )
        layers.append(
            alt.Chart(marks)
            .mark_tick(thickness=2, size=ROW_HEIGHT - 5)
            .encode(
                x=x,
                y=strip_y,
                color=group_color,
                opacity=alt.condition(pick_mark, alt.value(0.9), alt.value(0.35)),
                tooltip=tick_tooltip,
            )
            .add_params(pick_mark)
        )
        strip = alt.layer(*layers).properties(height=height, width=STRIP_WIDTH)
    else:
        rows = []
        for (novel_label, novel_id), members in marks.groupby(
            ["novel_label", "novel_id"]
        ):
            positions = members["position"].to_numpy()
            density = np.exp(
                -0.5 * ((GRID[:, None] - positions[None, :]) / BANDWIDTH) ** 2
            ).sum(axis=1)
            density = density / density.max()
            rows += [
                (novel_label, novel_id, g, d)
                for g, d in zip(GRID, density, strict=True)
            ]
        dens = pd.DataFrame(
            rows, columns=["novel_label", "novel_id", "position", "density"]
        )
        pick_mark = alt.selection_point(
            name="smooth", fields=["novel_id", "position"], on="click"
        )
        strip = (
            alt.Chart(dens)
            .mark_rect(width=12)
            .encode(
                x=x,
                y=strip_y,
                color=alt.Color(
                    "density:Q", scale=charts.sequential_scale(), legend=None
                ),
                tooltip=[
                    alt.Tooltip("novel_label:N", title=t("field.novel")),
                    alt.Tooltip("position:Q", title=t("position.x"), format=".0f"),
                ],
            )
            .add_params(pick_mark)
            .properties(height=height, width=STRIP_WIDTH)
        )
    # Each novel's share beside the strip, as one line down the rows.
    shares = shown.assign(share=shown["share_emotion"] * 100, row=range(len(shown)))
    share_x = alt.X(
        "share:Q",
        title=t("position.share_x"),
        scale=alt.Scale(domainMin=0),
        axis=alt.Axis(orient="top", tickCount=4),
    )
    share_y = alt.Y("novel_label:N", sort=order, scale=rows_scale, axis=None)
    share_line = (
        alt.Chart(shares)
        .mark_line(strokeWidth=2)
        .encode(
            x=share_x, y=share_y, order="row:Q", detail="group:N", color=group_color
        )
    )
    share_dots = (
        alt.Chart(shares)
        .mark_point(filled=True, size=36, opacity=1)
        .encode(
            x=share_x,
            y=share_y,
            color=group_color,
            tooltip=[
                alt.Tooltip("novel_label:N", title=t("field.novel")),
                alt.Tooltip("share:Q", title=t("position.share_x"), format=".1f"),
            ],
        )
    )
    side = alt.layer(share_line, share_dots).properties(
        width=SHARE_WIDTH, height=height
    )
    if split:
        # The group of each novel, as a coloured square before its row.
        tag = (
            alt.Chart(shown)
            .mark_square(size=80)
            .encode(
                y=y,
                color=compare.color(legend=False),
                tooltip=[alt.Tooltip("group:N", title=t("field.group"))],
            )
            .properties(width=14, height=height)
        )
        charts.swatch_legend([(g.label, g.color) for g in groups])
        chart = alt.hconcat(tag, strip, side, spacing=4).resolve_scale(
            y="shared", color="independent"
        )
    else:
        if shame_mode and style == "marks":
            charts.swatch_legend([(g.label, g.color) for g in groups])
        chart = alt.hconcat(strip, side, spacing=12).resolve_scale(
            y="shared", color="independent"
        )
    event = charts.show_chart(chart, key=f"pos_novels_{style}")
    if style == "marks":
        points = (event.selection.get("mark") if event else None) or []
        if points:
            keys = {(p["novel_id"], p["para_id"]) for p in points}
            excerpts = tables.excerpts("emotion")
            candidates = excerpts[excerpts["novel_id"].isin({k[0] for k in keys})]
            picked = candidates[
                candidates.apply(
                    lambda r: any((r.novel_id, pid) in keys for pid in r.focus_ids),
                    axis=1,
                )
            ]
    else:
        points = (event.selection.get("smooth") if event else None) or []
        if points:
            p = points[0]
            picked = excerpts_in(
                "emotion", [p["novel_id"]], p["position"] - 5, p["position"] + 5
            )
            picked_title = t(
                "position.bin_selected",
                a=round(p["position"] - 5),
                b=round(p["position"] + 5),
            )

st.caption(
    t(
        f"position.read.{chart_type.removesuffix('_novels')}",
        min_tagged=MIN_TAGGED,
        arc_min=tables.meta()["overview"]["arc_min_tagged"],
    )
)
notes.methodology(
    "position",
    bins=n_bins,
    part=round(part),
    min_tagged=MIN_TAGGED,
    bw=num(BANDWIDTH),
    arc_min=tables.meta()["overview"]["arc_min_tagged"],
    arc_fit=num(tables.meta()["overview"]["arc_min_fit"]),
)


def finding_lines() -> list[str]:
    lines = []
    for g in groups:
        rows = concentrated[concentrated["group"] == g.label]
        if rows.empty:
            continue
        peak = rows.loc[rows["mean"].idxmax()]
        first_fifth = rows.loc[rows["position_bin"] < FIFTH, "mean"].mean()
        last_fifth = rows.loc[rows["position_bin"] >= n_bins - FIFTH, "mean"].mean()
        lines.append(
            t(
                "position.find.group",
                group=g.label,
                a=round(peak["start"]),
                b=round(peak["start"] + part),
                peak=num(peak["mean"], 2),
                first=num(first_fifth, 2),
                last=num(last_fifth, 2),
            )
        )
    return lines


with findings_box:
    notes.findings(arc_findings + finding_lines())

if picked is not None:
    reader.show_excerpts(picked, key="pos_reader", title=picked_title)
elif chart_type != "violin":
    st.info(t("reader.empty"))
