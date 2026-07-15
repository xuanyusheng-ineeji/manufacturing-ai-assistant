from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st


@dataclass
class DashboardFilterResult:
    start_date: str
    end_date: str
    item_cd: str | None
    equipment_cd: str | None


def build_item_options(
    items_df: pd.DataFrame,
) -> dict[str, str | None]:
    options: dict[str, str | None] = {
        "All Products": None,
    }

    for _, row in items_df.iterrows():
        label = (
            f"{row['item_cd']} - "
            f"{row['item_name']}"
        )

        options[label] = row["item_cd"]

    return options


def build_equipment_options(
    equipment_df: pd.DataFrame,
) -> dict[str, str | None]:
    options: dict[str, str | None] = {
        "All Equipment": None,
    }

    for _, row in equipment_df.iterrows():
        label = (
            f"{row['equipment_cd']} - "
            f"{row['equipment_name']}"
        )

        options[label] = row["equipment_cd"]

    return options


def dashboard_filters(
    min_date: date,
    max_date: date,
    items_df: pd.DataFrame,
    equipment_df: pd.DataFrame,
) -> DashboardFilterResult:
    item_options = build_item_options(
        items_df
    )

    equipment_options = (
        build_equipment_options(
            equipment_df
        )
    )

    with st.sidebar:
        st.header("Dashboard Filters")

        selected_date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="dashboard_date_range",
        )

        selected_item_label = st.selectbox(
            "Product",
            options=list(
                item_options.keys()
            ),
            key="dashboard_product",
        )

        selected_equipment_label = st.selectbox(
            "Equipment",
            options=list(
                equipment_options.keys()
            ),
            key="dashboard_equipment",
        )

        if st.button(
            "Refresh Dashboard",
            use_container_width=True,
            key="refresh_dashboard",
        ):
            st.cache_data.clear()
            st.rerun()

    if len(selected_date_range) == 2:
        start_date = (
            selected_date_range[0]
            .strftime("%Y-%m-%d")
        )

        end_date = (
            selected_date_range[1]
            .strftime("%Y-%m-%d")
        )
    else:
        start_date = min_date.strftime(
            "%Y-%m-%d"
        )

        end_date = max_date.strftime(
            "%Y-%m-%d"
        )

    return DashboardFilterResult(
        start_date=start_date,
        end_date=end_date,
        item_cd=item_options[
            selected_item_label
        ],
        equipment_cd=equipment_options[
            selected_equipment_label
        ],
    )