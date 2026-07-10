import pandas as pd

from app.database.connection import execute_query
from app.services.analysis_service import generate_analysis
from app.services.text_to_sql_service import generate_sql


def ask_database(
    question: str,
) -> tuple[str, pd.DataFrame]:
    """
    Generate SQL and execute it.

    This function is kept for backward compatibility.
    """

    sql = generate_sql(question)

    result_df = execute_query(sql)

    return sql, result_df


def analyze_database_question(
    question: str,
) -> tuple[str, pd.DataFrame, str]:
    """
    Generate SQL, execute it and analyze the query result.
    """

    sql = generate_sql(question)

    result_df = execute_query(sql)

    analysis = generate_analysis(
        question=question,
        sql=sql,
        result_df=result_df,
    )

    return sql, result_df, analysis