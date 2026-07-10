import pandas as pd

from app.database.connection import execute_query
from app.services.analysis_service import generate_analysis
from app.services.text_to_sql_service import generate_sql
from app.services.visualization_service import (
    ChartResult,
    generate_visualization,
)


def ask_database(
    question: str,
) -> tuple[str, pd.DataFrame]:
    sql = generate_sql(question)

    result_df = execute_query(sql)

    return sql, result_df


def analyze_database_question(
    question: str,
) -> tuple[
    str,
    pd.DataFrame,
    str,
    ChartResult,
]:
    sql = generate_sql(question)

    result_df = execute_query(sql)

    analysis = generate_analysis(
        question=question,
        sql=sql,
        result_df=result_df,
    )

    chart_result = generate_visualization(
        dataframe=result_df,
        question=question,
    )

    return (
        sql,
        result_df,
        analysis,
        chart_result,
    )