import os
from dataclasses import dataclass

import pandas as pd

from app.services.ai_query_service import (
    analyze_database_question,
)
from app.services.knowledge_service import (
    answer_knowledge_question,
)
from app.services.retrieval_service import (
    RetrievalResult,
)
from app.services.text_to_sql_service import (
    get_llm_client,
)
from app.services.visualization_service import (
    ChartResult,
)
from app.services.query_decomposition_service import (
    DecomposedQuery,
    decompose_hybrid_question,
)

HYBRID_SYSTEM_PROMPT = """
You are a careful manufacturing operations analyst.

Create one integrated answer using:

1. Actual manufacturing database findings.
2. Retrieved SOP or equipment manual content.

Rules:
1. Database values are observations, not confirmed causes.
2. Document procedures are guidance, not proof that a specific cause occurred.
3. Never invent values, equipment, alarms or procedures.
4. Clearly separate observed data from recommended checks.
5. Do not claim causality unless the supplied information proves it.
6. Use the same language as the user's question.
7. Include important numerical results.
8. Cite document guidance using [Source 1], [Source 2], etc.
9. If database results or document evidence are insufficient, state the limitation.
10. Keep the answer practical and concise.

Preferred structure:

### 数据结论
Summarize the actual database findings.

### 文档依据
Summarize relevant SOP or manual instructions.

### 综合建议
Explain what should be checked next without presenting speculation as fact.
"""


@dataclass
class HybridAnalysisResult:
    answer: str
    sql: str
    result_df: pd.DataFrame
    chart_result: ChartResult
    sources: list[RetrievalResult]
    decomposition: DecomposedQuery


def build_source_context(
    sources: list[RetrievalResult],
) -> str:
    context_parts: list[str] = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        page_text = (
            f", page {source.page}"
            if source.page is not None
            else ""
        )

        context_parts.append(
            f"[Source {index}] "
            f"{source.source}{page_text}\n"
            f"{source.text}"
        )

    return "\n\n".join(context_parts)


def dataframe_to_text(
    dataframe: pd.DataFrame,
    max_rows: int = 30,
) -> str:
    if dataframe.empty:
        return "The database query returned no rows."

    preview_df = dataframe.head(max_rows)

    return (
        f"Total rows: {len(dataframe)}\n"
        f"Columns: {', '.join(dataframe.columns)}\n\n"
        f"{preview_df.to_csv(index=False)}"
    )


def analyze_hybrid_question(
    question: str,
) -> HybridAnalysisResult:
    decomposition = decompose_hybrid_question(
        question
    )

    (
        sql,
        result_df,
        database_analysis,
        chart_result,
    ) = analyze_database_question(
        decomposition.database_question
    )

    knowledge_result = answer_knowledge_question(
        decomposition.knowledge_question
    )

    source_context = build_source_context(
        knowledge_result.sources
    )

    database_context = dataframe_to_text(
        result_df
    )

    user_prompt = f"""
Original hybrid question:

{question}

Decomposed database question:

{decomposition.database_question}

Decomposed knowledge question:

{decomposition.knowledge_question}

Database analysis:

{database_analysis}

Executed SQL:

{sql}

Database result:

{database_context}

Document answer:

{knowledge_result.answer}

Retrieved document context:

{source_context}

Create one integrated response that answers the original hybrid question.
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
                "content": HYBRID_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
        max_tokens=1000,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The language model returned "
            "an empty hybrid analysis."
        )

    return HybridAnalysisResult(
        answer=content.strip(),
        sql=sql,
        result_df=result_df,
        chart_result=chart_result,
        sources=knowledge_result.sources,
        decomposition=decomposition,
    )