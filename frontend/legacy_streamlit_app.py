from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
BASE_DIR = Path(__file__).resolve().parent.parent
from app.services.unified_assistant_service import (
    ask_unified_assistant,
)
from app.services.root_cause_service import (
    analyze_root_cause,
)
from app.services.manufacturing_service import (
    get_date_range,
    get_items,
    get_equipment,
    get_kpi_summary,
    get_daily_weight_trend,
    get_daily_abnormal_trend,
    get_equipment_summary,
    get_product_summary,
    get_recent_abnormal_records,
)
from app.services.equipment_health_service import (
    calculate_equipment_health,
)

st.set_page_config(
    page_title="Manufacturing AI Assistant",
    page_icon="🏭",
    layout="wide",
)


@st.cache_data(ttl=300)
def load_items() -> pd.DataFrame:
    return get_items()


@st.cache_data(ttl=300)
def load_equipment() -> pd.DataFrame:
    return get_equipment()


@st.cache_data(ttl=300)
def load_date_range() -> tuple[str, str]:
    return get_date_range()


st.title("🏭 Manufacturing AI Assistant")

st.caption(
    "Manufacturing production, quality and weight monitoring dashboard"
)


min_date_string, max_date_string = load_date_range()

min_date = datetime.strptime(
    min_date_string,
    "%Y-%m-%d",
).date()

max_date = datetime.strptime(
    max_date_string,
    "%Y-%m-%d",
).date()


items_df = load_items()
equipment_df = load_equipment()


item_options = {
    "All Products": None,
}

for _, row in items_df.iterrows():
    label = f"{row['item_cd']} - {row['item_name']}"
    item_options[label] = row["item_cd"]


equipment_options = {
    "All Equipment": None,
}

for _, row in equipment_df.iterrows():
    label = (
        f"{row['equipment_cd']} - "
        f"{row['equipment_name']}"
    )
    equipment_options[label] = row["equipment_cd"]


with st.sidebar:
    st.header("Filters")

    selected_date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_item_label = st.selectbox(
        "Product",
        options=list(item_options.keys()),
    )

    selected_equipment_label = st.selectbox(
        "Equipment",
        options=list(equipment_options.keys()),
    )

    if st.button(
        "Refresh Data",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    if st.button(
        "Clear Assistant Chat",
        use_container_width=True,
    ):
        st.session_state.unified_chat_history = []
        st.session_state.pop("pending_question", None)
        st.rerun()

if len(selected_date_range) == 2:
    start_date = selected_date_range[0].strftime(
        "%Y-%m-%d"
    )

    end_date = selected_date_range[1].strftime(
        "%Y-%m-%d"
    )
else:
    start_date = min_date_string
    end_date = max_date_string


selected_item_cd = item_options[
    selected_item_label
]

selected_equipment_cd = equipment_options[
    selected_equipment_label
]


kpi_summary = get_kpi_summary(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
    equipment_cd=selected_equipment_cd,
)


st.subheader("Production Overview")

metric_columns = st.columns(4)

with metric_columns[0]:
    st.metric(
        label="Production Orders",
        value=f"{kpi_summary['order_count']:,}",
    )

with metric_columns[1]:
    st.metric(
        label="Production Quantity",
        value=f"{kpi_summary['total_result_qty']:,}",
    )

with metric_columns[2]:
    st.metric(
        label="Measurement Count",
        value=f"{kpi_summary['measurement_count']:,}",
    )

with metric_columns[3]:
    st.metric(
        label="Abnormal Rate",
        value=f"{kpi_summary['abnormal_rate']:.2f}%",
    )


metric_columns_second = st.columns(4)

with metric_columns_second[0]:
    st.metric(
        label="Abnormal Count",
        value=f"{kpi_summary['abnormal_count']:,}",
    )

with metric_columns_second[1]:
    st.metric(
        label="Average Weight Difference",
        value=(
            f"{kpi_summary['avg_weight_diff']:.2f} g"
        ),
    )

with metric_columns_second[2]:
    st.metric(
        label="Rework Quantity",
        value=f"{kpi_summary['total_rework_qty']:,}",
    )

with metric_columns_second[3]:
    st.metric(
        label="Rework Rate",
        value=f"{kpi_summary['rework_rate']:.2f}%",
    )


st.divider()


daily_weight_df = get_daily_weight_trend(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
    equipment_cd=selected_equipment_cd,
)

daily_abnormal_df = get_daily_abnormal_trend(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
    equipment_cd=selected_equipment_cd,
)


chart_columns = st.columns(2)

with chart_columns[0]:
    st.subheader("Daily Average Weight Difference")

    if daily_weight_df.empty:
        st.info("No data available.")
    else:
        weight_diff_figure = px.line(
            daily_weight_df,
            x="event_date",
            y="avg_weight_diff",
            markers=True,
            labels={
                "event_date": "Date",
                "avg_weight_diff": (
                    "Average Weight Difference (g)"
                ),
            },
        )

        weight_diff_figure.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="Target",
        )

        weight_diff_figure.update_layout(
            xaxis_title="Date",
            yaxis_title="Weight Difference (g)",
        )

        st.plotly_chart(
            weight_diff_figure,
            use_container_width=True,
        )


