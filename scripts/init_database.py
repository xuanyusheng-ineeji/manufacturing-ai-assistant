from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
DATABASE_PATH = BASE_DIR / "data" / "manufacturing.db"


TABLE_FILES = {
    "mst_item": "mst_item.csv",
    "mst_equipment": "mst_equipment.csv",
    "wrk_order": "wrk_order.csv",
    "weight_rawdata": "weight_rawdata.csv",
}


def load_csv_to_database(
    connection: sqlite3.Connection,
    table_name: str,
    filename: str,
) -> None:
    csv_path = RAW_DATA_DIR / filename

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    dataframe = pd.read_csv(csv_path)

    dataframe.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False,
    )

    print(
        f"Loaded table: {table_name} "
        f"({len(dataframe):,} rows)"
    )


def create_indexes(
    connection: sqlite3.Connection,
) -> None:
    cursor = connection.cursor()

    index_statements = [
        """
        CREATE INDEX IF NOT EXISTS
        idx_weight_event_time
        ON weight_rawdata(event_time)
        """,
        """
        CREATE INDEX IF NOT EXISTS
        idx_weight_item_cd
        ON weight_rawdata(item_cd)
        """,
        """
        CREATE INDEX IF NOT EXISTS
        idx_weight_equipment_cd
        ON weight_rawdata(equipment_cd)
        """,
        """
        CREATE INDEX IF NOT EXISTS
        idx_weight_order_id
        ON weight_rawdata(order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS
        idx_order_date
        ON wrk_order(order_date)
        """,
    ]

    for statement in index_statements:
        cursor.execute(statement)

    connection.commit()

    print("Database indexes created.")


def validate_database(
    connection: sqlite3.Connection,
) -> None:
    print("\nDatabase validation:")

    for table_name in TABLE_FILES:
        query = f"SELECT COUNT(*) AS row_count FROM {table_name}"

        result = pd.read_sql_query(
            query,
            connection,
        )

        row_count = result.iloc[0]["row_count"]

        print(
            f"- {table_name}: {row_count:,} rows"
        )


def main() -> None:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        for table_name, filename in TABLE_FILES.items():
            load_csv_to_database(
                connection=connection,
                table_name=table_name,
                filename=filename,
            )

        create_indexes(connection)
        validate_database(connection)

    print(f"\nDatabase created: {DATABASE_PATH}")


if __name__ == "__main__":
    main()