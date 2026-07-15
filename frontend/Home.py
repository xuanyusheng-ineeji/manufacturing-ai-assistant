from pathlib import Path
import sys

import streamlit as st

from components.styles import (
    apply_global_styles,
)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


st.set_page_config(
    page_title="Manufacturing AI Assistant",
    page_icon="🏭",
    layout="wide",
)
apply_global_styles()


st.title("🏭 Manufacturing AI Assistant")

st.caption(
    "AI-powered production intelligence platform for "
    "manufacturing data analysis, equipment monitoring "
    "and knowledge retrieval."
)

st.divider()


st.subheader("Platform Modules")

module_columns = st.columns(3)

with module_columns[0]:
    st.markdown("### 📊 Dashboard")
    st.write(
        "Monitor production KPIs, weight trends, "
        "abnormal rates and recent quality records."
    )

with module_columns[1]:
    st.markdown("### 🏥 Equipment Health")
    st.write(
        "Compare equipment health scores based on "
        "abnormal rate, rework, trend and weight deviation."
    )

with module_columns[2]:
    st.markdown("### 🚨 Root Cause Analysis")
    st.write(
        "Analyze abnormal patterns by equipment, "
        "product, time period and anomaly type."
    )


module_columns_second = st.columns(3)

with module_columns_second[0]:
    st.markdown("### 🤖 AI Assistant")
    st.write(
        "Ask natural-language questions and automatically "
        "route them to SQL, RAG or hybrid analysis."
    )

with module_columns_second[1]:
    st.markdown("### 📚 Knowledge Search")
    st.write(
        "Search equipment manuals, SOPs and "
        "quality procedures with source references."
    )

with module_columns_second[2]:
    st.markdown("### ⚙️ Settings")
    st.write(
        "Review the current model, database, "
        "knowledge index and application version."
    )


st.divider()


st.subheader("Current Capabilities")

capability_columns = st.columns(4)

with capability_columns[0]:
    st.metric(
        "Data Query",
        "Text-to-SQL",
    )

with capability_columns[1]:
    st.metric(
        "Knowledge",
        "RAG",
    )

with capability_columns[2]:
    st.metric(
        "Analysis",
        "Hybrid AI",
    )

with capability_columns[3]:
    st.metric(
        "Monitoring",
        "Health Score",
    )


st.divider()


st.subheader("Recommended Starting Points")

st.markdown(
    """
- Open **Dashboard** to review production and quality KPIs.
- Open **Equipment Health** to identify risk equipment.
- Open **Root Cause Analysis** to inspect abnormal patterns.
- Open **AI Assistant** to ask questions in natural language.
"""
)


st.info(
    "Use the page navigation in the left sidebar "
    "to open each module."
)