from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.services.ai_query_service import (
    analyze_database_question,
)
from app.tools.sql_validator import SQLValidationError
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


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
        "Clear AI Chat",
        use_container_width=True,
    ):
        st.session_state.chat_history = []
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

st.subheader("AI Database Assistant")

st.caption(
    "Ask questions about products, equipment, orders "
    "and weight measurements."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            st.markdown(message["analysis"])

            with st.expander("View generated SQL"):
                st.code(message["sql"], language="sql")

            with st.expander("View query result"):
                result_records = message.get("result_records", [])
                if result_records:
                    st.dataframe(
                        pd.DataFrame(result_records),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No matching data was found.")

user_question = st.chat_input(
    "Example: Which equipment has the highest abnormal rate?"
)

if user_question:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_question}
    )

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        try:
            with st.spinner(
                "Querying and analyzing manufacturing data..."
            ):
                (
                    generated_sql,
                    query_result,
                    analysis,
                ) = analyze_database_question(user_question)

            st.markdown(analysis)

            with st.expander("View generated SQL"):
                st.code(generated_sql, language="sql")

            with st.expander("View query result"):
                if query_result.empty:
                    st.info("No matching data was found.")
                else:
                    st.dataframe(
                        query_result,
                        use_container_width=True,
                        hide_index=True,
                    )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "analysis": analysis,
                    "sql": generated_sql,
                    "result_records": (
                        query_result.head(200).to_dict(orient="records")
                    ),
                }
            )

        except SQLValidationError as exc:
            st.error(f"SQL safety validation failed: {exc}")

        except Exception as exc:
            st.error(f"Unable to process the question: {exc}")