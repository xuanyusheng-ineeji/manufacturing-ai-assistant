from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.services.manufacturing_service import (
    get_daily_abnormal_trend,
    get_daily_weight_trend,
    get_date_range,
    get_equipment,
    get_equipment_summary,
    get_items,
    get_kpi_summary,
    get_product_summary,
    get_recent_abnormal_records,
)
from frontend.components.charts import (
    horizontal_bar_chart,
    line_chart,
    weight_process_chart,
)
from frontend.components.filters import dashboard_filters
from frontend.components.metrics import metric_row
from frontend.components.tables import (
    dataframe_table,
    expandable_table,
)

st.set_page_config(
    page_title="Manufacturing Dashboard",
    page_icon="📊",
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


st.title("📊 Manufacturing Dashboard")

st.caption(
    "Production overview, quality monitoring and "
    "weight process analysis."
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

filter_result = dashboard_filters(
    min_date=min_date,
    max_date=max_date,
    items_df=items_df,
    equipment_df=equipment_df,
)

start_date = filter_result.start_date
end_date = filter_result.end_date
selected_item_cd = filter_result.item_cd
selected_equipment_cd = filter_result.equipment_cd


kpi_summary = get_kpi_summary(
    start_date=start_date,
    end_date=end_date,
    item_cd=selected_item_cd,
    equipment_cd=selected_equipment_cd,
)


st.subheader("Production Overview")

metric_row(
    [
        {
            "label": "Production Orders",
            "value": f"{kpi_summary['order_count']:,}",
            "help": (
                "Number of production orders included "
                "in the selected period."
            ),
        },
        {
            "label": "Production Quantity",
            "value": f"{kpi_summary['total_result_qty']:,}",
            "help": "Total completed production quantity.",
        },
        {
            "label": "Measurement Count",
            "value": f"{kpi_summary['measurement_count']:,}",
            "help": "Total number of weight measurements.",
        },
        {
            "label": "Abnormal Rate",
            "value": f"{kpi_summary['abnormal_rate']:.2f}%",
            "help": (
                "Percentage of OVER and UNDER measurements."
            ),
        },
    ]
)

metric_row(
    [
        {
            "label": "Abnormal Count",
            "value": f"{kpi_summary['abnormal_count']:,}",
            "help": "Total number of OVER and UNDER records.",
        },
        {
            "label": "Average Weight Difference",
            "value": f"{kpi_summary['avg_weight_diff']:.2f} g",
            "help": (
                "Average measured weight minus standard weight."
            ),
        },
        {
            "label": "Rework Quantity",
            "value": f"{kpi_summary['total_rework_qty']:,}",
            "help": (
                "Total rework quantity from production orders."
            ),
        },
        {
            "label": "Rework Rate",
            "value": f"{kpi_summary['rework_rate']:.2f}%",
            "help": (
                "Rework quantity divided by completed "
                "production quantity."
            ),
        },
    ]
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
    line_chart(
        dataframe=daily_weight_df,
        x="event_date",
        y="avg_weight_diff",
        title="Daily Average Weight Difference",
        x_label="Date",
        y_label="Average Weight Difference (g)",
        add_zero_line=True,
    )

with chart_columns[1]:
    line_chart(
        dataframe=daily_abnormal_df,
        x="event_date",
        y="abnormal_rate",
        title="Daily Abnormal Rate",
        x_label="Date",
        y_label="Abnormal Rate (%)",
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
    horizontal_bar_chart(
        dataframe=equipment_summary_df,
        x="abnormal_rate",
        y="machine_name",
        title="Equipment Abnormal Rate",
        x_label="Abnormal Rate (%)",
        y_label="Equipment",
        text="abnormal_rate",
        value_suffix="%",
    )

with ranking_columns[1]:
    horizontal_bar_chart(
        dataframe=product_summary_df,
        x="abnormal_rate",
        y="item_name",
        title="Product Abnormal Rate",
        x_label="Abnormal Rate (%)",
        y_label="Product",
        text="abnormal_rate",
        value_suffix="%",
    )


st.divider()


weight_process_chart(
    dataframe=daily_weight_df,
    title="Weight Process Trend",
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
    dataframe_table(
        abnormal_records_df
    )


expandable_table(
    title="Equipment Summary Data",
    dataframe=equipment_summary_df,
)

expandable_table(
    title="Product Summary Data",
    dataframe=product_summary_df,
)