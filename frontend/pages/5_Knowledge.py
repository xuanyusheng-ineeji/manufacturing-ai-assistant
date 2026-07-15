from pathlib import Path
import sys

import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.services.knowledge_service import (
    answer_knowledge_question,
)
from frontend.components.header import (
    page_header,
)


st.set_page_config(
    page_title="Knowledge Search",
    page_icon="📚",
    layout="wide",
)


page_header(
    title="📚 Manufacturing Knowledge Search",
    caption=(
        "Search equipment manuals, quality procedures "
        "and SOP documents with source references."
    ),
)


if "knowledge_history" not in st.session_state:
    st.session_state.knowledge_history = []


if "knowledge_pending_question" not in st.session_state:
    st.session_state.knowledge_pending_question = None


with st.sidebar:
    st.subheader("Knowledge Search")

    if st.button(
        "Clear Search History",
        use_container_width=True,
        key="clear_knowledge_history",
    ):
        st.session_state.knowledge_history = []
        st.session_state.knowledge_pending_question = None
        st.rerun()

    st.caption(
        "Answers are generated only from indexed "
        "manuals and SOP documents."
    )


st.info(
    "The assistant will not invent procedures that are "
    "not supported by the retrieved documents."
)


st.markdown("### Recommended Questions")

recommended_questions = [
    "E102报警是什么意思？",
    "连续三次UNDER应该怎么处理？",
    "什么时候需要校准重量传感器？",
    "产品切换时应该做什么？",
]

question_columns = st.columns(2)

for index, question in enumerate(
    recommended_questions
):
    with question_columns[index % 2]:
        if st.button(
            question,
            use_container_width=True,
            key=f"knowledge_question_{index}",
        ):
            st.session_state.knowledge_pending_question = (
                question
            )
            st.rerun()


st.divider()


for message in st.session_state.knowledge_history:
    with st.chat_message(
        message["role"]
    ):
        if message["role"] == "user":
            st.write(
                message["content"]
            )

        else:
            st.markdown(
                message["answer"]
            )

            sources = message.get(
                "sources",
                [],
            )

            if sources:
                with st.expander(
                    "View retrieved sources"
                ):
                    for index, source in enumerate(
                        sources,
                        start=1,
                    ):
                        title = (
                            f"Source {index}: "
                            f"{source['source']}"
                        )

                        if source.get(
                            "page"
                        ) is not None:
                            title += (
                                f" - Page "
                                f"{source['page']}"
                            )

                        st.markdown(
                            f"**{title}**"
                        )

                        st.caption(
                            "Similarity score: "
                            f"{source['score']:.4f}"
                        )

                        st.write(
                            source["text"]
                        )

                        st.divider()


typed_question = st.chat_input(
    "Ask about alarms, calibration, SOPs or procedures..."
)


knowledge_question = (
    st.session_state.knowledge_pending_question
    or typed_question
)


if knowledge_question:
    st.session_state.knowledge_pending_question = None

    st.session_state.knowledge_history.append(
        {
            "role": "user",
            "content": knowledge_question,
        }
    )

    with st.chat_message("user"):
        st.write(
            knowledge_question
        )

    with st.chat_message("assistant"):
        try:
            with st.spinner(
                "Searching manufacturing documents..."
            ):
                result = answer_knowledge_question(
                    knowledge_question
                )

            st.markdown(
                result.answer
            )

            source_records = [
                {
                    "source": source.source,
                    "page": source.page,
                    "score": source.score,
                    "text": source.text,
                }
                for source in result.sources
            ]

            if source_records:
                with st.expander(
                    "View retrieved sources"
                ):
                    for index, source in enumerate(
                        source_records,
                        start=1,
                    ):
                        title = (
                            f"Source {index}: "
                            f"{source['source']}"
                        )

                        if source.get(
                            "page"
                        ) is not None:
                            title += (
                                f" - Page "
                                f"{source['page']}"
                            )

                        st.markdown(
                            f"**{title}**"
                        )

                        st.caption(
                            "Similarity score: "
                            f"{source['score']:.4f}"
                        )

                        st.write(
                            source["text"]
                        )

                        st.divider()

            st.session_state.knowledge_history.append(
                {
                    "role": "assistant",
                    "answer": result.answer,
                    "sources": source_records,
                }
            )

        except Exception as exc:
            st.error(
                "Unable to search the knowledge base: "
                f"{exc}"
            )