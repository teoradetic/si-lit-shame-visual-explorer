"""Smoke test: every page and chart type renders in both languages and with
every comparison."""

from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

PAGES = [
    "views/home.py",
    "views/over_time.py",
    "views/position.py",
    "views/words.py",
    "views/themes.py",
    "views/stylistics.py",
    "views/method.py",
]
# Page -> (session key of its chart-type picker, chart types, extra state).
CHART_TYPES = {
    "views/over_time.py": (
        "time_type",
        ["scatter", "trend", "decades", "authors", "top", "groups"],
        {},
    ),
    "views/position.py": (
        "pos_type",
        ["concentration", "share", "violin", "heatmap", "novels"],
        {"pos_marks": "smoothed", "pos_all": True},
    ),
    "views/words.py": ("words_type", ["cloud", "map", "dots", "network"], {}),
    "views/stylistics.py": ("style_type", ["index", "raw", "time"], {}),
}
MODES = ["none", "shame", "period", "gender", "authors", "rest", "novels"]


def run(page: str, lang: str, state: dict) -> AppTest:
    at = AppTest.from_file("../app/streamlit_app.py", default_timeout=120)
    # Switch the language after the first run, as a reader would.
    at.run()
    at.session_state["lang"] = lang
    for key, value in state.items():
        at.session_state[key] = value
    at.switch_page(page).run()
    return at


@pytest.mark.parametrize("lang", ["en", "sl"])
@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page, lang):
    at = run(page, lang, {})
    assert not at.exception, [e.value for e in at.exception]


CASES = [
    (page, key, chart, extra)
    for page, (key, charts, extra) in CHART_TYPES.items()
    for chart in charts
]


@pytest.mark.parametrize("lang", ["en", "sl"])
@pytest.mark.parametrize(("page", "key", "chart", "extra"), CASES)
def test_chart_type_renders(page, key, chart, extra, lang):
    at = run(page, lang, {key: chart, **extra})
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize(("page", "key", "chart", "extra"), CASES)
def test_chart_type_renders_with_each_comparison(page, key, chart, extra, mode):
    at = run(page, "en", {key: chart, "cmp_mode": mode, **extra})
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("mode", MODES)
def test_clicked_word_shows_its_neighbours_and_cases(mode):
    # The chart's event, as Streamlit hands it to the page after a click.
    click = SimpleNamespace(selection={"word": [{"word": "sram", "side": "emotion"}]})
    at = run("views/words.py", "en", {"cmp_mode": mode, "words_type": "dots"})
    at.session_state["words_dots"] = click
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    titles = [h.value for h in at.subheader]
    assert titles[:2] == ["Words that come with *sram*", "Cases of *sram*"]


@pytest.mark.parametrize(
    "state",
    [{"words_class": c} for c in ("nouns", "verbs", "all")]
    + [{"words_split": s} for s in ("narration", "dialogue")],
)
def test_word_options_render(state):
    at = run("views/words.py", "en", state)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("mode", MODES)
def test_clicked_theme_shows_its_passages(mode):
    click = SimpleNamespace(selection={"theme": [{"theme": 1, "set": "emotion"}]})
    at = run("views/themes.py", "en", {"cmp_mode": mode})
    at.session_state["themes_chart"] = click
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.subheader[0].value.startswith("Passages on the theme")
