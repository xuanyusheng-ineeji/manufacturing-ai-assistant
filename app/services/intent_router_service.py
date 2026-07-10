import json
import os
import re
from dataclasses import dataclass
from typing import Literal

from app.services.text_to_sql_service import get_llm_client


IntentType = Literal[
    "database",
    "knowledge",
    "hybrid",
    "general",
]


@dataclass
class RouteDecision:
    intent: IntentType
    confidence: float
    reason: str


DATABASE_KEYWORDS = {
    "异常率",
    "平均重量",
    "重量偏差",
    "订单",
    "产品",
    "设备",
    "产量",
    "返工",
    "趋势",
    "最近",
    "每天",
    "每月",
    "多少条",
    "最高",
    "最低",
    "比较",
    "统计",
    "超重数量",
    "低重数量",
    "over数量",
    "under数量",
    "measurement",
    "order",
    "abnormal rate",
    "average weight",
    "production quantity",
    "rework rate",
    "trend",
}

KNOWLEDGE_KEYWORDS = {
    "报警",
    "故障",
    "怎么处理",
    "如何处理",
    "处理流程",
    "操作步骤",
    "校准",
    "说明书",
    "sop",
    "启动前",
    "开机前",
    "连续低重",
    "连续超重",
    "产品切换",
    "检查项目",
    "alarm",
    "manual",
    "procedure",
    "calibration",
    "troubleshooting",
}

HYBRID_ACTION_KEYWORDS = {
    "应该检查",
    "需要检查",
    "如何改善",
    "怎么改善",
    "如何处理",
    "怎么处理",
    "需要处理",
    "建议",
    "应该怎么做",
    "需要校准",
    "最需要校准",
    "处理建议",
    "改善建议",
    "what should",
    "how should",
    "recommend",
    "need calibration",
    "should inspect",
}

ALARM_CODE_PATTERN = re.compile(
    r"\bE\d{3,4}\b",
    flags=re.IGNORECASE,
)


ROUTER_SYSTEM_PROMPT = """
You are an intent router for a manufacturing AI assistant.

Classify the user's question into exactly one intent:

database:
Questions requiring actual production data, measurements, orders,
products, equipment statistics, dates, rankings, comparisons or trends.

knowledge:
Questions requiring only equipment manuals, SOPs, alarm handling,
calibration procedures, operating instructions or quality procedures.

hybrid:
Questions requiring both actual production data and document-based
procedures or recommendations.

Examples of hybrid questions:
- Which equipment currently needs calibration most?
- Which equipment has the highest abnormal rate and what should be checked?
- Find the product with the most UNDER results and explain the SOP response.
- Why is this equipment abnormal and what procedure should operators follow?

general:
Greetings, thanks, casual conversation or questions unrelated to the
available manufacturing database and documents.

Return JSON only:

{
  "intent": "database | knowledge | hybrid | general",
  "confidence": 0.0,
  "reason": "short explanation"
}

Rules:
1. Do not answer the user's question.
2. Do not generate SQL.
3. Return valid JSON only.
4. Use database when only actual stored data is required.
5. Use knowledge when only instructions or documents are required.
6. Use hybrid when both data findings and document guidance are required.
"""


def keyword_score(
    question: str,
    keywords: set[str],
) -> int:
    question_lower = question.lower()

    return sum(
        1
        for keyword in keywords
        if keyword.lower() in question_lower
    )


def route_by_rules(
    question: str,
) -> RouteDecision | None:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    if ALARM_CODE_PATTERN.search(
        cleaned_question
    ):
        return RouteDecision(
            intent="knowledge",
            confidence=0.98,
            reason="An equipment alarm code was detected.",
        )

    database_score = keyword_score(
        cleaned_question,
        DATABASE_KEYWORDS,
    )

    knowledge_score = keyword_score(
        cleaned_question,
        KNOWLEDGE_KEYWORDS,
    )

    hybrid_action_score = keyword_score(
        cleaned_question,
        HYBRID_ACTION_KEYWORDS,
    )
    if (
        database_score >= 1
        and (
            knowledge_score >= 1
            or hybrid_action_score >= 1
        )
    ):
        return RouteDecision(
            intent="hybrid",
            confidence=min(
                0.80
                + database_score * 0.03
                + knowledge_score * 0.03
                + hybrid_action_score * 0.03,
                0.97,
            ),
            reason=(
                "The question requires both production data "
                "and manufacturing procedure knowledge."
            ),
        )
    if (
        database_score >= 2
        and database_score > knowledge_score
    ):
        return RouteDecision(
            intent="database",
            confidence=min(
                0.70 + database_score * 0.05,
                0.95,
            ),
            reason=(
                "The question contains multiple "
                "production-data keywords."
            ),
        )

    if (
        knowledge_score >= 1
        and knowledge_score > database_score
    ):
        return RouteDecision(
            intent="knowledge",
            confidence=min(
                0.75 + knowledge_score * 0.05,
                0.95,
            ),
            reason=(
                "The question contains procedure, alarm "
                "or manual-related keywords."
            ),
        )

    simple_general_questions = {
        "你好",
        "您好",
        "谢谢",
        "感谢",
        "hello",
        "hi",
        "thanks",
        "thank you",
    }

    if cleaned_question.lower() in simple_general_questions:
        return RouteDecision(
            intent="general",
            confidence=0.99,
            reason="A greeting or casual message was detected.",
        )

    return None


def route_by_llm(
    question: str,
) -> RouteDecision:
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
                "content": ROUTER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0,
        max_tokens=200,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The model returned an empty routing result."
        )

    cleaned_content = content.strip()

    cleaned_content = re.sub(
        r"^```json\s*",
        "",
        cleaned_content,
        flags=re.IGNORECASE,
    )

    cleaned_content = re.sub(
        r"\s*```$",
        "",
        cleaned_content,
    )

    try:
        payload = json.loads(
            cleaned_content
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The model returned invalid router JSON: "
            f"{cleaned_content}"
        ) from exc

    intent = payload.get("intent")
    confidence = payload.get(
        "confidence",
        0.5,
    )
    reason = payload.get(
        "reason",
        "Classified by the language model.",
    )

    if intent not in {
        "database",
        "knowledge",
        "hybrid",
        "general",
    }:
        raise ValueError(
            f"Unsupported intent returned: {intent}"
        )

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5

    confidence = max(
        0.0,
        min(confidence, 1.0),
    )

    return RouteDecision(
        intent=intent,
        confidence=confidence,
        reason=str(reason),
    )


def route_question(
    question: str,
) -> RouteDecision:
    rule_decision = route_by_rules(
        question
    )

    if rule_decision is not None:
        return rule_decision

    return route_by_llm(
        question
    )