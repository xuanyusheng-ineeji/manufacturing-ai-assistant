import pandas as pd
import streamlit as st


def dataframe_table(
    dataframe: pd.DataFrame,
    empty_message: str = "No data available.",
) -> None:
    if dataframe.empty:
        st.info(empty_message)
        return

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


def expandable_table(
    title: str,
    dataframe: pd.DataFrame,
    empty_message: str = "No data available.",
) -> None:
    with st.expander(title):
        dataframe_table(
            dataframe=dataframe,
            empty_message=empty_message,
        )