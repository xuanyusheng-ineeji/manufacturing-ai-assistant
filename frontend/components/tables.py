import streamlit as st


def dataframe_table(
    dataframe,
):
    if dataframe.empty:
        st.info("No data.")
        return

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )