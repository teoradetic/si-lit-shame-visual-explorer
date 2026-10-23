"""Entry point: language switch, global filters and navigation."""

import streamlit as st

import compare
import filters
import reader
from language import LANGUAGES, t

st.set_page_config(page_title=t("app.title"), layout="wide")
reader.inject_css()

title, switch = st.columns([5, 1], vertical_alignment="center")
switch.segmented_control(
    t("app.language"),
    LANGUAGES,
    default="en",
    required=True,
    format_func=str.upper,
    key="lang",
    label_visibility="collapsed",
)
title.caption(t("app.title"))

# The comparison comes first in the sidebar: it shapes every chart.
compare.sidebar()
filters.sidebar()

# Pages live in views/, not pages/, so Streamlit's automatic multipage
# mode never picks them up alongside st.navigation.
pages = [
    st.Page("views/home.py", title=t("nav.home"), default=True),
    st.Page("views/over_time.py", title=t("nav.time"), url_path="over-time"),
    st.Page("views/position.py", title=t("nav.position"), url_path="position"),
    st.Page("views/words.py", title=t("nav.words"), url_path="words"),
    st.Page("views/stylistics.py", title=t("nav.style"), url_path="style"),
    st.Page("views/method.py", title=t("nav.method"), url_path="method"),
]
st.navigation(pages, position="top").run()
