"""Entry point of the Streamlit app: page config and navigation."""

import streamlit as st

st.set_page_config(page_title="Emotion explorer", layout="wide")

# Pages live in views/, not pages/, so Streamlit's automatic multipage
# mode never picks them up alongside st.navigation.
home = st.Page("views/home.py", title="Home", default=True)

st.navigation([home]).run()
