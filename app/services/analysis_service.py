import pandas as pd

from app.services.text_to_sql_service import get_llm_client, get_llm_model


MAX_PREVIEW_ROWS = 50
MAX_CONTEXT_CHARACTERS = 12_000


ANALYSIS_SYSTEM_PROMPT = """
You are a careful manufacturing data analyst.

Analyze the SQL query result supplied by the application.

Rules:
1. Base every conclusion only on the supplied query result.
2. Never invent values, columns, equipment, products or dates.
3. Do not claim causality from descriptive data.
4. Clearly distinguish:
   - observed facts;
   - possible interpretations;
   - recommended follow-up checks.
5. If the result is insufficient to answer the question, say so clearly.
6. Include important numerical values when they are available.
7. Do not explain SQL syntax unless explicitly requested.
8. Do not mention that you are an AI.
9. Answer in the same language as the user's question.
10. Keep the answer concise and suitable for a manufacturing manager.
11. Do not recommend checking variables that do not exist in the supplied
    result as if they were already verified.
12. Suggestions may be provided, but they must be labeled as follow-up
    checks rather than confirmed causes.

Preferred response structure:

### 分析结论
A concise answer to the user's question.

### 关键发现
Important numerical observations.

### 建议检查
Reasonable next checks based on the available evidence.

If there is too little data, explain the limitation instead.
"""


def dataframe_to_context(
    dataframe: pd.DataFrame,
) -> str:
    """
    Convert a DataFrame into a limited text context for the LLM.

    The complete DataFrame is not always sent because query results
    can become very large.
    """

    if dataframe.empty:
        return (
            "The SQL query returned an empty result. "
            "There are no rows available for analysis."
        )

    preview_df = dataframe.head(MAX_PREVIEW_ROWS).copy()

    basic_information = [
        f"Total rows returned: {len(dataframe)}",
        f"Total columns: {len(dataframe.columns)}",
        "Columns: " + ", ".join(map(str, dataframe.columns)),
    ]

    data_types = [
        f"- {column}: {dataframe[column].dtype}"
        for column in dataframe.columns
    ]

    null_counts = dataframe.isna().sum()
    null_information = [
        f"- {column}: {int(count)}"
        for column, count in null_counts.items()
        if count > 0
    ]

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    numeric_summary = ""

    if numeric_columns:
        described_df = (
            dataframe[numeric_columns]
            .describe()
            .round(4)
            .transpose()
            .reset_index()
            .rename(columns={"index": "column"})
        )

        numeric_summary = described_df.to_csv(
            index=False
        )

    preview_csv = preview_df.to_csv(
        index=False
    )

    context_parts = [
        "BASIC INFORMATION",
        "\n".join(basic_information),
        "",
        "DATA TYPES",
        "\n".join(data_types),
        "",
    ]

    if null_information:
        context_parts.extend(
            [
                "NULL COUNTS",
                "\n".join(null_information),
                "",
            ]
        )

    if numeric_summary:
        context_parts.extend(
            [
                "NUMERIC SUMMARY",
                numeric_summary,
                "",
            ]
        )

    context_parts.extend(
        [
            (
                f"DATA PREVIEW "
                f"(first {len(preview_df)} rows)"
            ),
            preview_csv,
        ]
    )

    context = "\n".join(context_parts)

    if len(context) > MAX_CONTEXT_CHARACTERS:
        context = context[:MAX_CONTEXT_CHARACTERS]

        context += (
            "\n\n[Context truncated because the query "
            "result was too large.]"
        )

    return context


def generate_analysis(
    question: str,
    sql: str,
    result_df: pd.DataFrame,
) -> str:
    """
    Generate a grounded natural-language analysis of an SQL result.
    """

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    if result_df.empty:
        return (
            "### 分析结论\n"
            "当前查询没有返回符合条件的数据，因此无法得出有效结论。\n\n"
            "### 建议检查\n"
            "请确认筛选日期、产品、设备或订单条件是否正确。"
        )

    data_context = dataframe_to_context(
        result_df
    )

    user_prompt = f"""
User question:

{cleaned_question}

Executed SQL:

{sql}

SQL query result information:

{data_context}

Analyze the result and answer the original question.
Use only the supplied query result.
"""

    client = get_llm_client()

    response = client.chat.completions.create(
        model=get_llm_model(),
        messages=[
            {
                "role": "system",
                "content": ANALYSIS_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
        max_tokens=800,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The language model returned an empty analysis."
        )

    return content.strip()