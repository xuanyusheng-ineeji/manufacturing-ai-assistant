import streamlit as st


def metric_card(
    label: str,
    value,
    delta: str | None = None,
):
    """
    Display a standard Streamlit metric card.
    """

    st.metric(
        label=label,
        value=value,
        delta=delta,
    )


def metric_row(
    metrics: list[dict],
):
    """
    Display multiple metric cards in one row.

    Example:
    [
        {"label":"Orders","value":120},
        {"label":"Abnormal Rate","value":"2.1%"},
    ]
    """

    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        with col:
            st.metric(
                metric["label"],
                metric["value"],
                metric.get("delta"),
            )