with chart_columns[1]:
    st.subheader("Daily Abnormal Rate")

    if daily_abnormal_df.empty:
        st.info("No data available.")
    else:
        abnormal_figure = px.line(
            daily_abnormal_df,
            x="event_date",
            y="abnormal_rate",
            markers=True,
            labels={
                "event_date": "Date",
                "abnormal_rate": "Abnormal Rate (%)",
            },
        )

        abnormal_figure.update_layout(
            xaxis_title="Date",
            yaxis_title="Abnormal Rate (%)",
        )

        st.plotly_chart(
            abnormal_figure,
            use_container_width=True,
        )


st.divider()


equipment_summary_df = get_equipment_summary(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
)

product_summary_df = get_product_summary(
    start_date=start_date,
    end_date=end_date,
    equipment_cd=selected_equipment_cd,
)


ranking_columns = st.columns(2)

with ranking_columns[0]:
    st.subheader("Equipment Abnormal Rate")

    if equipment_summary_df.empty:
        st.info("No equipment data available.")
    else:
        equipment_figure = px.bar(
            equipment_summary_df,
            x="abnormal_rate",
            y="machine_name",
            orientation="h",
            text="abnormal_rate",
            labels={
                "abnormal_rate": "Abnormal Rate (%)",
                "machine_name": "Equipment",
            },
        )

        equipment_figure.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        equipment_figure.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
        )

        st.plotly_chart(
            equipment_figure,
            use_container_width=True,
        )


with ranking_columns[1]:
    st.subheader("Product Abnormal Rate")

    if product_summary_df.empty:
        st.info("No product data available.")
    else:
        product_figure = px.bar(
            product_summary_df,
            x="abnormal_rate",
            y="item_name",
            orientation="h",
            text="abnormal_rate",
            labels={
                "abnormal_rate": "Abnormal Rate (%)",
                "item_name": "Product",
            },
        )

        product_figure.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        product_figure.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
        )

        st.plotly_chart(
            product_figure,
            use_container_width=True,
        )


st.divider()


st.subheader("Weight Process Trend")

if daily_weight_df.empty:
    st.info("No weight trend data available.")
else:
    weight_process_figure = go.Figure()

    weight_process_figure.add_trace(
        go.Scatter(
            x=daily_weight_df["event_date"],
            y=daily_weight_df["avg_weight"],
            mode="lines+markers",
            name="Average Weight",
        )
    )

    weight_process_figure.add_trace(
        go.Scatter(
            x=daily_weight_df["event_date"],
            y=daily_weight_df["avg_std_weight"],
            mode="lines",
            name="Standard Weight",
            line={
                "dash": "dash",
            },
        )
    )

    weight_process_figure.update_layout(
        xaxis_title="Date",
        yaxis_title="Weight (g)",
        hovermode="x unified",
    )

    st.plotly_chart(
        weight_process_figure,
        use_container_width=True,
    )


st.divider()


st.subheader("Recent Abnormal Measurements")

abnormal_records_df = get_recent_abnormal_records(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
    equipment_cd=selected_equipment_cd,
    limit=100,
)

if abnormal_records_df.empty:
    st.success(
        "No abnormal measurements in the selected period."
    )
else:
    st.dataframe(
        abnormal_records_df,
        use_container_width=True,
        hide_index=True,
    )


