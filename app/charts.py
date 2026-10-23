"""The shared chart style (SET-03): colours, shapes and Altair config.

Every chart goes through `show_chart`, which applies the same config and lets
Streamlit's theme carry the fonts and light/dark ink. Colours follow the
entity, never the order: Realism is always blue and Modernism always orange,
in every view. The palette passes the CVD and contrast checks in both modes.
"""

import altair as alt
import streamlit as st

PERIODS = ("Realism", "Modernism", "unknown")
GENDERS = ("F", "M", "unknown")

_PERIOD_COLORS = {
    "light": ("#2a78d6", "#eb6834", "#898781"),
    "dark": ("#3987e5", "#d95926", "#898781"),
}
# Detected passages against the comparison set: ink against muted grey, so
# that neither looks like a period.
_SET_COLORS = {
    "light": {"emotion": "#52514e", "comparison": "#b5b3ab"},
    "dark": {"emotion": "#e4e2dc", "comparison": "#6f6e69"},
}
GENDER_SHAPES = {"F": "triangle-up", "M": "circle", "unknown": "square"}

# Charts render tens of thousands of marks in AN-02; the default limit of
# 5,000 rows only guards notebooks against huge specs.
alt.data_transformers.disable_max_rows()


def mode() -> str:
    return "dark" if st.context.theme.type == "dark" else "light"


def period_scale(labels: dict[str, str]) -> alt.Scale:
    """Colour scale over translated period labels, in the fixed order."""
    return alt.Scale(
        domain=[labels[p] for p in PERIODS], range=list(_PERIOD_COLORS[mode()])
    )


def period_color(period: str) -> str:
    return _PERIOD_COLORS[mode()][PERIODS.index(period)]


def set_color(name: str) -> str:
    return _SET_COLORS[mode()][name]


def gender_shape(labels: dict[str, str]) -> alt.Scale:
    return alt.Scale(
        domain=[labels[g] for g in GENDERS], range=[GENDER_SHAPES[g] for g in GENDERS]
    )


def show_chart(chart: alt.TopLevelMixin, key: str, select: bool = True):
    """Render with the shared config; returns the selection event."""
    chart = (
        chart.configure_view(stroke=None)
        .configure_legend(orient="top", title=None, labelFontSize=13, symbolSize=120)
        .configure_axis(
            labelFontSize=12, titleFontSize=13, titleFontWeight="normal", domain=False
        )
    )
    return st.altair_chart(
        chart,
        key=key,
        theme="streamlit",
        on_select="rerun" if select else "ignore",
        selection_mode=None,
    )
