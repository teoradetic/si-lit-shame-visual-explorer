"""Overview: what the tool shows, key numbers and a first few passages."""

import streamlit as st

import filters
import reader
import tables
from language import num, t

meta = tables.meta()["paragraphs"]
f = filters.current()

st.title(t("app.title"))
st.write(
    t(
        "home.intro",
        novels=meta["n_novels"],
        authors=meta["n_authors"],
        first=meta["year_range"][0],
        last=meta["year_range"][1],
    )
)
st.info(t("home.caveat"), icon=":material/info:")

ids = filters.novel_ids()
selected = filters.filtered_novels()
excerpts = tables.excerpts(f.tier)
excerpts = excerpts[excerpts["novel_id"].isin(ids)]
cols = st.columns(4)
cols[0].metric(t("home.m_novels"), num(len(selected), 0))
cols[1].metric(t("home.m_paragraphs"), num(int(selected["n_paragraphs"].sum()), 0))
cols[2].metric(t("home.m_tagged"), num(int(selected[f"n_{f.tier}"].sum()), 0))
cols[3].metric(t("home.m_excerpts"), num(len(excerpts), 0))

st.subheader(t("home.views"))
for view in ("time", "position", "words", "style", "method"):
    st.markdown(f"- {t(f'home.view.{view}')}")

filters.stop_if_empty()
reader.show_excerpts(
    excerpts, key="home", title=t("home.sample"), default_sort="random"
)
