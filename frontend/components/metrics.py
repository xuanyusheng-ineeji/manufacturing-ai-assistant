import streamlit as st


def metric_card(
    label: str,
    value,
    delta: str | None = None,
    help_text: str | None = None,
) -> None:
    """
    Display one standard Streamlit metric card.
    """

    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text,
    )


def metric_row(
    metrics: list[dict],
) -> None:
    """
    Display multiple metric cards in one row.

    Example:
    [
        {
            "label": "Orders",
            "value": 120,
            "delta": "+5",
            "help": "Number of production orders.",
        },
        {
            "label": "Abnormal Rate",
            "value": "2.1%",
        },
    ]
    """

    if not metrics:
        return

    columns = st.columns(len(metrics))

    for column, metric in zip(
        columns,
        metrics,
    ):
        with column:
            st.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta"),
                help=metric.get("help"),
            )