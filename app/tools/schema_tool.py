from app.database.connection import execute_query


ALLOWED_TABLES = [
    "mst_item",
    "mst_equipment",
    "wrk_order",
    "weight_rawdata",
]


def get_database_schema() -> str:
    schema_parts: list[str] = []

    for table_name in ALLOWED_TABLES:
        query = f"PRAGMA table_info({table_name})"

        columns_df = execute_query(query)

        column_lines = []

        for _, row in columns_df.iterrows():
            column_lines.append(
                f"- {row['name']} ({row['type']})"
            )

        schema_parts.append(
            f"Table: {table_name}\n"
            + "\n".join(column_lines)
        )

    return "\n\n".join(schema_parts)


if __name__ == "__main__":
    print(get_database_schema())