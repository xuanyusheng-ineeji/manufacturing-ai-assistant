import streamlit as st


GLOBAL_STYLES = """
<style>
    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 18px 20px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        font-weight: 700;
    }

    .section-description {
        color: rgba(128, 128, 128, 0.9);
        margin-top: -0.4rem;
        margin-bottom: 1.2rem;
    }

    .status-card {
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        background: rgba(128, 128, 128, 0.04);
    }

    .status-card-title {
        font-size: 0.85rem;
        color: rgba(128, 128, 128, 0.95);
        margin-bottom: 6px;
    }

    .status-card-value {
        font-size: 1.35rem;
        font-weight: 700;
    }

    .small-muted {
        color: rgba(128, 128, 128, 0.9);
        font-size: 0.85rem;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
"""


def apply_global_styles() -> None:
    st.markdown(
        GLOBAL_STYLES,
        unsafe_allow_html=True,
    )


def section_header(
    title: str,
    description: str | None = None,
) -> None:
    st.subheader(title)

    if description:
        st.markdown(
            (
                '<div class="section-description">'
                f"{description}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def status_card(
    title: str,
    value: str,
    description: str | None = None,
) -> None:
    description_html = ""

    if description:
        description_html = (
            '<div class="small-muted">'
            f"{description}"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-title">
                {title}
            </div>
            <div class="status-card-value">
                {value}
            </div>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )