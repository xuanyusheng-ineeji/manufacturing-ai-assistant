import os

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.schema_tool import get_database_schema
from app.tools.sql_validator import validate_sql


load_dotenv()


SYSTEM_PROMPT = """
You are a manufacturing data analyst and SQLite expert.

Your task is to convert the user's natural-language question into
one valid SQLite SELECT query.

Rules:
1. Return SQL only.
2. Do not include explanations.
3. Do not use markdown code fences.
4. Only use tables and columns shown in the database schema.
5. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or PRAGMA.
6. Use SQLite syntax.
7. Use DATE(event_time) when filtering weight_rawdata by date.
8. Use DATE(order_date) when filtering wrk_order by date.
9. result_flag has values: OK, OVER, UNDER.
10. Abnormal records mean result_flag is not OK.
11. Abnormal rate means abnormal count divided by total count times 100.
12. Add clear aliases to calculated columns.
"""


def get_llm_model() -> str:
    return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def get_llm_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY is not configured in .env"
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def generate_sql(question: str) -> str:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    schema = get_database_schema()

    user_prompt = f"""
Database schema:

{schema}

User question:

{question}

Generate one SQLite SELECT query.
"""

    client = get_llm_client()

    response = client.chat.completions.create(
        model=get_llm_model(),
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    generated_sql = response.choices[0].message.content.strip()

    return validate_sql(generated_sql)