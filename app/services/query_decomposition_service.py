import json
import os
import re
from dataclasses import dataclass

from app.services.text_to_sql_service import (
    get_llm_client,
)


DECOMPOSITION_SYSTEM_PROMPT = """
You are a query decomposition component for a manufacturing AI assistant.

The user gives one hybrid manufacturing question that requires both:

1. Actual production database analysis.
2. SOP, equipment manual or quality procedure knowledge.

Split the original question into exactly two independent questions:

database_question:
A question that can be answered only using actual manufacturing database
records such as equipment, products, orders, measurements, abnormal rates,
dates, rankings, counts or trends.

knowledge_question:
A question that can be answered only using manufacturing documents such as
SOPs, manuals, alarm instructions, calibration procedures or quality rules.

Return valid JSON only:

{
  "database_question": "...",
  "knowledge_question": "...",
  "reason": "..."
}

Rules:
1. Preserve the original language of the user.
2. Do not answer either question.
3. Do not generate SQL.
4. Do not include Markdown.
5. The database question must not ask for SOP instructions.
6. The knowledge question must not depend on unknown database values.
7. Replace references such as "that equipment" or "the product above" with
   general document-search wording.
8. Keep both questions concise and independently understandable.
9. Never invent equipment codes, product names, alarm codes or values.
"""


@dataclass
class DecomposedQuery:
    original_question: str
    database_question: str
    knowledge_question: str
    reason: str


def clean_json_response(
    content: str,
) -> str:
    cleaned_content = content.strip()

    cleaned_content = re.sub(
        r"^```json\s*",
        "",
        cleaned_content,
        flags=re.IGNORECASE,
    )

    cleaned_content = re.sub(
        r"^```\s*",
        "",
        cleaned_content,
    )

    cleaned_content = re.sub(
        r"\s*```$",
        "",
        cleaned_content,
    )

    return cleaned_content.strip()


def validate_decomposed_query(
    original_question: str,
    payload: dict,
) -> DecomposedQuery:
    database_question = str(
        payload.get(
            "database_question",
            "",
        )
    ).strip()

    knowledge_question = str(
        payload.get(
            "knowledge_question",
            "",
        )
    ).strip()

    reason = str(
        payload.get(
            "reason",
            "The hybrid question was split into data and document tasks.",
        )
    ).strip()

    if not database_question:
        raise ValueError(
            "The decomposed database question is empty."
        )

    if not knowledge_question:
        raise ValueError(
            "The decomposed knowledge question is empty."
        )

    if database_question == knowledge_question:
        raise ValueError(
            "The decomposed questions must be different."
        )

    return DecomposedQuery(
        original_question=original_question,
        database_question=database_question,
        knowledge_question=knowledge_question,
        reason=reason,
    )


def decompose_hybrid_question(
    question: str,
) -> DecomposedQuery:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

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
                "content": DECOMPOSITION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": cleaned_question,
            },
        ],
        temperature=0,
        max_tokens=400,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The language model returned "
            "an empty decomposition result."
        )

    cleaned_content = clean_json_response(
        content
    )

    try:
        payload = json.loads(
            cleaned_content
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The language model returned invalid JSON: "
            f"{cleaned_content}"
        ) from exc

    return validate_decomposed_query(
        original_question=cleaned_question,
        payload=payload,
    )