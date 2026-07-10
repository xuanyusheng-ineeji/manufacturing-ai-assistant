import pandas as pd

from app.database.connection import execute_query
from app.services.text_to_sql_service import generate_sql


def ask_database(
    question: str,
) -> tuple[str, pd.DataFrame]:
    sql = generate_sql(question)

    result_df = execute_query(sql)

    return sql, result_df