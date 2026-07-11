from dataclasses import dataclass

import pandas as pd

from app.database.connection import execute_query


@dataclass
class EquipmentHealthResult:
    summary_df: pd.DataFrame
    detail_df: pd.DataFrame


def get_equipment_health_metrics() -> pd.DataFrame:
    query = """
    WITH max_date AS (
        SELECT
            MAX(DATE(event_time)) AS latest_date
        FROM weight_rawdata
    ),

    base_metrics AS (
        SELECT
            w.equipment_cd,
            w.machine_name,
            COUNT(*) AS measurement_count,

            SUM(
                CASE
                    WHEN w.result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) AS abnormal_count,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN w.result_flag != 'OK'
                        THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS abnormal_rate,

            ROUND(
                AVG(ABS(w.weight_diff)),
                2
            ) AS avg_abs_weight_diff,

            ROUND(
                AVG(
                    ABS(w.weight_diff)
                    / NULLIF(w.std_weight, 0)
                    * 100.0
                ),
                2
            ) AS avg_weight_diff_rate

        FROM weight_rawdata AS w
        GROUP BY
            w.equipment_cd,
            w.machine_name
    ),

    recent_metrics AS (
        SELECT
            equipment_cd,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN result_flag != 'OK'
                        THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS recent_abnormal_rate

        FROM weight_rawdata
        WHERE DATE(event_time) >
              DATE(
                  (SELECT latest_date FROM max_date),
                  '-7 day'
              )
        GROUP BY equipment_cd
    ),

    previous_metrics AS (
        SELECT
            equipment_cd,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN result_flag != 'OK'
                        THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS previous_abnormal_rate

        FROM weight_rawdata
        WHERE DATE(event_time) >
              DATE(
                  (SELECT latest_date FROM max_date),
                  '-14 day'
              )
          AND DATE(event_time) <=
              DATE(
                  (SELECT latest_date FROM max_date),
                  '-7 day'
              )
        GROUP BY equipment_cd
    ),

    order_metrics AS (
        SELECT
            equipment_cd,

            ROUND(
                100.0 * SUM(rework_qty)
                / NULLIF(SUM(result_qty), 0),
                2
            ) AS rework_rate

        FROM wrk_order
        GROUP BY equipment_cd
    )

    SELECT
        b.equipment_cd,
        b.machine_name,
        b.measurement_count,
        b.abnormal_count,
        b.abnormal_rate,
        b.avg_abs_weight_diff,
        b.avg_weight_diff_rate,

        COALESCE(
            r.recent_abnormal_rate,
            0
        ) AS recent_abnormal_rate,

        COALESCE(
            p.previous_abnormal_rate,
            0
        ) AS previous_abnormal_rate,

        ROUND(
            COALESCE(
                r.recent_abnormal_rate,
                0
            )
            -
            COALESCE(
                p.previous_abnormal_rate,
                0
            ),
            2
        ) AS abnormal_rate_change,

        COALESCE(
            o.rework_rate,
            0
        ) AS rework_rate

    FROM base_metrics AS b

    LEFT JOIN recent_metrics AS r
        ON b.equipment_cd = r.equipment_cd

    LEFT JOIN previous_metrics AS p
        ON b.equipment_cd = p.equipment_cd

    LEFT JOIN order_metrics AS o
        ON b.equipment_cd = o.equipment_cd

    ORDER BY b.equipment_cd
    """

    return execute_query(query)

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(value, maximum),
    )


def calculate_health_score(
    abnormal_rate: float,
    rework_rate: float,
    abnormal_rate_change: float,
    avg_weight_diff_rate: float,
) -> float:
    """
    Calculate a 0-100 health score.

    Higher values indicate healthier equipment.
    """

    abnormal_penalty = min(
        abnormal_rate * 5.0,
        40.0,
    )

    rework_penalty = min(
        rework_rate * 4.0,
        20.0,
    )

    trend_penalty = 0.0

    if abnormal_rate_change > 0:
        trend_penalty = min(
            abnormal_rate_change * 6.0,
            20.0,
        )

    weight_penalty = min(
        avg_weight_diff_rate * 4.0,
        20.0,
    )

    score = (
        100.0
        - abnormal_penalty
        - rework_penalty
        - trend_penalty
        - weight_penalty
    )

    return round(
        clamp(score),
        1,
    )


def get_health_status(
    score: float,
) -> str:
    if score >= 85:
        return "Healthy"

    if score >= 70:
        return "Watch"

    if score >= 50:
        return "Risk"

    return "Critical"

def calculate_equipment_health() -> EquipmentHealthResult:
    metrics_df = get_equipment_health_metrics()

    if metrics_df.empty:
        return EquipmentHealthResult(
            summary_df=pd.DataFrame(),
            detail_df=pd.DataFrame(),
        )

    detail_df = metrics_df.copy()

    detail_df["health_score"] = detail_df.apply(
        lambda row: calculate_health_score(
            abnormal_rate=float(
                row["abnormal_rate"] or 0
            ),
            rework_rate=float(
                row["rework_rate"] or 0
            ),
            abnormal_rate_change=float(
                row["abnormal_rate_change"] or 0
            ),
            avg_weight_diff_rate=float(
                row["avg_weight_diff_rate"] or 0
            ),
        ),
        axis=1,
    )

    detail_df["health_status"] = (
        detail_df["health_score"].apply(
            get_health_status
        )
    )

    detail_df["health_rank"] = (
        detail_df["health_score"]
        .rank(
            method="dense",
            ascending=False,
        )
        .astype(int)
    )

    detail_df = detail_df.sort_values(
        by="health_score",
        ascending=False,
    ).reset_index(drop=True)

    summary_columns = [
        "health_rank",
        "equipment_cd",
        "machine_name",
        "health_score",
        "health_status",
        "abnormal_rate",
        "rework_rate",
        "abnormal_rate_change",
    ]

    summary_df = detail_df[
        summary_columns
    ].copy()

    return EquipmentHealthResult(
        summary_df=summary_df,
        detail_df=detail_df,
    )