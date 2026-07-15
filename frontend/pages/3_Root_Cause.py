from pathlib import Path
import sys

import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.services.root_cause_service import (
    analyze_root_cause,
)
from frontend.components.header import (
    page_header,
)
from frontend.components.metrics import (
    metric_row,
)
from frontend.components.tables import (
    dataframe_table,
    expandable_table,
)


st.set_page_config(
    page_title="Root Cause Analysis",
    page_icon="🚨",
    layout="wide",
)


page_header(
    title="🚨 Root Cause Analysis",
    caption=(
        "Identify abnormal patterns by equipment, product, "
        "time period and anomaly type."
    ),
)


st.info(
    "This analysis identifies abnormal patterns and investigation "
    "priorities. It does not prove a confirmed physical root cause."
)


if "root_cause_result" not in st.session_state:
    st.session_state.root_cause_result = None


action_columns = st.columns(
    [
        1,
        3,
    ]
)

with action_columns[0]:
    run_analysis = st.button(
        "Run Root Cause Analysis",
        type="primary",
        use_container_width=True,
    )

with action_columns[1]:
    st.caption(
        "The system automatically selects the equipment "
        "with the highest abnormal rate."
    )


if run_analysis:
    try:
        with st.spinner(
            "Analyzing equipment, products, anomaly types, "
            "time periods and SOP guidance..."
        ):
            st.session_state.root_cause_result = (
                analyze_root_cause()
            )

    except Exception as exc:
        st.error(
            "Unable to run root-cause analysis: "
            f"{exc}"
        )


root_cause_result = (
    st.session_state.root_cause_result
)


if root_cause_result is None:
    st.warning(
        "Run the analysis to generate a root-cause report."
    )

    st.stop()


st.success(
    "Analysis completed for "
    f"{root_cause_result.target_equipment_name} "
    f"({root_cause_result.target_equipment_cd})."
)


st.subheader("Analysis Summary")

st.markdown(
    root_cause_result.answer
)


st.divider()


equipment_ranking_df = (
    root_cause_result.equipment_ranking_df
)

target_row = equipment_ranking_df[
    equipment_ranking_df["equipment_cd"]
    == root_cause_result.target_equipment_cd
]


if target_row.empty:
    target_abnormal_rate = 0.0
    target_abnormal_count = 0
    target_measurement_count = 0

else:
    selected_target_row = target_row.iloc[0]

    target_abnormal_rate = float(
        selected_target_row[
            "abnormal_rate"
        ]
    )

    target_abnormal_count = int(
        selected_target_row[
            "abnormal_count"
        ]
    )

    target_measurement_count = int(
        selected_target_row[
            "measurement_count"
        ]
    )


top_product = "N/A"

if not root_cause_result.product_contribution_df.empty:
    top_product = str(
        root_cause_result
        .product_contribution_df
        .iloc[0]["item_name"]
    )


metric_row(
    [
        {
            "label": "Target Equipment",
            "value": (
                root_cause_result
                .target_equipment_cd
            ),
            "help": (
                "Equipment with the highest "
                "abnormal rate."
            ),
        },
        {
            "label": "Abnormal Rate",
            "value": (
                f"{target_abnormal_rate:.2f}%"
            ),
            "help": (
                "Percentage of OVER and UNDER "
                "measurements for the target equipment."
            ),
        },
        {
            "label": "Abnormal Count",
            "value": (
                f"{target_abnormal_count:,}"
            ),
            "help": (
                "Total abnormal measurements "
                "for the target equipment."
            ),
        },
        {
            "label": "Top Contributing Product",
            "value": top_product,
            "help": (
                "Product contributing the largest "
                "number of abnormal records."
            ),
        },
    ]
)


metric_row(
    [
        {
            "label": "Measurement Count",
            "value": (
                f"{target_measurement_count:,}"
            ),
        },
        {
            "label": "Document Sources",
            "value": (
                f"{len(root_cause_result.sources):,}"
            ),
        },
    ]
)


st.divider()


st.subheader("Abnormal Pattern Analysis")


chart_columns = st.columns(2)


