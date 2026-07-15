from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.services.equipment_health_service import (
    calculate_equipment_health,
)
from frontend.components.header import (
    page_header,
)
from frontend.components.metrics import (
    metric_row,
)
from frontend.components.tables import (
    dataframe_table,
)

from frontend.components.styles import (
    apply_global_styles,
)
st.set_page_config(
    page_title="Equipment Health",
    page_icon="🏥",
    layout="wide",
)
apply_global_styles()

page_header(
    title="🏥 Equipment Health",
    caption=(
        "Monitor equipment condition using health scores "
        "based on abnormal rate, rework, recent trend "
        "and weight deviation."
    ),
)


health_result = calculate_equipment_health()


if health_result.summary_df.empty:
    st.info(
        "No equipment health data is available."
    )

    st.stop()


health_summary_df = health_result.summary_df
health_detail_df = health_result.detail_df


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


metric_row(
    [
        {
            "label": "Equipment Count",
            "value": f"{total_equipment:,}",
            "help": (
                "Total number of equipment records "
                "included in health scoring."
            ),
        },
        {
            "label": "Average Health Score",
            "value": f"{average_score:.1f}",
            "help": (
                "Average health score across "
                "all equipment."
            ),
        },
        {
            "label": "Healthy Equipment",
            "value": f"{healthy_count:,}",
            "help": (
                "Equipment with a health score "
                "of 85 or higher."
            ),
        },
        {
            "label": "Risk Equipment",
            "value": f"{risk_count:,}",
            "help": (
                "Equipment classified as Risk "
                "or Critical."
            ),
        },
    ]
)


st.divider()


st.subheader("Equipment Health Ranking")


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
    yaxis={
        "categoryorder": "total ascending",
    },
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

dataframe_table(
    display_health_df
)


st.divider()


st.subheader("Equipment Details")


equipment_labels = {
    (
        f"{row['equipment_cd']} - "
        f"{row['machine_name']}"
    ): row["equipment_cd"]
    for _, row in health_detail_df.iterrows()
}


selected_equipment_label = st.selectbox(
    "Select equipment",
    options=list(
        equipment_labels.keys()
    ),
    key="equipment_health_selector",
)


selected_equipment_cd = equipment_labels[
    selected_equipment_label
]


selected_rows = health_detail_df[
    health_detail_df["equipment_cd"]
    == selected_equipment_cd
]


if selected_rows.empty:
    st.info(
        "No health details are available "
        "for the selected equipment."
    )

else:
    selected_row = selected_rows.iloc[0]

    metric_row(
        [
            {
                "label": "Health Score",
                "value": (
                    f"{selected_row['health_score']:.1f}"
                ),
                "help": (
                    "Combined monitoring score "
                    "from 0 to 100."
                ),
            },
            {
                "label": "Abnormal Rate",
                "value": (
                    f"{selected_row['abnormal_rate']:.2f}%"
                ),
                "help": (
                    "Percentage of OVER and UNDER "
                    "measurements."
                ),
            },
            {
                "label": "Rework Rate",
                "value": (
                    f"{selected_row['rework_rate']:.2f}%"
                ),
                "help": (
                    "Rework quantity divided by "
                    "completed production quantity."
                ),
            },
            {
                "label": "Recent Change",
                "value": (
                    f"{selected_row['abnormal_rate_change']:+.2f} %p"
                ),
                "help": (
                    "Change between the latest seven days "
                    "and the previous seven days."
                ),
            },
        ]
    )

    metric_row(
        [
            {
                "label": "Measurement Count",
                "value": (
                    f"{int(selected_row['measurement_count']):,}"
                ),
            },
            {
                "label": "Abnormal Count",
                "value": (
                    f"{int(selected_row['abnormal_count']):,}"
                ),
            },
            {
                "label": (
                    "Average Absolute Weight Difference"
                ),
                "value": (
                    f"{selected_row['avg_abs_weight_diff']:.2f} g"
                ),
            },
            {
                "label": "Status",
                "value": selected_row[
                    "health_status"
                ],
            },
        ]
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