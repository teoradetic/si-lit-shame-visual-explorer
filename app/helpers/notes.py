"""The findings and methodology boxes every view shares."""

import streamlit as st

from helpers.language import t


def findings(lines: list[str]) -> None:
    if not lines:
        return
    with st.container(border=True):
        st.markdown(f":material/lightbulb: **{t('findings.title')}**")
        st.markdown("\n".join(f"- {line}" for line in lines))
        st.caption(t("findings.note"))


def methodology(view: str, **values) -> None:
    """A short technical account of the view, for readers who want the detail."""
    with st.expander(t("methodology.title"), icon=":material/functions:"):
        st.markdown(t(f"{view}.methodology", **values))
