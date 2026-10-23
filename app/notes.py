"""Boxes that every view shares: findings, and the technical methodology.

Findings are computed from the novels and the comparison currently
selected, so they change with the sidebar; they state what the chart
shows, not more.
"""

import streamlit as st

from language import t


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
