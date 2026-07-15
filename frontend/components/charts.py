import plotly.express as px
import streamlit as st


def horizontal_bar_chart(
    dataframe,
    x,
    y,
    title,
    text=None,
):
    if dataframe.empty:
        st.info("No data.")
        return

    figure = px.bar(
        dataframe,
        x=x,
        y=y,
        orientation="h",
        text=text,
        title=title,
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


def line_chart(
    dataframe,
    x,
    y,
    title,
):
    if dataframe.empty:
        st.info("No data.")
        return

    figure = px.line(
        dataframe,
        x=x,
        y=y,
        markers=True,
        title=title,
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )