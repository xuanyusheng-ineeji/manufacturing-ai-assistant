import re

import sqlglot
from sqlglot import exp


ALLOWED_TABLES = {
    "mst_item",
    "mst_equipment",
    "wrk_order",
    "weight_rawdata",
}

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
}


class SQLValidationError(ValueError):
    pass


def clean_sql(sql: str) -> str:
    cleaned_sql = sql.strip()

    cleaned_sql = re.sub(
        r"^```sql\s*",
        "",
        cleaned_sql,
        flags=re.IGNORECASE,
    )

    cleaned_sql = re.sub(
        r"^```\s*",
        "",
        cleaned_sql,
    )

    cleaned_sql = re.sub(
        r"\s*```$",
        "",
        cleaned_sql,
    )

    return cleaned_sql.strip()


def validate_sql(sql: str) -> str:
    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        raise SQLValidationError("SQL is empty.")

    upper_sql = cleaned_sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(
            rf"\b{keyword}\b",
            upper_sql,
        ):
            raise SQLValidationError(
                f"Forbidden SQL keyword: {keyword}"
            )

    try:
        parsed_statements = sqlglot.parse(
            cleaned_sql,
            read="sqlite",
        )
    except sqlglot.errors.ParseError as exc:
        raise SQLValidationError(
            f"Invalid SQL syntax: {exc}"
        ) from exc

    if len(parsed_statements) != 1:
        raise SQLValidationError(
            "Only one SQL statement is allowed."
        )

    statement = parsed_statements[0]

    if not isinstance(
        statement,
        (exp.Select, exp.Union),
    ):
        raise SQLValidationError(
            "Only SELECT queries are allowed."
        )

    referenced_tables = {
        table.name
        for table in statement.find_all(exp.Table)
    }

    disallowed_tables = (
        referenced_tables - ALLOWED_TABLES
    )

    if disallowed_tables:
        raise SQLValidationError(
            "Access to the following tables is not allowed: "
            + ", ".join(sorted(disallowed_tables))
        )

    if "LIMIT" not in upper_sql:
        cleaned_sql = (
            cleaned_sql.rstrip(";")
            + "\nLIMIT 200;"
        )

    return cleaned_sql