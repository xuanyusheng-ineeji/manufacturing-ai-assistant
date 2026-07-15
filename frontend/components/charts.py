from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def line_chart(
    dataframe: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_label: str | None = None,
    y_label: str | None = None,
    add_zero_line: bool = False,
) -> None:
    if dataframe.empty:
        st.info("No data available.")
        return

    figure = px.line(
        dataframe,
        x=x,
        y=y,
        markers=True,
        title=title,
        labels={
            x: x_label or x.replace("_", " ").title(),
            y: y_label or y.replace("_", " ").title(),
        },
    )

    if add_zero_line:
        figure.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="Target",
        )

    figure.update_layout(
        hovermode="x unified",
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )


def horizontal_bar_chart(
    dataframe: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_label: str | None = None,
    y_label: str | None = None,
    text: str | None = None,
    value_suffix: str = "",
    max_rows: int = 20,
) -> None:
    if dataframe.empty:
        st.info("No data available.")
        return

    chart_df = dataframe.copy()

    if len(chart_df) > max_rows:
        chart_df = chart_df.head(max_rows)

    figure = px.bar(
        chart_df,
        x=x,
        y=y,
        orientation="h",
        text=text,
        title=title,
        labels={
            x: x_label or x.replace("_", " ").title(),
            y: y_label or y.replace("_", " ").title(),
        },
    )

    if text:
        figure.update_traces(
            texttemplate=(
                f"%{{text:.2f}}{value_suffix}"
            ),
            textposition="outside",
        )

    figure.update_layout(
        yaxis={
            "categoryorder": "total ascending",
        },
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )


def weight_process_chart(
    dataframe: pd.DataFrame,
    date_column: str = "event_date",
    actual_column: str = "avg_weight",
    target_column: str = "avg_std_weight",
    title: str = "Weight Process Trend",
) -> None:
    if dataframe.empty:
        st.info("No weight process data.")
        return

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=dataframe[date_column],
            y=dataframe[actual_column],
            mode="lines+markers",
            name="Average Weight",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=dataframe[date_column],
            y=dataframe[target_column],
            mode="lines",
            name="Standard Weight",
            line={
                "dash": "dash",
            },
        )
    )

    figure.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Weight (g)",
        hovermode="x unified",
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )