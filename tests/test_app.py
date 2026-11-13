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
    "views/people.py",
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
        [
            "concentration",
            "share",
            "violin",
            "heatmap",
            "heatmap_novels",
            "novels",
            "arcs",
        ],
        {"pos_marks": "smoothed"},
    ),
    "views/words.py": ("words_type", ["cloud", "map", "dots", "network"], {}),
    "views/stylistics.py": ("style_type", ["index", "raw", "time"], {}),
}
MODES = ["shame", "period", "gender", "authors", "rest", "novels"]


def run(page: str, lang: str, state: dict) -> AppTest:
    at = AppTest.from_file("../app/streamlit_app.py", default_timeout=120)
    at.run()
    for key, value in {"cmp_mode": "shame", **state}.items():
        at.session_state[key] = value
    at.switch_page(page).run()
    # Run the comparison, as a reader must before a page shows its charts.
    run_button = [b for b in at.button if b.key == "cmp_run"]
    if run_button:
        run_button[0].click().run()
    # Switch the language last: AppTest formats a selectbox's value in
    # English, so a click after the switch would not find it.
    if lang != "en":
        at.session_state["lang"] = lang
        at.run()
    return at


def test_page_waits_until_a_comparison_is_run():
    at = AppTest.from_file("../app/streamlit_app.py", default_timeout=120)
    at.run()
    at.switch_page("views/words.py").run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.info[0].value.startswith("Choose what to compare")
    assert not at.get("vega_lite_chart")


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
    + [{"f_text": s} for s in ("narration", "dialogue")],
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


def test_clicked_word_of_two_themes_shows_its_passages():
    click = SimpleNamespace(selection={"pair_word": [{"word": "mati"}]})
    at = run("views/themes.py", "en", {})
    at.session_state["themes_pair"] = click
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert "with the word “mati”" in at.subheader[-1].value


@pytest.mark.parametrize("mode", MODES)
def test_clicked_name_shows_its_passages(mode):
    click = SimpleNamespace(selection={"name": [{"word": "bog"}]})
    at = run("views/people.py", "en", {"cmp_mode": mode})
    at.session_state["people_names"] = click
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.subheader[-1].value == "Passages containing a form of “bog”"
