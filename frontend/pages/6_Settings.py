import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from frontend.components.header import page_header
from frontend.components.metrics import metric_row
from frontend.components.styles import (
    apply_global_styles,
)

ENV_PATH = BASE_DIR / ".env"
DATABASE_PATH = BASE_DIR / "data" / "manufacturing.db"
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"
EMBEDDING_PATH = KNOWLEDGE_DIR / "embeddings.npy"
CHUNKS_PATH = KNOWLEDGE_DIR / "chunks.json"


load_dotenv(
    dotenv_path=ENV_PATH,
    override=False,
)


st.set_page_config(
    page_title="System Settings",
    page_icon="⚙️",
    layout="wide",
)
apply_global_styles()

def mask_api_key(
    api_key: str | None,
) -> str:
    """
    Mask the API key so the complete secret is never displayed.
    """

    if not api_key:
        return "Not configured"

    if len(api_key) <= 8:
        return "Configured"

    return (
        f"{api_key[:4]}"
        f"{'*' * 10}"
        f"{api_key[-4:]}"
    )


def get_file_modified_time(
    file_path: Path,
) -> str:
    """
    Return a readable last-modified timestamp.
    """

    if not file_path.exists():
        return "Not available"

    modified_timestamp = (
        file_path.stat().st_mtime
    )

    modified_datetime = datetime.fromtimestamp(
        modified_timestamp
    )

    return modified_datetime.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_file_size(
    file_path: Path,
) -> str:
    """
    Return the file size in a readable format.
    """

    if not file_path.exists():
        return "Not available"

    size_bytes = file_path.stat().st_size

    if size_bytes < 1024:
        return f"{size_bytes} B"

    size_kb = size_bytes / 1024

    if size_kb < 1024:
        return f"{size_kb:.1f} KB"

    size_mb = size_kb / 1024

    return f"{size_mb:.1f} MB"


def check_database_connection() -> tuple[
    bool,
    str,
]:
    """
    Test whether the SQLite database can be opened.
    """

    if not DATABASE_PATH.exists():
        return (
            False,
            "Database file does not exist.",
        )

    try:
        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:
            connection.execute(
                "SELECT 1"
            )

        return (
            True,
            "Connected",
        )

    except sqlite3.Error as exc:
        return (
            False,
            str(exc),
        )


def get_database_tables() -> list[str]:
    """
    Return the list of user-created database tables.
    """

    if not DATABASE_PATH.exists():
        return []

    try:
        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:
            cursor = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )

            rows = cursor.fetchall()

        return [
            str(row[0])
            for row in rows
        ]

    except sqlite3.Error:
        return []


def get_table_row_counts(
    table_names: list[str],
) -> dict[str, int]:
    """
    Return row counts for each database table.
    """

    row_counts: dict[str, int] = {}

    if not DATABASE_PATH.exists():
        return row_counts

    try:
        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:
            for table_name in table_names:
                safe_table_name = (
                    table_name.replace(
                        '"',
                        '""',
                    )
                )

                cursor = connection.execute(
                    f'''
                    SELECT COUNT(*)
                    FROM "{safe_table_name}"
                    '''
                )

                result = cursor.fetchone()

                row_counts[table_name] = int(
                    result[0]
                    if result
                    else 0
                )

    except sqlite3.Error:
        return {}

    return row_counts


def get_knowledge_chunk_count() -> int:
    """
    Count knowledge chunks stored in chunks.json.
    """

    if not CHUNKS_PATH.exists():
        return 0

    try:
        payload = json.loads(
            CHUNKS_PATH.read_text(
                encoding="utf-8",
            )
        )

        if isinstance(payload, list):
            return len(payload)

        return 0

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return 0


def get_document_count() -> int:
    """
    Count supported source documents in the docs directory.
    """

    docs_dir = BASE_DIR / "docs"

    if not docs_dir.exists():
        return 0

    supported_extensions = {
        ".md",
        ".txt",
        ".pdf",
    }

    return sum(
        1
        for file_path in docs_dir.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in supported_extensions
        )
    )


def render_status_badge(
    connected: bool,
    success_message: str,
    failure_message: str,
) -> None:
    """
    Render a success or error message.
    """

    if connected:
        st.success(success_message)
    else:
        st.error(failure_message)


database_connected, database_message = (
    check_database_connection()
)

database_tables = get_database_tables()

database_row_counts = (
    get_table_row_counts(
        database_tables
    )
)

database_table_count = len(
    database_tables
)

total_database_rows = sum(
    database_row_counts.values()
)

knowledge_index_ready = (
    EMBEDDING_PATH.exists()
    and CHUNKS_PATH.exists()
)

knowledge_chunk_count = (
    get_knowledge_chunk_count()
)

document_count = get_document_count()


llm_provider = os.getenv(
    "LLM_PROVIDER",
    "deepseek",
)

llm_model = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-chat",
)

llm_base_url = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com",
)

api_key = os.getenv(
    "DEEPSEEK_API_KEY"
)

application_version = os.getenv(
    "APP_VERSION",
    "2.0.0",
)

application_environment = os.getenv(
    "APP_ENV",
    "development",
)

temperature = os.getenv(
    "LLM_TEMPERATURE",
    "0.0",
)


page_header(
    title="⚙️ System Settings",
    caption=(
        "Review application status, AI configuration, "
        "database connectivity and knowledge index information."
    ),
)


st.subheader("System Status")

metric_row(
    [
        {
            "label": "Application",
            "value": "Running",
            "help": (
                "Current Streamlit application status."
            ),
        },
        {
            "label": "Database",
            "value": (
                "Connected"
                if database_connected
                else "Disconnected"
            ),
            "help": (
                "SQLite database connection status."
            ),
        },
        {
            "label": "Knowledge Base",
            "value": (
                "Ready"
                if knowledge_index_ready
                else "Not Ready"
            ),
            "help": (
                "Whether embeddings and chunk metadata "
                "are available."
            ),
        },
        {
            "label": "LLM Provider",
            "value": llm_provider.title(),
            "help": (
                "Current language model provider."
            ),
        },
    ]
)


st.divider()


st.subheader("Application Configuration")

configuration_columns = st.columns(2)

with configuration_columns[0]:
    st.text_input(
        "Application Version",
        value=application_version,
        disabled=True,
    )

    st.text_input(
        "Environment",
        value=application_environment,
        disabled=True,
    )

with configuration_columns[1]:
    st.text_input(
        "Project Root",
        value=str(BASE_DIR),
        disabled=True,
    )

    st.text_input(
        "Environment File",
        value=(
            str(ENV_PATH)
            if ENV_PATH.exists()
            else "Not found"
        ),
        disabled=True,
    )


st.caption(
    "Settings are loaded from the local .env file. "
    "This page is read-only and does not modify configuration."
)


st.divider()


st.subheader("AI Configuration")

ai_columns = st.columns(2)

with ai_columns[0]:
    st.text_input(
        "Provider",
        value=llm_provider,
        disabled=True,
    )

    st.text_input(
        "Model",
        value=llm_model,
        disabled=True,
    )

    st.text_input(
        "Temperature",
        value=temperature,
        disabled=True,
    )

with ai_columns[1]:
    st.text_input(
        "Base URL",
        value=llm_base_url,
        disabled=True,
    )

    st.text_input(
        "API Key",
        value=mask_api_key(
            api_key
        ),
        disabled=True,
    )


if api_key:
    st.success(
        "Language model API key is configured."
    )
else:
    st.warning(
        "DEEPSEEK_API_KEY is not configured. "
        "AI query and RAG response generation may fail."
    )


with st.expander(
    "Recommended AI environment variables"
):
    st.code(
        """
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
LLM_TEMPERATURE=0.0
APP_VERSION=2.0.0
APP_ENV=development
""".strip(),
        language="text",
    )

    st.warning(
        "Do not commit the .env file or a real API key "
        "to GitHub."
    )


st.divider()


st.subheader("Database Status")

metric_row(
    [
        {
            "label": "Connection",
            "value": (
                "Connected"
                if database_connected
                else "Disconnected"
            ),
            "help": (
                "Whether the SQLite database can "
                "successfully execute a test query."
            ),
        },
        {
            "label": "Database Type",
            "value": "SQLite",
            "help": (
                "Current database engine."
            ),
        },
        {
            "label": "Table Count",
            "value": f"{database_table_count:,}",
            "help": (
                "Number of user-created tables."
            ),
        },
        {
            "label": "Total Rows",
            "value": f"{total_database_rows:,}",
            "help": (
                "Combined number of rows in all tables."
            ),
        },
    ]
)


database_information_columns = (
    st.columns(2)
)

with database_information_columns[0]:
    st.text_input(
        "Database Path",
        value=str(DATABASE_PATH),
        disabled=True,
    )

    st.text_input(
        "Database Size",
        value=get_file_size(
            DATABASE_PATH
        ),
        disabled=True,
    )

with database_information_columns[1]:
    st.text_input(
        "Last Modified",
        value=get_file_modified_time(
            DATABASE_PATH
        ),
        disabled=True,
    )

    st.text_input(
        "Connection Message",
        value=database_message,
        disabled=True,
    )


