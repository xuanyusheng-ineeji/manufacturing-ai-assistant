import streamlit as st


def page_header(
    title,
    caption,
):
    st.title(title)

    st.caption(caption)

    st.divider()