from pathlib import Path
import os
import sqlite3
import sys

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


from components.styles import (
    apply_global_styles,
    section_header,
    status_card,
)


DATABASE_PATH = (
    BASE_DIR
    / "data"
    / "manufacturing.db"
)

KNOWLEDGE_DIR = (
    BASE_DIR
    / "data"
    / "knowledge"
)

EMBEDDING_PATH = (
    KNOWLEDGE_DIR
    / "embeddings.npy"
)

CHUNKS_PATH = (
    KNOWLEDGE_DIR
    / "chunks.json"
)


st.set_page_config(
    page_title="Manufacturing AI Assistant",
    page_icon="🏭",
    layout="wide",
)

apply_global_styles()


def check_database() -> bool:
    if not DATABASE_PATH.exists():
        return False

    try:
        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:
            connection.execute(
                "SELECT 1"
            )

        return True

    except sqlite3.Error:
        return False


database_ready = check_database()

knowledge_ready = (
    EMBEDDING_PATH.exists()
    and CHUNKS_PATH.exists()
)

llm_provider = os.getenv(
    "LLM_PROVIDER",
    "deepseek",
)

application_version = os.getenv(
    "APP_VERSION",
    "2.0.0",
)


st.title(
    "🏭 Manufacturing AI Assistant"
)

st.caption(
    "AI-powered production intelligence platform "
    "for manufacturing data analysis, equipment "
    "monitoring and knowledge retrieval."
)

st.divider()


section_header(
    title="System Overview",
    description=(
        "Current platform status and core runtime "
        "configuration."
    ),
)


status_columns = st.columns(4)

with status_columns[0]:
    status_card(
        title="Application",
        value="Running",
        description=(
            f"Version {application_version}"
        ),
    )

with status_columns[1]:
    status_card(
        title="Database",
        value=(
            "Connected"
            if database_ready
            else "Unavailable"
        ),
        description="SQLite manufacturing database",
    )

with status_columns[2]:
    status_card(
        title="Knowledge Base",
        value=(
            "Ready"
            if knowledge_ready
            else "Not Ready"
        ),
        description="RAG document index",
    )

with status_columns[3]:
    status_card(
        title="LLM Provider",
        value=llm_provider.title(),
        description="Language model integration",
    )


st.divider()


section_header(
    title="Platform Modules",
    description=(
        "Use the left navigation menu to open "
        "each manufacturing intelligence module."
    ),
)


module_columns = st.columns(3)

with module_columns[0]:
    st.markdown(
        "### 📊 Dashboard"
    )

    st.write(
        "Monitor production KPIs, weight trends, "
        "abnormal rates and recent quality records."
    )

    st.markdown(
        "### 🏥 Equipment Health"
    )

    st.write(
        "Compare equipment health scores and "
        "identify equipment requiring attention."
    )

with module_columns[1]:
    st.markdown(
        "### 🚨 Root Cause Analysis"
    )

    st.write(
        "Analyze abnormal patterns by equipment, "
        "product, anomaly type and time period."
    )

    st.markdown(
        "### 🤖 AI Assistant"
    )

    st.write(
        "Ask natural-language questions using "
        "Text-to-SQL, RAG and hybrid analysis."
    )

with module_columns[2]:
    st.markdown(
        "### 📚 Knowledge Search"
    )

    st.write(
        "Search manuals, SOPs and quality procedures "
        "with document source references."
    )

    st.markdown(
        "### ⚙️ Settings"
    )

    st.write(
        "Review model, database, knowledge index "
        "and application configuration."
    )


st.divider()


section_header(
    title="Core Capabilities",
    description=(
        "The platform combines production data, "
        "manufacturing knowledge and AI analysis."
    ),
)


capability_columns = st.columns(4)

with capability_columns[0]:
    st.metric(
        label="Data Query",
        value="Text-to-SQL",
    )

with capability_columns[1]:
    st.metric(
        label="Knowledge",
        value="RAG",
    )

with capability_columns[2]:
    st.metric(
        label="Reasoning",
        value="Hybrid AI",
    )

with capability_columns[3]:
    st.metric(
        label="Monitoring",
        value="Health Score",
    )


st.divider()


section_header(
    title="Recommended Workflow",
    description=(
        "A practical sequence for investigating "
        "manufacturing quality issues."
    ),
)


workflow_columns = st.columns(4)

with workflow_columns[0]:
    st.markdown(
        "### 1. Monitor"
    )

    st.write(
        "Review production KPIs and abnormal trends "
        "in the Dashboard."
    )

with workflow_columns[1]:
    st.markdown(
        "### 2. Prioritize"
    )

    st.write(
        "Use Equipment Health to identify "
        "higher-risk equipment."
    )

with workflow_columns[2]:
    st.markdown(
        "### 3. Investigate"
    )

    st.write(
        "Run Root Cause Analysis to inspect "
        "abnormal contribution patterns."
    )

with workflow_columns[3]:
    st.markdown(
        "### 4. Ask"
    )

    st.write(
        "Use the AI Assistant for data questions, "
        "SOP guidance and combined analysis."
    )


st.divider()


if not database_ready:
    st.warning(
        "The manufacturing database is unavailable. "
        "Run the database initialization scripts."
    )

    st.code(
        (
            "python scripts\\generate_data.py\n"
            "python scripts\\init_database.py"
        ),
        language="powershell",
    )


if not knowledge_ready:
    st.warning(
        "The knowledge index is unavailable. "
        "Build the document index before using RAG."
    )

    st.code(
        "python scripts\\build_knowledge_index.py",
        language="powershell",
    )


if database_ready and knowledge_ready:
    st.success(
        "All core platform services are ready."
    )