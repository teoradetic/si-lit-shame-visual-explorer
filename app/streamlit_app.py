"""Entry point: language switch, global filters and navigation."""

import streamlit as st

from helpers import compare, filters, reader
from helpers.language import LANGUAGES, lang, setting, t

st.set_page_config(page_title=t("app.title"), layout="wide")
reader.inject_css()

# Pages live in views/, not pages/, so Streamlit's automatic multipage
# mode never picks them up alongside st.navigation.
pages = [
    st.Page("views/home.py", title=t("nav.home"), default=True),
    st.Page("views/over_time.py", title=t("nav.time"), url_path="over-time"),
    st.Page("views/position.py", title=t("nav.position"), url_path="position"),
    st.Page("views/words.py", title=t("nav.words"), url_path="words"),
    st.Page("views/themes.py", title=t("nav.themes"), url_path="themes"),
    st.Page("views/people.py", title=t("nav.people"), url_path="people"),
    st.Page("views/stylistics.py", title=t("nav.style"), url_path="style"),
    st.Page("views/method.py", title=t("nav.method"), url_path="method"),
]
# The language menu is a dropdown at the end of the top menu (Streamlit puts
# named sections after the pages), named after the current language; its
# entries are the other languages. Flag emoji show as letters
# (GB, SI) on Windows; the names stay readable.
languages = {
    st.Page(
        lambda: None,
        title=f"{setting('flag', code)} {setting('name', code)}",
        url_path=f"language-{code}",
    ): code
    for code in LANGUAGES
    if code != lang()
}
page = st.navigation(
    {"": pages, f"{setting('flag')} {setting('name')}": list(languages)},
    position="top",
)
if page in languages:
    # Switch before anything is drawn, then go back to the last page.
    st.session_state["lang"] = languages[page]
    back = st.session_state.get("last_page")
    st.switch_page(next((p for p in pages if p.url_path == back), pages[0]))
st.session_state["last_page"] = page.url_path

st.caption(t("app.title"))
# The comparison comes first in the sidebar: it shapes every chart.
compare.sidebar()
# The text split only changes the Words and Style pages.
filters.sidebar(text=page.url_path in ("words", "style"))
page.run()