with chart_columns[0]:
    abnormal_type_df = (
        root_cause_result
        .abnormal_type_df
    )

    if abnormal_type_df.empty:
        st.info(
            "No abnormal type data is available."
        )

    else:
        abnormal_type_figure = px.pie(
            abnormal_type_df,
            names="result_flag",
            values="abnormal_count",
            title="Abnormal Type Distribution",
            hole=0.35,
        )

        st.plotly_chart(
            abnormal_type_figure,
            use_container_width=True,
        )


with chart_columns[1]:
    product_contribution_df = (
        root_cause_result
        .product_contribution_df
    )

    if product_contribution_df.empty:
        st.info(
            "No product contribution data is available."
        )

    else:
        product_figure = px.bar(
            product_contribution_df.sort_values(
                "abnormal_count",
                ascending=True,
            ),
            x="abnormal_count",
            y="item_name",
            orientation="h",
            text="abnormal_count",
            title="Product Abnormal Contribution",
        )

        product_figure.update_traces(
            textposition="outside",
        )

        product_figure.update_layout(
            xaxis_title="Abnormal Count",
            yaxis_title="Product",
        )

        st.plotly_chart(
            product_figure,
            use_container_width=True,
        )


chart_columns_second = st.columns(2)


with chart_columns_second[0]:
    hourly_contribution_df = (
        root_cause_result
        .hourly_contribution_df
    )

    if hourly_contribution_df.empty:
        st.info(
            "No hourly contribution data is available."
        )

    else:
        hourly_figure = px.bar(
            hourly_contribution_df.sort_values(
                "production_hour",
                ascending=True,
            ),
            x="production_hour",
            y="abnormal_rate",
            text="abnormal_rate",
            title="Hourly Abnormal Rate",
        )

        hourly_figure.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        hourly_figure.update_layout(
            xaxis_title="Production Hour",
            yaxis_title="Abnormal Rate (%)",
        )

        st.plotly_chart(
            hourly_figure,
            use_container_width=True,
        )


with chart_columns_second[1]:
    trend_comparison_df = (
        root_cause_result
        .trend_comparison_df
    )

    if trend_comparison_df.empty:
        st.info(
            "No recent trend comparison is available."
        )

    else:
        trend_figure = px.bar(
            trend_comparison_df,
            x="period_name",
            y="abnormal_rate",
            text="abnormal_rate",
            title="Recent 7-Day Trend Comparison",
        )

        trend_figure.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )

        trend_figure.update_layout(
            xaxis_title="Period",
            yaxis_title="Abnormal Rate (%)",
        )

        st.plotly_chart(
            trend_figure,
            use_container_width=True,
        )


st.divider()


st.subheader("Evidence")


expandable_table(
    title="Equipment Ranking",
    dataframe=(
        root_cause_result
        .equipment_ranking_df
    ),
)

expandable_table(
    title="Abnormal Type Distribution",
    dataframe=(
        root_cause_result
        .abnormal_type_df
    ),
)

expandable_table(
    title="Product Contribution",
    dataframe=(
        root_cause_result
        .product_contribution_df
    ),
)

expandable_table(
    title="Daily Contribution",
    dataframe=(
        root_cause_result
        .daily_contribution_df
    ),
)

expandable_table(
    title="Hourly Contribution",
    dataframe=(
        root_cause_result
        .hourly_contribution_df
    ),
)

expandable_table(
    title="Trend Comparison",
    dataframe=(
        root_cause_result
        .trend_comparison_df
    ),
)


if root_cause_result.sources:
    with st.expander(
        "Retrieved SOP and Manual Sources"
    ):
        for index, source in enumerate(
            root_cause_result.sources,
            start=1,
        ):
            source_title = (
                f"Source {index}: "
                f"{source.source}"
            )

            if source.page is not None:
                source_title += (
                    f" - Page {source.page}"
                )

            st.markdown(
                f"**{source_title}**"
            )

            st.caption(
                "Similarity score: "
                f"{source.score:.4f}"
            )

            st.write(
                source.text
            )

            st.divider()