render_status_badge(
    connected=database_connected,
    success_message=(
        "Database connection is available."
    ),
    failure_message=(
        "Database connection failed: "
        f"{database_message}"
    ),
)


if st.button(
    "Test Database Connection",
    use_container_width=True,
    key="test_database_connection",
):
    connected, message = (
        check_database_connection()
    )

    if connected:
        st.success(
            f"Database connection successful: "
            f"{message}"
        )
    else:
        st.error(
            f"Database connection failed: "
            f"{message}"
        )


if database_row_counts:
    with st.expander(
        "View database table statistics"
    ):
        table_statistics = [
            {
                "Table": table_name,
                "Row Count": row_count,
            }
            for table_name, row_count
            in database_row_counts.items()
        ]

        st.dataframe(
            table_statistics,
            use_container_width=True,
            hide_index=True,
        )


st.divider()


st.subheader("Knowledge Base Status")

metric_row(
    [
        {
            "label": "Source Documents",
            "value": f"{document_count:,}",
            "help": (
                "Number of supported documents "
                "in the docs directory."
            ),
        },
        {
            "label": "Knowledge Chunks",
            "value": f"{knowledge_chunk_count:,}",
            "help": (
                "Number of indexed document chunks."
            ),
        },
        {
            "label": "Embedding File",
            "value": (
                "Available"
                if EMBEDDING_PATH.exists()
                else "Missing"
            ),
            "help": (
                "Whether embeddings.npy exists."
            ),
        },
        {
            "label": "Index Status",
            "value": (
                "Ready"
                if knowledge_index_ready
                else "Not Ready"
            ),
            "help": (
                "Both embedding and chunk files "
                "must exist."
            ),
        },
    ]
)


knowledge_columns = st.columns(2)

with knowledge_columns[0]:
    st.text_input(
        "Knowledge Directory",
        value=str(KNOWLEDGE_DIR),
        disabled=True,
    )

    st.text_input(
        "Embedding File Size",
        value=get_file_size(
            EMBEDDING_PATH
        ),
        disabled=True,
    )

with knowledge_columns[1]:
    st.text_input(
        "Last Index Build",
        value=get_file_modified_time(
            CHUNKS_PATH
        ),
        disabled=True,
    )

    st.text_input(
        "Chunk Metadata Size",
        value=get_file_size(
            CHUNKS_PATH
        ),
        disabled=True,
    )


if knowledge_index_ready:
    st.success(
        "Knowledge index is ready for document retrieval."
    )
else:
    st.warning(
        "Knowledge index is incomplete. "
        "Build or rebuild the index before using RAG."
    )

    st.code(
        r"python scripts\build_knowledge_index.py",
        language="powershell",
    )


st.divider()


st.subheader("Platform Modules")

module_columns = st.columns(3)

with module_columns[0]:
    st.markdown("#### 📊 Dashboard")
    st.write(
        "Production KPIs, quality trends and "
        "abnormal measurement monitoring."
    )

    st.markdown("#### 🏥 Equipment Health")
    st.write(
        "Rule-based equipment health scoring "
        "and risk classification."
    )

with module_columns[1]:
    st.markdown("#### 🚨 Root Cause Analysis")
    st.write(
        "Evidence-based abnormal pattern and "
        "investigation-priority analysis."
    )

    st.markdown("#### 🤖 AI Assistant")
    st.write(
        "Unified SQL, RAG, hybrid analysis "
        "and query decomposition."
    )

with module_columns[2]:
    st.markdown("#### 📚 Knowledge Search")
    st.write(
        "Document retrieval with source references "
        "for manuals and SOPs."
    )

    st.markdown("#### ⚙️ Settings")
    st.write(
        "System configuration and service status."
    )


st.divider()


st.subheader("Architecture Overview")

st.code(
    """
User Question
      |
      v
Intent Router
      |
      +-- Database --------> Text-to-SQL
      |                         |
      |                         v
      |                    SQL Validator
      |                         |
      |                         v
      |                      Database
      |
      +-- Knowledge -------> RAG Retrieval
      |
      +-- Hybrid ----------> Query Decomposition
                                |
                                +-- Database Question
                                +-- Knowledge Question
                                |
                                v
                         Integrated Analysis
                                |
                                v
                     Answer + Chart + Evidence
""".strip(),
    language="text",
)


st.info(
    "Manufacturing AI Assistant is designed as a "
    "portfolio and demonstration platform. Health scores "
    "and root-cause outputs are monitoring indicators, "
    "not confirmed maintenance diagnoses."
)