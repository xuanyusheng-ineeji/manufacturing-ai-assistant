from dataclasses import dataclass


import pandas as pd

from app.services.ai_query_service import (
    analyze_database_question,
)
from app.services.intent_router_service import (
    RouteDecision,
    route_question,
)
from app.services.knowledge_service import (
    answer_knowledge_question,
)
from app.services.retrieval_service import (
    RetrievalResult,
)
from app.services.visualization_service import (
    ChartResult,
)
from app.services.hybrid_analysis_service import (
    analyze_hybrid_question,
)

@dataclass
class UnifiedAssistantResponse:
    route: RouteDecision
    answer: str
    sql: str | None = None
    result_df: pd.DataFrame | None = None
    chart_result: ChartResult | None = None
    sources: list[RetrievalResult] | None = None


def answer_general_question(
    question: str,
) -> str:
    question_lower = question.strip().lower()

    if question_lower in {
        "你好",
        "您好",
        "hello",
        "hi",
    }:
        return (
            "你好，我可以帮助你查询制造数据库，"
            "也可以检索设备说明书和质量管理SOP。"
        )

    if question_lower in {
        "谢谢",
        "感谢",
        "thanks",
        "thank you",
    }:
        return "不客气。"

    return (
        "这个问题目前不属于制造数据库分析或文档知识检索范围。"
        "你可以询问生产数据、设备异常、质量指标或SOP流程。"
    )


def ask_unified_assistant(
    question: str,
) -> UnifiedAssistantResponse:
    route = route_question(
        question
    )

    if route.intent == "database":
        (
            sql,
            result_df,
            analysis,
            chart_result,
        ) = analyze_database_question(
            question
        )

        return UnifiedAssistantResponse(
            route=route,
            answer=analysis,
            sql=sql,
            result_df=result_df,
            chart_result=chart_result,
            sources=[],
        )
    if route.intent == "hybrid":
        hybrid_result = analyze_hybrid_question(
            question
        )

        return UnifiedAssistantResponse(
            route=route,
            answer=hybrid_result.answer,
            sql=hybrid_result.sql,
            result_df=hybrid_result.result_df,
            chart_result=hybrid_result.chart_result,
            sources=hybrid_result.sources,
        )
    if route.intent == "knowledge":
        knowledge_result = (
            answer_knowledge_question(
                question
            )
        )

        return UnifiedAssistantResponse(
            route=route,
            answer=knowledge_result.answer,
            sql=None,
            result_df=None,
            chart_result=None,
            sources=knowledge_result.sources,
        )

    return UnifiedAssistantResponse(
        route=route,
        answer=answer_general_question(
            question
        ),
        sql=None,
        result_df=None,
        chart_result=None,
        sources=[],
    )