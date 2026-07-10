from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "data" / "manufacturing.db"


def get_connection() -> sqlite3.Connection:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database does not exist. "
            "Run scripts/init_database.py first."
        )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def execute_query(
    query: str,
    parameters: tuple | None = None,
) -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(
            sql=query,
            con=connection,
            params=parameters,
        )