with st.expander("Equipment Summary Data"):
    st.dataframe(
        equipment_summary_df,
        use_container_width=True,
        hide_index=True,
    )


with st.expander("Product Summary Data"):
    st.dataframe(
        product_summary_df,
        use_container_width=True,
        hide_index=True,
    )
st.divider()

st.subheader("Root Cause Analysis")

st.caption(
    "Automatically identify the equipment with the highest "
    "abnormal rate and analyze abnormal patterns."
)

if st.button(
    "Run Root Cause Analysis",
    use_container_width=True,
):
    try:
        with st.spinner(
            "Analyzing equipment, products, time periods "
            "and quality procedures..."
        ):
            root_cause_result = (
                analyze_root_cause()
            )

        st.markdown(
            root_cause_result.answer
        )

        st.info(
            "Analysis target: "
            f"{root_cause_result.target_equipment_name} "
            f"({root_cause_result.target_equipment_cd})"
        )

        chart_columns = st.columns(2)

        with chart_columns[0]:
            if (
                not root_cause_result
                .abnormal_type_df
                .empty
            ):
                figure = px.pie(
                    root_cause_result.abnormal_type_df,
                    names="result_flag",
                    values="abnormal_count",
                    title="Abnormal Type Distribution",
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                )

        with chart_columns[1]:
            if (
                not root_cause_result
                .product_contribution_df
                .empty
            ):
                figure = px.bar(
                    root_cause_result
                    .product_contribution_df,
                    x="abnormal_count",
                    y="item_name",
                    orientation="h",
                    title="Product Abnormal Contribution",
                )

                figure.update_layout(
                    yaxis={
                        "categoryorder": "total ascending"
                    }
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                )

        chart_columns_second = st.columns(2)

        with chart_columns_second[0]:
            if (
                not root_cause_result
                .hourly_contribution_df
                .empty
            ):
                figure = px.bar(
                    root_cause_result
                    .hourly_contribution_df,
                    x="production_hour",
                    y="abnormal_rate",
                    title="Hourly Abnormal Rate",
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                )

        with chart_columns_second[1]:
            if (
                not root_cause_result
                .trend_comparison_df
                .empty
            ):
                figure = px.bar(
                    root_cause_result
                    .trend_comparison_df,
                    x="period_name",
                    y="abnormal_rate",
                    title="Recent Trend Comparison",
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                )

        with st.expander(
            "View root-cause evidence"
        ):
            st.markdown(
                "#### Equipment Ranking"
            )

            st.dataframe(
                root_cause_result
                .equipment_ranking_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                "#### Abnormal Type Distribution"
            )

            st.dataframe(
                root_cause_result
                .abnormal_type_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                "#### Product Contribution"
            )

            st.dataframe(
                root_cause_result
                .product_contribution_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                "#### Daily Contribution"
            )

            st.dataframe(
                root_cause_result
                .daily_contribution_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown(
                "#### Hourly Contribution"
            )

            st.dataframe(
                root_cause_result
                .hourly_contribution_df,
                use_container_width=True,
                hide_index=True,
            )
            
    except Exception as exc:
        st.error(
            "Unable to run root-cause analysis: "
            f"{exc}"
        )

st.divider()

st.subheader("Equipment Health")

st.caption(
    "Health score combines abnormal rate, rework rate, "
    "recent trend and weight deviation."
)

health_result = calculate_equipment_health()

if health_result.summary_df.empty:
    st.info(
        "No equipment health data is available."
    )
else:
    health_summary_df = (
        health_result.summary_df
    )

    health_columns = st.columns(4)

    total_equipment = len(
        health_summary_df
    )

    healthy_count = int(
        (
            health_summary_df["health_status"]
            == "Healthy"
        ).sum()
    )

    risk_count = int(
        health_summary_df[
            "health_status"
        ].isin(
            [
                "Risk",
                "Critical",
            ]
        ).sum()
    )

    average_score = float(
        health_summary_df[
            "health_score"
        ].mean()
    )

    with health_columns[0]:
        st.metric(
            "Equipment Count",
            total_equipment,
        )

    with health_columns[1]:
        st.metric(
            "Average Health Score",
            f"{average_score:.1f}",
        )

    with health_columns[2]:
        st.metric(
            "Healthy Equipment",
            healthy_count,
        )

    with health_columns[3]:
        st.metric(
            "Risk Equipment",
            risk_count,
        )
health_chart_df = (
    health_summary_df.sort_values(
        "health_score",
        ascending=True,
    )
)

health_figure = px.bar(
    health_chart_df,
    x="health_score",
    y="machine_name",
    orientation="h",
    text="health_score",
    title="Equipment Health Score",
    hover_data=[
        "equipment_cd",
        "health_status",
        "abnormal_rate",
        "rework_rate",
        "abnormal_rate_change",
    ],
)

health_figure.update_traces(
    texttemplate="%{text:.1f}",
    textposition="outside",
)

health_figure.update_layout(
    xaxis_title="Health Score",
    yaxis_title="Equipment",
    xaxis_range=[0, 100],
)

st.plotly_chart(
    health_figure,
    use_container_width=True,
)
display_health_df = (
    health_summary_df.rename(
        columns={
            "health_rank": "Rank",
            "equipment_cd": "Equipment Code",
            "machine_name": "Equipment",
            "health_score": "Health Score",
            "health_status": "Status",
            "abnormal_rate": "Abnormal Rate (%)",
            "rework_rate": "Rework Rate (%)",
            "abnormal_rate_change": (
                "7-Day Rate Change (%p)"
            ),
        }
    )
)

st.dataframe(
    display_health_df,
    use_container_width=True,
    hide_index=True,
)
st.markdown("### Equipment Details")

equipment_labels = {
    (
        f"{row['equipment_cd']} - "
        f"{row['machine_name']}"
    ): row["equipment_cd"]
    for _, row in health_result.detail_df.iterrows()
}

selected_health_equipment_label = st.selectbox(
    "Select equipment for health details",
    options=list(equipment_labels.keys()),
    key="health_equipment_selector",
)

selected_health_equipment_cd = equipment_labels[
    selected_health_equipment_label
]

selected_health_rows = health_result.detail_df[
    health_result.detail_df["equipment_cd"]
    == selected_health_equipment_cd
]

if selected_health_rows.empty:
    st.info("No health details are available for this equipment.")
else:
    selected_health_row = selected_health_rows.iloc[0]

    detail_columns = st.columns(4)

    with detail_columns[0]:
        st.metric(
            "Health Score",
            f"{selected_health_row['health_score']:.1f}",
        )

    with detail_columns[1]:
        st.metric(
            "Abnormal Rate",
            f"{selected_health_row['abnormal_rate']:.2f}%",
        )

    with detail_columns[2]:
        st.metric(
            "Rework Rate",
            f"{selected_health_row['rework_rate']:.2f}%",
        )

    with detail_columns[3]:
        st.metric(
            "Recent Change",
            (
                f"{selected_health_row['abnormal_rate_change']:+.2f}"
                " %p"
            ),
        )

    detail_columns_second = st.columns(4)

    with detail_columns_second[0]:
        st.metric(
            "Measurement Count",
            f"{int(selected_health_row['measurement_count']):,}",
        )

    with detail_columns_second[1]:
        st.metric(
            "Abnormal Count",
            f"{int(selected_health_row['abnormal_count']):,}",
        )

    with detail_columns_second[2]:
        st.metric(
            "Average Absolute Weight Difference",
            (
                f"{selected_health_row['avg_abs_weight_diff']:.2f} g"
            ),
        )

    with detail_columns_second[3]:
        st.metric(
            "Status",
            selected_health_row["health_status"],
        )

with st.expander(
    "How is the health score calculated?"
):
    st.markdown(
        """
The score begins at **100 points**.

Penalties are applied for:

- High abnormal rate
- High rework rate
- Increasing abnormal rate during the latest seven days
- Large average weight deviation

Status thresholds:

- **Healthy:** 85–100
- **Watch:** 70–84.9
- **Risk:** 50–69.9
- **Critical:** below 50

This is a monitoring score, not a confirmed maintenance diagnosis.
"""
    )


st.divider()

st.subheader("Manufacturing AI Assistant")

st.caption(
    "Ask about production data, equipment performance, "
    "alarm handling or quality procedures."
)


if "unified_chat_history" not in st.session_state:
    st.session_state.unified_chat_history = []


def display_assistant_message(
    message: dict,
) -> None:
    st.markdown(
        message["answer"]
    )

    route = message.get(
        "route",
        "unknown",
    )

    confidence = message.get(
        "confidence",
        0,
    )

    st.caption(
        f"Route: {route} | "
        f"Confidence: {confidence:.2f}"
    )
    database_question = message.get(
        "database_question"
    )

    knowledge_question = message.get(
        "knowledge_question"
    )

    if database_question or knowledge_question:
        with st.expander(
            "View query decomposition"
        ):
            if database_question:
                st.markdown(
                    "**Database question**"
                )
                st.write(
                    database_question
                )

            if knowledge_question:
                st.markdown(
                    "**Knowledge question**"
                )
                st.write(
                    knowledge_question
                )
    chart_result = message.get(
        "chart_result"
    )

    if (
        chart_result is not None
        and chart_result.figure is not None
    ):
        st.plotly_chart(
            chart_result.figure,
            use_container_width=True,
        )

    sql = message.get(
        "sql"
    )

    if sql:
        with st.expander(
            "View generated SQL"
        ):
            st.code(
                sql,
                language="sql",
            )

    result_records = message.get(
        "result_records",
        [],
    )

    if result_records:
        with st.expander(
            "View query result"
        ):
            st.dataframe(
                pd.DataFrame(
                    result_records
                ),
                use_container_width=True,
                hide_index=True,
            )

    sources = message.get(
        "sources",
        [],
    )

    if sources:
        with st.expander(
            "View retrieved sources"
        ):
            for index, source in enumerate(
                sources,
                start=1,
            ):
                title = (
                    f"Source {index}: "
                    f"{source['source']}"
                )

                if source.get(
                    "page"
                ) is not None:
                    title += (
                        f" - Page "
                        f"{source['page']}"
                    )

                st.markdown(
                    f"**{title}**"
                )

                st.caption(
                    "Similarity score: "
                    f"{source['score']:.4f}"
                )

                st.write(
                    source["text"]
                )

                st.divider()


for message in st.session_state.unified_chat_history:
    with st.chat_message(
        message["role"]
    ):
        if message["role"] == "user":
            st.write(
                message["content"]
            )
        else:
            display_assistant_message(
                message
            )


st.markdown("#### 💡 Recommended Questions")

example_questions = [
    "哪个设备的异常率最高？",
    "最近30天每天的平均重量偏差是多少？",
    "E102报警应该怎么处理？",
    "连续三次UNDER应该怎么处理？",
]

example_columns = st.columns(2)

for index, example_question in enumerate(example_questions):
    with example_columns[index % 2]:
        if st.button(
            example_question,
            key=f"example_question_{index}",
            use_container_width=True,
        ):
            st.session_state.pending_question = example_question

user_question = st.chat_input(
    "Ask about production data, alarms or quality procedures..."
)

if not user_question:
    user_question = st.session_state.pop(
        "pending_question",
        None,
    )

if user_question:
    st.session_state.unified_chat_history.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        try:
            with st.spinner(
                "Analyzing your question..."
            ):
                response = (
                    ask_unified_assistant(
                        user_question
                    )
                )

            source_records = []

            if response.sources:
                source_records = [
                    {
                        "source": source.source,
                        "page": source.page,
                        "score": source.score,
                        "text": source.text,
                    }
                    for source in response.sources
                ]

            result_records = []

            if (
                response.result_df
                is not None
                and not response.result_df.empty
            ):
                result_records = (
                    response.result_df
                    .head(200)
                    .to_dict(
                        orient="records"
                    )
                )
            assistant_message = {
                "role": "assistant",
                "answer": response.answer,
                "route": response.route.intent,
                "confidence": response.route.confidence,
                "sql": response.sql,
                "result_records": result_records,
                "sources": source_records,
                "chart_result": response.chart_result,
                "database_question": (
                    response.database_question
                ),
                "knowledge_question": (
                    response.knowledge_question
                ),
            }

            display_assistant_message(
                assistant_message
            )

            st.session_state.unified_chat_history.append(
                assistant_message
            )

        except Exception as exc:
            error_message = (
                "Unable to process the question: "
                f"{exc}"
            )

            st.error(error_message)