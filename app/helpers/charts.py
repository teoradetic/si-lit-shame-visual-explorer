"""The shared chart colours and Altair config."""

import html
import re

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
# The position page renders tens of thousands of marks; the default limit
# of 5,000 rows only guards notebooks against huge specs.
alt.data_transformers.disable_max_rows()


def mode() -> str:
    return "dark" if st.context.theme.type == "dark" else "light"


# Black and white: for printing and grey downloads. Groups keep apart by
# grey tone and by pattern: line dashes, point shapes, outlined bars.
# Dark to light, by the number of groups.
_GREYS = {
    1: ["#1a1a1a"],
    2: ["#1a1a1a", "#8c8c8c"],
    3: ["#1a1a1a", "#6e6e6e", "#b3b3b3"],
    4: ["#1a1a1a", "#5c5c5c", "#8c8c8c", "#bdbdbd"],
}
_DASHES = ([1, 0], [7, 3], [1.5, 2.5], [8, 3, 1.5, 3])
_SHAPES = ("circle", "square", "triangle-up", "diamond")
_LINES = ("line", "rule", "trail")
_POINTS = ("point", "circle", "square")
# Bars get an outline, so that a light grey still shows on white.
_FILLS = ("bar", "arc")
# White paper, grey grid, near-black text.
_BW_CONFIG = {
    "background": "#ffffff",
    "axis": {
        "gridColor": "#e0e0e0",
        "domainColor": "#999999",
        "tickColor": "#999999",
        "labelColor": "#333333",
        "titleColor": "#333333",
    },
    "legend": {"labelColor": "#333333", "titleColor": "#333333"},
    "header": {"labelColor": "#333333", "titleColor": "#333333"},
    "title": {"color": "#333333"},
}


# The interface in grey too; the charts are greyed in their spec, so that
# their downloads are grey as well.
BW_CSS = "<style>.stApp { filter: grayscale(1); }</style>"


def bw() -> bool:
    return st.session_state.get("bw", False)


def _grey(color):
    """The grey of the same lightness; other values pass through."""
    if not (isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color)):
        return color
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    level = round(0.2126 * r + 0.7152 * g + 0.0722 * b)
    return "#" + f"{level:02x}" * 3


def _greys(value):
    """Every colour inside a mark or a value in grey."""
    if isinstance(value, dict):
        return {k: _greys(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_greys(v) for v in value]
    return _grey(value)


def _bw_unit(unit: dict) -> None:
    """One mark: grey colours, and a pattern per group of its colour field."""
    mark = unit["mark"] if isinstance(unit["mark"], dict) else {"type": unit["mark"]}
    unit["mark"] = mark = _greys(mark)
    encoding = unit.get("encoding", {})
    for channel in ("fill", "stroke"):
        if channel in encoding:
            encoding[channel] = _greys(encoding[channel])
    color = encoding.get("color")
    if not isinstance(color, dict):
        return
    scale = color.get("scale", {})
    if "field" not in color or color.get("type") not in ("nominal", "ordinal"):
        encoding["color"] = _greys(color)
        return
    domain = scale.get("domain")
    n = len(domain) if isinstance(domain, list) else len(scale.get("range", [])) or 4
    n = min(max(n, 1), 4)
    color["scale"] = {**scale, "range": _GREYS[n]}
    pattern = {k: color[k] for k in ("field", "type", "legend", "sort") if k in color}
    if isinstance(domain, list):
        pattern["scale"] = {"domain": domain}
    kind = mark["type"]
    if kind in _LINES:
        pattern["scale"] = {**pattern.get("scale", {}), "range": list(_DASHES[:n])}
        encoding["strokeDash"] = pattern
    elif kind in _POINTS:
        pattern["scale"] = {**pattern.get("scale", {}), "range": list(_SHAPES[:n])}
        encoding["shape"] = pattern
        mark["type"] = "point"
        mark.setdefault("filled", True)
    if kind in _FILLS:
        mark.setdefault("stroke", _GREYS[1][0])
        mark.setdefault("strokeWidth", 0.8)


def _bw(spec: dict) -> dict:
    """The chart in black and white, on white paper."""
    config = spec.setdefault("config", {})
    for key, value in _BW_CONFIG.items():
        config[key] = (
            {**config.get(key, {}), **value} if isinstance(value, dict) else value
        )
    units = list(_units(spec))
    for unit in units:
        _bw_unit(unit)
    # Where a group has both a shape and a dash, the legend shows the shape
    # alone: a dashed square reads oddly. Vega-Lite still dashes the merged
    # symbol's outline, so the outline goes.
    shaped = {
        u["encoding"]["shape"]["field"] for u in units if "shape" in u["encoding"]
    }
    for unit in units:
        for channel, value in unit["encoding"].items():
            if not (isinstance(value, dict) and value.get("field") in shaped):
                continue
            if channel == "strokeDash":
                value["legend"] = None
            elif channel in ("color", "shape") and value.get("legend", {}) is not None:
                value["legend"] = {**value.get("legend", {}), "symbolStrokeWidth": 0}
    return spec


def _units(spec):
    """Every mark of a Vega-Lite spec, however deeply layered."""
    if not isinstance(spec, dict):
        return
    if "mark" in spec:
        spec.setdefault("encoding", {})
        yield spec
    for key in ("layer", "hconcat", "vconcat", "concat"):
        for part in spec.get(key, []):
            yield from _units(part)
    yield from _units(spec.get("spec"))


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


def two_shades() -> list[str]:
    """A dark and a lighter accent, for the two parts of a bar; both carry
    white text in either mode."""
    ramp = _SEQUENTIAL[mode()]
    return [ramp[6], ramp[4]] if mode() == "light" else [ramp[4], ramp[2]]


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
    """Non-overlapping label positions for a log-log scatter of `a`, `b`."""
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


def spring_layout(nodes: list[str], edges: pd.DataFrame) -> np.ndarray:
    """Positions in [-1, 1]² for a small graph (Fruchterman and Reingold 1991):
    nodes repel, `edges` (a, b) attract, a weak pull keeps the parts together."""
    n = len(nodes)
    pos = np.random.default_rng(0).uniform(-1, 1, (n, 2))
    index = {w: i for i, w in enumerate(nodes)}
    a, b = edges["a"].map(index).to_numpy(), edges["b"].map(index).to_numpy()
    k, step = np.sqrt(4 / n), 0.1
    for _ in range(300):
        delta = pos[:, None] - pos[None, :]
        dist = np.linalg.norm(delta, axis=2) + 1e-6
        force = (delta * (k**2 / dist**2)[..., None]).sum(axis=1) - pos * 0.5
        pull = pos[a] - pos[b]
        pull *= np.linalg.norm(pull, axis=1, keepdims=True) / k
        np.add.at(force, a, -pull)
        np.add.at(force, b, pull)
        length = np.linalg.norm(force, axis=1, keepdims=True) + 1e-9
        pos += force / length * np.minimum(length, step)
        step *= 0.985
    pos -= pos.mean(axis=0)
    return pos / (np.abs(pos).max(axis=0) + 1e-9)


def show_chart(
    chart: alt.TopLevelMixin, key: str, select: bool = True, fit: bool = True
):
    """Render with the shared config; returns the selection event."""
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
    options = {
        "key": key,
        "width": "stretch" if fit else "content",
        "theme": "streamlit",
        "on_select": "rerun" if select else "ignore",
    }
    if bw():
        event = st.vega_lite_chart(_bw(chart.to_dict()), **options)
    else:
        event = st.altair_chart(chart, selection_mode=None, **options)
    return event


def selected(event, param: str, field: str) -> list:
    """Values of `field` in the points selected under parameter `param`."""
    if event is None:
        return []
    points = event.selection.get(param) or []
    return [p[field] for p in points if field in p]
