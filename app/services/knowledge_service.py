import os
from dataclasses import dataclass

from app.services.retrieval_service import (
    RetrievalResult,
    retrieve_documents,
)
from app.services.text_to_sql_service import (
    get_llm_client,
)


KNOWLEDGE_SYSTEM_PROMPT = """
You are a manufacturing knowledge assistant.

Answer the user's question using only the supplied document context.

Rules:
1. Do not use unsupported external knowledge.
2. Do not invent procedures, alarm meanings or safety instructions.
3. If the context does not contain the answer, clearly state that the
   available documents do not provide enough information.
4. Answer in the same language as the user's question.
5. Keep safety-related steps in their original order.
6. Clearly distinguish required actions from possible checks.
7. Cite the source using [Source 1], [Source 2], and so on.
8. Do not cite a source that does not support the statement.
9. Keep the response concise and practical.
"""


@dataclass
class KnowledgeAnswer:
    answer: str
    sources: list[RetrievalResult]


def build_context(
    results: list[RetrievalResult],
) -> str:
    context_parts: list[str] = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        page_information = (
            f", page {result.page}"
            if result.page is not None
            else ""
        )

        context_parts.append(
            f"[Source {index}] "
            f"{result.source}"
            f"{page_information}\n"
            f"{result.text}"
        )

    return "\n\n".join(context_parts)


def answer_knowledge_question(
    question: str,
) -> KnowledgeAnswer:
    results = retrieve_documents(
        question=question,
        top_k=4,
    )

    if not results:
        return KnowledgeAnswer(
            answer=(
                "当前知识库中没有检索到足够相关的内容，"
                "因此无法依据现有文档回答该问题。"
            ),
            sources=[],
        )

    context = build_context(results)

    user_prompt = f"""
Document context:

{context}

User question:

{question}

Answer using only the document context.
"""

    client = get_llm_client()

    model = os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-chat",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": KNOWLEDGE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
        max_tokens=700,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The language model returned "
            "an empty knowledge answer."
        )

    return KnowledgeAnswer(
        answer=content.strip(),
        sources=results,
    )