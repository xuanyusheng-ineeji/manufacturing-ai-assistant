from pathlib import Path
import sys

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.services.unified_assistant_service import (
    ask_unified_assistant,
)
from frontend.components.header import (
    page_header,
)
from frontend.components.styles import (
    apply_global_styles,
)

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
)
apply_global_styles()

page_header(
    title="🤖 Manufacturing AI Assistant",
    caption=(
        "Ask about production data, equipment performance, "
        "alarm handling or quality procedures."
    ),
)


if "unified_chat_history" not in st.session_state:
    st.session_state.unified_chat_history = []


if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def display_assistant_message(
    message: dict,
) -> None:
    st.markdown(
        message["answer"]
    )

    route = message.get(
        "route",
        "unknown",
    )

    confidence = message.get(
        "confidence",
        0.0,
    )

    st.caption(
        f"Route: {route} | "
        f"Confidence: {confidence:.2f}"
    )

    database_question = message.get(
        "database_question"
    )

    knowledge_question = message.get(
        "knowledge_question"
    )

    if database_question or knowledge_question:
        with st.expander(
            "View query decomposition"
        ):
            if database_question:
                st.markdown(
                    "**Database question**"
                )

                st.write(
                    database_question
                )

            if knowledge_question:
                st.markdown(
                    "**Knowledge question**"
                )

                st.write(
                    knowledge_question
                )

    chart_result = message.get(
        "chart_result"
    )

    if (
        chart_result is not None
        and chart_result.figure is not None
    ):
        st.plotly_chart(
            chart_result.figure,
            use_container_width=True,
        )

    sql = message.get(
        "sql"
    )

    if sql:
        with st.expander(
            "View generated SQL"
        ):
            st.code(
                sql,
                language="sql",
            )

    result_records = message.get(
        "result_records",
        [],
    )

    if result_records:
        with st.expander(
            "View query result"
        ):
            st.dataframe(
                pd.DataFrame(
                    result_records
                ),
                use_container_width=True,
                hide_index=True,
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


with st.sidebar:
    st.subheader("AI Assistant")

    if st.button(
        "Clear Chat",
        use_container_width=True,
        key="clear_unified_chat",
    ):
        st.session_state.unified_chat_history = []
        st.session_state.pending_question = None
        st.rerun()

    st.caption(
        "The assistant automatically routes questions "
        "to SQL, RAG, hybrid analysis or general response."
    )


st.markdown("### Recommended Questions")

recommended_questions = [
    "哪个设备的异常率最高？",
    "最近30天每天的平均重量偏差是多少？",
    "E102报警应该怎么处理？",
    "哪个设备异常率最高，根据SOP应该检查什么？",
]

question_columns = st.columns(2)

for index, question in enumerate(
    recommended_questions
):
    with question_columns[index % 2]:
        if st.button(
            question,
            use_container_width=True,
            key=f"recommended_question_{index}",
        ):
            st.session_state.pending_question = question
            st.rerun()


st.divider()


for message in (
    st.session_state.unified_chat_history
):
    with st.chat_message(
        message["role"]
    ):
        if message["role"] == "user":
            st.write(
                message["content"]
            )

        else:
            display_assistant_message(
                message
            )


typed_question = st.chat_input(
    "Ask a manufacturing question..."
)


user_question = (
    st.session_state.pending_question
    or typed_question
)


if user_question:
    st.session_state.pending_question = None

    st.session_state.unified_chat_history.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.write(
            user_question
        )

    with st.chat_message("assistant"):
        try:
            with st.spinner(
                "Analyzing your question..."
            ):
                response = ask_unified_assistant(
                    user_question
                )

            source_records = []

            if response.sources:
                source_records = [
                    {
                        "source": source.source,
                        "page": source.page,
                        "score": source.score,
                        "text": source.text,
                    }
                    for source in response.sources
                ]

            result_records = []

            if (
                response.result_df is not None
                and not response.result_df.empty
            ):
                result_records = (
                    response.result_df
                    .head(200)
                    .to_dict(
                        orient="records"
                    )
                )

            assistant_message = {
                "role": "assistant",
                "answer": response.answer,
                "route": response.route.intent,
                "confidence": (
                    response.route.confidence
                ),
                "sql": response.sql,
                "result_records": (
                    result_records
                ),
                "sources": source_records,
                "chart_result": (
                    response.chart_result
                ),
                "database_question": (
                    response.database_question
                ),
                "knowledge_question": (
                    response.knowledge_question
                ),
            }

            display_assistant_message(
                assistant_message
            )

            st.session_state.unified_chat_history.append(
                assistant_message
            )

        except Exception as exc:
            st.error(
                "Unable to process the question: "
                f"{exc}"
            )