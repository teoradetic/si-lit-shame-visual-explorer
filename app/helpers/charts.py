"""The shared chart style (SET-03): colours and Altair config.

Every chart goes through `show_chart`, which applies the same config and lets
Streamlit's theme carry the fonts and light/dark ink. Colours follow the
entity, never the order: passages with shame are always plum and those
without grey, Realism is always blue and Modernism always orange, in every
view. Other comparisons (author gender, authors, novels) take the group
palette in a fixed order. Each set passes the CVD and contrast checks in both
modes; the group palette also for every pair, as scatter plots need.
"""

import html

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

PERIODS = ("Realism", "Modernism", "unknown")
GENDERS = ("F", "M", "unknown")

_PERIOD_COLORS = {
    "light": ("#2a78d6", "#eb6834", "#898781"),
    "dark": ("#3987e5", "#d95926", "#898781"),
}
# Passages with the emotion in the app's accent (plum), those without in a
# neutral grey: the grey is meant to read as "nothing".
_SET_COLORS = {
    "light": {"emotion": "#8a4f7d", "comparison": "#b5b3ab"},
    "dark": {"emotion": "#b86fa5", "comparison": "#6f6e69"},
}
# Aqua, yellow and violet: no period's colour and far from plum. Three is
# the most that stay apart in every pair in both modes.
_GROUP_COLORS = {
    "light": ("#1baf7a", "#eda100", "#6250d6"),
    "dark": ("#199e70", "#c98500", "#9085e9"),
}
# Text and lines that stand for no group (reference lines, shared words).
_INK = {"light": "#52514e", "dark": "#e4e2dc"}
# One-hue ramps (plum, the app's accent) for magnitudes in heatmaps; plum is
# no period's colour. Dark mode runs from the dark surface up to light.
_SEQUENTIAL = {
    "light": [
        "#f4eef3",
        "#e3d2df",
        "#cfb0c7",
        "#b98caf",
        "#a26b97",
        "#8a4f7d",
        "#6e3d63",
        "#53304b",
    ],
    "dark": [
        "#2b2229",
        "#41303d",
        "#5a4054",
        "#76526d",
        "#946787",
        "#b17fa3",
        "#cc9cc0",
        "#e4bfda",
    ],
}
# Charts render tens of thousands of marks in AN-02; the default limit of
# 5,000 rows only guards notebooks against huge specs.
alt.data_transformers.disable_max_rows()


def mode() -> str:
    return "dark" if st.context.theme.type == "dark" else "light"


def period_color(period: str) -> str:
    return _PERIOD_COLORS[mode()][PERIODS.index(period)]


def set_color(name: str) -> str:
    """Plum for passages with the emotion, grey for those without."""
    return _SET_COLORS[mode()][name]


def group_color(i: int) -> str:
    return _GROUP_COLORS[mode()][i]


def ink() -> str:
    """Marks that stand for no group: reference lines, words shared by all."""
    return _INK[mode()]


def sequential_scale(**kwargs) -> alt.Scale:
    return alt.Scale(range=_SEQUENTIAL[mode()], **kwargs)


def swatch_legend(items: list[tuple[str, str]]) -> None:
    """A legend of colour swatches, for charts too narrow to hold one."""
    swatches = "".join(
        f'<span><span class="swatch" style="background:{color}"></span>'
        f"{html.escape(name)}</span>"
        for name, color in items
    )
    st.html(f'<div class="reader-legend">{swatches}</div>')


# Where a label may sit around its dot, in pixels: beside, above and below,
# then diagonally; the second ring is farther out and gets a leader line.
_LABEL_SPOTS = [
    (7, 0, "left"),
    (-7, 0, "right"),
    (0, -11, "center"),
    (0, 11, "center"),
    (5, -9, "left"),
    (5, 9, "left"),
    (-5, -9, "right"),
    (-5, 9, "right"),
]
_LABEL_RINGS = (1, 2.5)
DOT_RADIUS = 5


