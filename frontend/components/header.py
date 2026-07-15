import streamlit as st


def page_header(
    title: str,
    caption: str,
) -> None:
    st.title(title)
    st.caption(caption)
    st.divider()