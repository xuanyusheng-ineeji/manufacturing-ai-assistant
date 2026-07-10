from typing import Any

import pandas as pd

from app.database.connection import execute_query


def get_date_range() -> tuple[str, str]:
    query = """
    SELECT
        MIN(DATE(event_time)) AS min_date,
        MAX(DATE(event_time)) AS max_date
    FROM weight_rawdata
    """

    result = execute_query(query)

    return (
        result.iloc[0]["min_date"],
        result.iloc[0]["max_date"],
    )


def get_items() -> pd.DataFrame:
    query = """
    SELECT
        item_cd,
        item_name
    FROM mst_item
    ORDER BY item_cd
    """

    return execute_query(query)


def get_equipment() -> pd.DataFrame:
    query = """
    SELECT
        equipment_cd,
        equipment_name,
        line_name,
        status
    FROM mst_equipment
    ORDER BY equipment_cd
    """

    return execute_query(query)


def build_filter_clause(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
    equipment_cd: str | None = None,
) -> tuple[str, tuple[Any, ...]]:
    conditions = [
        "DATE(event_time) BETWEEN ? AND ?"
    ]

    parameters: list[Any] = [
        start_date,
        end_date,
    ]

    if item_cd:
        conditions.append("item_cd = ?")
        parameters.append(item_cd)

    if equipment_cd:
        conditions.append("equipment_cd = ?")
        parameters.append(equipment_cd)

    where_clause = " AND ".join(conditions)

    return where_clause, tuple(parameters)


def get_kpi_summary(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
    equipment_cd: str | None = None,
) -> dict[str, float]:
    weight_filter, weight_parameters = build_filter_clause(
        start_date=start_date,
        end_date=end_date,
        item_cd=item_cd,
        equipment_cd=equipment_cd,
    )

    weight_query = f"""
    SELECT
        COUNT(*) AS measurement_count,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(AVG(weight_diff), 2) AS avg_weight_diff,
        SUM(
            CASE
                WHEN result_flag != 'OK'
                THEN 1
                ELSE 0
            END
        ) AS abnormal_count,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS abnormal_rate
    FROM weight_rawdata
    WHERE {weight_filter}
    """

    weight_result = execute_query(
        weight_query,
        weight_parameters,
    )

    order_conditions = [
        "DATE(order_date) BETWEEN ? AND ?"
    ]

    order_parameters: list[Any] = [
        start_date,
        end_date,
    ]

    if item_cd:
        order_conditions.append("item_cd = ?")
        order_parameters.append(item_cd)

    if equipment_cd:
        order_conditions.append("equipment_cd = ?")
        order_parameters.append(equipment_cd)

    order_where_clause = " AND ".join(order_conditions)

    order_query = f"""
    SELECT
        COALESCE(SUM(result_qty), 0) AS total_result_qty,
        COALESCE(SUM(rework_qty), 0) AS total_rework_qty,
        ROUND(
            100.0 * SUM(rework_qty)
            / NULLIF(SUM(result_qty), 0),
            2
        ) AS rework_rate
    FROM wrk_order
    WHERE {order_where_clause}
    """

    order_result = execute_query(
        order_query,
        tuple(order_parameters),
    )

    return {
        "measurement_count": int(
            weight_result.iloc[0]["measurement_count"] or 0
        ),
        "order_count": int(
            weight_result.iloc[0]["order_count"] or 0
        ),
        "avg_weight_diff": float(
            weight_result.iloc[0]["avg_weight_diff"] or 0
        ),
        "abnormal_count": int(
            weight_result.iloc[0]["abnormal_count"] or 0
        ),
        "abnormal_rate": float(
            weight_result.iloc[0]["abnormal_rate"] or 0
        ),
        "total_result_qty": int(
            order_result.iloc[0]["total_result_qty"] or 0
        ),
        "total_rework_qty": int(
            order_result.iloc[0]["total_rework_qty"] or 0
        ),
        "rework_rate": float(
            order_result.iloc[0]["rework_rate"] or 0
        ),
    }


def get_daily_weight_trend(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
    equipment_cd: str | None = None,
) -> pd.DataFrame:
    where_clause, parameters = build_filter_clause(
        start_date=start_date,
        end_date=end_date,
        item_cd=item_cd,
        equipment_cd=equipment_cd,
    )

    query = f"""
    SELECT
        DATE(event_time) AS event_date,
        ROUND(AVG(weight), 2) AS avg_weight,
        ROUND(AVG(std_weight), 2) AS avg_std_weight,
        ROUND(AVG(weight_diff), 2) AS avg_weight_diff,
        ROUND(MIN(weight), 2) AS min_weight,
        ROUND(MAX(weight), 2) AS max_weight,
        COUNT(*) AS measurement_count
    FROM weight_rawdata
    WHERE {where_clause}
    GROUP BY DATE(event_time)
    ORDER BY event_date
    """

    return execute_query(
        query,
        parameters,
    )


def get_daily_abnormal_trend(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
    equipment_cd: str | None = None,
) -> pd.DataFrame:
    where_clause, parameters = build_filter_clause(
        start_date=start_date,
        end_date=end_date,
        item_cd=item_cd,
        equipment_cd=equipment_cd,
    )

    query = f"""
    SELECT
        DATE(event_time) AS event_date,
        COUNT(*) AS measurement_count,
        SUM(
            CASE
                WHEN result_flag = 'OVER'
                THEN 1
                ELSE 0
            END
        ) AS over_count,
        SUM(
            CASE
                WHEN result_flag = 'UNDER'
                THEN 1
                ELSE 0
            END
        ) AS under_count,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS abnormal_rate
    FROM weight_rawdata
    WHERE {where_clause}
    GROUP BY DATE(event_time)
    ORDER BY event_date
    """

    return execute_query(
        query,
        parameters,
    )


def get_equipment_summary(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
) -> pd.DataFrame:
    conditions = [
        "DATE(w.event_time) BETWEEN ? AND ?"
    ]

    parameters: list[Any] = [
        start_date,
        end_date,
    ]

    if item_cd:
        conditions.append("w.item_cd = ?")
        parameters.append(item_cd)

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        w.equipment_cd,
        w.machine_name,
        e.line_name,
        COUNT(*) AS measurement_count,
        ROUND(AVG(w.weight_diff), 2) AS avg_weight_diff,
        SUM(
            CASE
                WHEN w.result_flag = 'OVER'
                THEN 1
                ELSE 0
            END
        ) AS over_count,
        SUM(
            CASE
                WHEN w.result_flag = 'UNDER'
                THEN 1
                ELSE 0
            END
        ) AS under_count,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN w.result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS abnormal_rate
    FROM weight_rawdata AS w
    LEFT JOIN mst_equipment AS e
        ON w.equipment_cd = e.equipment_cd
    WHERE {where_clause}
    GROUP BY
        w.equipment_cd,
        w.machine_name,
        e.line_name
    ORDER BY abnormal_rate DESC
    """

    return execute_query(
        query,
        tuple(parameters),
    )


def get_product_summary(
    start_date: str,
    end_date: str,
    equipment_cd: str | None = None,
) -> pd.DataFrame:
    conditions = [
        "DATE(w.event_time) BETWEEN ? AND ?"
    ]

    parameters: list[Any] = [
        start_date,
        end_date,
    ]

    if equipment_cd:
        conditions.append("w.equipment_cd = ?")
        parameters.append(equipment_cd)

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        w.item_cd,
        i.item_name,
        COUNT(*) AS measurement_count,
        ROUND(AVG(w.weight), 2) AS avg_weight,
        ROUND(AVG(w.std_weight), 2) AS std_weight,
        ROUND(AVG(w.weight_diff), 2) AS avg_weight_diff,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN w.result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS abnormal_rate
    FROM weight_rawdata AS w
    LEFT JOIN mst_item AS i
        ON w.item_cd = i.item_cd
    WHERE {where_clause}
    GROUP BY
        w.item_cd,
        i.item_name
    ORDER BY abnormal_rate DESC
    """

    return execute_query(
        query,
        tuple(parameters),
    )


def get_recent_abnormal_records(
    start_date: str,
    end_date: str,
    item_cd: str | None = None,
    equipment_cd: str | None = None,
    limit: int = 100,
) -> pd.DataFrame:
    where_clause, parameters = build_filter_clause(
        start_date=start_date,
        end_date=end_date,
        item_cd=item_cd,
        equipment_cd=equipment_cd,
    )

    query = f"""
    SELECT
        measurement_id,
        event_time,
        order_id,
        item_cd,
        equipment_cd,
        machine_name,
        weight,
        std_weight,
        lower_limit,
        upper_limit,
        weight_diff,
        result_flag
    FROM weight_rawdata
    WHERE {where_clause}
      AND result_flag != 'OK'
    ORDER BY event_time DESC
    LIMIT ?
    """

    full_parameters = parameters + (limit,)

    return execute_query(
        query,
        full_parameters,
    )