def place_labels(
    df: pd.DataFrame,
    domain: tuple[float, float],
    width: int,
    height: int,
    font_size: int = 12,
) -> pd.DataFrame:
    """Label positions that do not overlap, for a log-log scatter of `a`, `b`.

    Rows are placed in order, so the most important come first. Each label
    tries the spots around its dot until one is clear of every placed label
    and every other dot; a label with no clear spot is left out (its dot
    keeps its tooltip). Returns the anchor in data units (`label_a`,
    `label_b`), the text `align`, whether a `leader` line is needed, and
    `labelled`.
    """
    low, high = np.log(domain[0]), np.log(domain[1])
    span = high - low
    px = width * (np.log(df["a"].to_numpy()) - low) / span
    py = height * (1 - (np.log(df["b"].to_numpy()) - low) / span)
    char_width = 0.58 * font_size
    box_height = font_size + 2
    placed: list[tuple[float, float, float, float]] = []
    rows = []
    for i, word in enumerate(df["word"].astype(str)):
        text_width = char_width * len(word)
        others = np.delete(np.arange(len(df)), i)
        spot = None
        for ring in _LABEL_RINGS:
            for dx, dy, align in _LABEL_SPOTS:
                x, y = px[i] + dx * ring, py[i] + dy * ring
                x0 = {"left": x, "right": x - text_width}.get(align, x - text_width / 2)
                box = (x0, y - box_height / 2, x0 + text_width, y + box_height / 2)
                inside = box[0] >= 0 and box[2] <= width and box[1] >= 0
                inside = inside and box[3] <= height
                hits_label = any(
                    box[0] < p[2] and p[0] < box[2] and box[1] < p[3] and p[1] < box[3]
                    for p in placed
                )
                hits_dot = (
                    (px[others] + DOT_RADIUS > box[0])
                    & (px[others] - DOT_RADIUS < box[2])
                    & (py[others] + DOT_RADIUS > box[1])
                    & (py[others] - DOT_RADIUS < box[3])
                ).any()
                if inside and not hits_label and not hits_dot:
                    spot = (x, y, align, ring > 1)
                    placed.append(box)
                    break
            if spot:
                break
        if spot is None:
            rows.append((np.nan, np.nan, "left", False, False))
            continue
        x, y, align, leader = spot
        rows.append(
            (
                float(np.exp(low + x / width * span)),
                float(np.exp(low + (1 - y / height) * span)),
                align,
                leader,
                True,
            )
        )
    placement = pd.DataFrame(
        rows,
        columns=["label_a", "label_b", "align", "leader", "labelled"],
        index=df.index,
    )
    return df.join(placement)


def show_chart(
    chart: alt.TopLevelMixin, key: str, select: bool = True, fit: bool = True
):
    """Render with the shared config; returns the selection event.

    `fit=False` keeps a chart's own width, for layouts computed in pixels.
    """
    composite = not fit or isinstance(
        chart, (alt.FacetChart, alt.HConcatChart, alt.VConcatChart)
    )
    chart = chart.properties(padding={"left": 8, "right": 8, "top": 4, "bottom": 4})
    if not composite:
        # "padding" keeps long axis labels inside the chart's width; composite
        # charts size their panels themselves.
        chart = chart.properties(
            autosize=alt.AutoSizeParams(type="fit", contains="padding")
        )
    chart = (
        chart.configure_view(stroke=None)
        .configure_legend(
            orient="top", title=None, labelFontSize=13, symbolSize=120, symbolOpacity=1
        )
        .configure_axis(
            labelFontSize=12, titleFontSize=13, titleFontWeight="normal", domain=False
        )
    )
    return st.altair_chart(
        chart,
        key=key,
        width="stretch" if fit else "content",
        theme="streamlit",
        on_select="rerun" if select else "ignore",
        selection_mode=None,
    )


def selected(event, param: str, field: str) -> list:
    """Values of `field` in the points selected under parameter `param`."""
    if event is None:
        return []
    points = event.selection.get(param) or []
    return [p[field] for p in points if field in p]
