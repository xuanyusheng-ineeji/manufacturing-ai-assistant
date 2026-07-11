import pytest

from app.tools.sql_validator import (
    SQLValidationError,
    validate_sql,
)


def test_select_is_allowed() -> None:
    sql = """
    SELECT item_cd, COUNT(*) AS count
    FROM weight_rawdata
    GROUP BY item_cd
    """

    validated = validate_sql(sql)

    assert "SELECT" in validated.upper()
    assert "LIMIT" in validated.upper()


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM weight_rawdata",
        "DROP TABLE weight_rawdata",
        "UPDATE weight_rawdata SET weight = 0",
        "INSERT INTO mst_item VALUES ('X')",
        "ALTER TABLE mst_item ADD COLUMN test TEXT",
    ],
)
def test_mutation_queries_are_rejected(
    sql: str,
) -> None:
    with pytest.raises(
        SQLValidationError
    ):
        validate_sql(sql)


def test_unknown_table_is_rejected() -> None:
    with pytest.raises(
        SQLValidationError
    ):
        validate_sql(
            "SELECT * FROM secret_table"
        )


def test_multiple_statements_are_rejected() -> None:
    with pytest.raises(
        SQLValidationError
    ):
        validate_sql(
            "SELECT * FROM mst_item; "
            "SELECT * FROM wrk_order;"
        )