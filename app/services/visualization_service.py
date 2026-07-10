from dataclasses import dataclass
from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


ChartType = Literal[
    "line",
    "bar",
    "scatter",
    "pie",
    "none",
]


@dataclass
class ChartResult:
    chart_type: ChartType
    title: str
    figure: go.Figure | None
    reason: str


DATE_KEYWORDS = {
    "date",
    "day",
    "month",
    "year",
    "time",
    "event_date",
    "order_date",
    "event_time",
}

CATEGORY_KEYWORDS = {
    "item",
    "product",
    "equipment",
    "machine",
    "line",
    "category",
    "status",
    "result_flag",
}

RATE_KEYWORDS = {
    "rate",
    "ratio",
    "percentage",
    "percent",
}

COUNT_KEYWORDS = {
    "count",
    "qty",
    "quantity",
    "total",
    "sum",
}


def is_date_column(
    dataframe: pd.DataFrame,
    column: str,
) -> bool:
    column_lower = column.lower()

    if any(
        keyword in column_lower
        for keyword in DATE_KEYWORDS
    ):
        try:
            pd.to_datetime(
                dataframe[column],
                errors="raise",
            )
            return True
        except Exception:
            pass

    return pd.api.types.is_datetime64_any_dtype(
        dataframe[column]
    )


def get_numeric_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    return dataframe.select_dtypes(
        include="number"
    ).columns.tolist()


def get_categorical_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    numeric_columns = set(
        get_numeric_columns(dataframe)
    )

    return [
        column
        for column in dataframe.columns
        if column not in numeric_columns
        and not is_date_column(
            dataframe,
            column,
        )
    ]


def choose_primary_numeric_column(
    numeric_columns: list[str],
) -> str | None:
    if not numeric_columns:
        return None

    priority_keywords = [
        "abnormal_rate",
        "rework_rate",
        "avg_weight_diff",
        "avg_weight",
        "measurement_count",
        "abnormal_count",
        "result_qty",
        "count",
        "rate",
    ]

    for keyword in priority_keywords:
        for column in numeric_columns:
            if keyword in column.lower():
                return column

    return numeric_columns[0]


def generate_chart_title(
    x_column: str,
    y_column: str,
    chart_type: ChartType,
) -> str:
    cleaned_x = x_column.replace(
        "_",
        " ",
    ).title()

    cleaned_y = y_column.replace(
        "_",
        " ",
    ).title()

    if chart_type == "line":
        return f"{cleaned_y} Trend by {cleaned_x}"

    if chart_type == "bar":
        return f"{cleaned_y} by {cleaned_x}"

    if chart_type == "scatter":
        return f"{cleaned_y} vs {cleaned_x}"

    if chart_type == "pie":
        return f"{cleaned_y} Distribution by {cleaned_x}"

    return "Query Result Visualization"


def create_line_chart(
    dataframe: pd.DataFrame,
    date_column: str,
    numeric_column: str,
) -> ChartResult:
    chart_df = dataframe.copy()

    chart_df[date_column] = pd.to_datetime(
        chart_df[date_column],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=[date_column]
    )

    chart_df = chart_df.sort_values(
        date_column
    )

    title = generate_chart_title(
        date_column,
        numeric_column,
        "line",
    )

    figure = px.line(
        chart_df,
        x=date_column,
        y=numeric_column,
        markers=True,
        title=title,
    )

    figure.update_layout(
        xaxis_title=date_column.replace(
            "_",
            " ",
        ).title(),
        yaxis_title=numeric_column.replace(
            "_",
            " ",
        ).title(),
        hovermode="x unified",
    )

    return ChartResult(
        chart_type="line",
        title=title,
        figure=figure,
        reason=(
            "A date/time column and a numeric column "
            "were detected."
        ),
    )


def create_bar_chart(
    dataframe: pd.DataFrame,
    category_column: str,
    numeric_column: str,
) -> ChartResult:
    chart_df = dataframe.copy()

    chart_df = chart_df.sort_values(
        numeric_column,
        ascending=False,
    )

    chart_df = chart_df.head(20)

    title = generate_chart_title(
        category_column,
        numeric_column,
        "bar",
    )

    figure = px.bar(
        chart_df,
        x=category_column,
        y=numeric_column,
        text=numeric_column,
        title=title,
    )

    figure.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
    )

    figure.update_layout(
        xaxis_title=category_column.replace(
            "_",
            " ",
        ).title(),
        yaxis_title=numeric_column.replace(
            "_",
            " ",
        ).title(),
    )

    return ChartResult(
        chart_type="bar",
        title=title,
        figure=figure,
        reason=(
            "A categorical column and a numeric column "
            "were detected."
        ),
    )


def create_horizontal_bar_chart(
    dataframe: pd.DataFrame,
    category_column: str,
    numeric_column: str,
) -> ChartResult:
    chart_df = dataframe.copy()

    chart_df = chart_df.sort_values(
        numeric_column,
        ascending=True,
    )

    chart_df = chart_df.tail(20)

    title = generate_chart_title(
        category_column,
        numeric_column,
        "bar",
    )

    figure = px.bar(
        chart_df,
        x=numeric_column,
        y=category_column,
        orientation="h",
        text=numeric_column,
        title=title,
    )

    figure.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
    )

    figure.update_layout(
        xaxis_title=numeric_column.replace(
            "_",
            " ",
        ).title(),
        yaxis_title=category_column.replace(
            "_",
            " ",
        ).title(),
    )

    return ChartResult(
        chart_type="bar",
        title=title,
        figure=figure,
        reason=(
            "A categorical ranking result was detected."
        ),
    )


def create_scatter_chart(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
) -> ChartResult:
    title = generate_chart_title(
        x_column,
        y_column,
        "scatter",
    )

    figure = px.scatter(
        dataframe,
        x=x_column,
        y=y_column,
        title=title,
        trendline=None,
    )

    figure.update_layout(
        xaxis_title=x_column.replace(
            "_",
            " ",
        ).title(),
        yaxis_title=y_column.replace(
            "_",
            " ",
        ).title(),
    )

    return ChartResult(
        chart_type="scatter",
        title=title,
        figure=figure,
        reason=(
            "Two numeric columns were detected."
        ),
    )


def create_pie_chart(
    dataframe: pd.DataFrame,
    category_column: str,
    numeric_column: str,
) -> ChartResult:
    title = generate_chart_title(
        category_column,
        numeric_column,
        "pie",
    )

    figure = px.pie(
        dataframe.head(10),
        names=category_column,
        values=numeric_column,
        title=title,
    )

    return ChartResult(
        chart_type="pie",
        title=title,
        figure=figure,
        reason=(
            "A small categorical distribution was detected."
        ),
    )


def generate_visualization(
    dataframe: pd.DataFrame,
    question: str = "",
) -> ChartResult:
    if dataframe.empty:
        return ChartResult(
            chart_type="none",
            title="",
            figure=None,
            reason="The query returned no data.",
        )

    if len(dataframe) == 1:
        return ChartResult(
            chart_type="none",
            title="",
            figure=None,
            reason=(
                "A single-row result is better displayed "
                "as a metric or table."
            ),
        )

    date_columns = [
        column
        for column in dataframe.columns
        if is_date_column(
            dataframe,
            column,
        )
    ]

    numeric_columns = get_numeric_columns(
        dataframe
    )

    categorical_columns = get_categorical_columns(
        dataframe
    )

    primary_numeric = (
        choose_primary_numeric_column(
            numeric_columns
        )
    )

    if date_columns and primary_numeric:
        return create_line_chart(
            dataframe=dataframe,
            date_column=date_columns[0],
            numeric_column=primary_numeric,
        )

    if (
        categorical_columns
        and primary_numeric
    ):
        category_column = categorical_columns[0]

        unique_count = dataframe[
            category_column
        ].nunique()

        question_lower = question.lower()

        if (
            "占比" in question
            or "比例" in question
            or "distribution" in question_lower
            or "share" in question_lower
        ) and unique_count <= 8:
            return create_pie_chart(
                dataframe=dataframe,
                category_column=category_column,
                numeric_column=primary_numeric,
            )

        if unique_count > 6:
            return create_horizontal_bar_chart(
                dataframe=dataframe,
                category_column=category_column,
                numeric_column=primary_numeric,
            )

        return create_bar_chart(
            dataframe=dataframe,
            category_column=category_column,
            numeric_column=primary_numeric,
        )

    if len(numeric_columns) >= 2:
        return create_scatter_chart(
            dataframe=dataframe,
            x_column=numeric_columns[0],
            y_column=numeric_columns[1],
        )

    return ChartResult(
        chart_type="none",
        title="",
        figure=None,
        reason=(
            "The result structure is not suitable "
            "for automatic visualization."
        ),
    )