from pathlib import Path
import sys

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="Equipment Health",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Equipment Health")

st.caption(
    "Monitor equipment condition using health scores "
    "derived from production quality metrics."
)

st.divider()

st.info(
    "Equipment Health page migration is in progress."
)