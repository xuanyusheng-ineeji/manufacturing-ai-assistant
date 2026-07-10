from pathlib import Path
import sys

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


from app.database.connection import execute_query


def show_table_counts() -> None:
    query = """
    SELECT
        'mst_item' AS table_name,
        COUNT(*) AS row_count
    FROM mst_item

    UNION ALL

    SELECT
        'mst_equipment',
        COUNT(*)
    FROM mst_equipment

    UNION ALL

    SELECT
        'wrk_order',
        COUNT(*)
    FROM wrk_order

    UNION ALL

    SELECT
        'weight_rawdata',
        COUNT(*)
    FROM weight_rawdata
    """

    result = execute_query(query)

    print("\nTable counts")
    print(result.to_string(index=False))


def show_equipment_summary() -> None:
    query = """
    SELECT
        equipment_cd,
        machine_name,
        COUNT(*) AS measurement_count,
        ROUND(AVG(weight), 2) AS avg_weight,
        ROUND(AVG(weight_diff), 2) AS avg_weight_diff,
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
            ) / COUNT(*),
            2
        ) AS abnormal_rate
    FROM weight_rawdata
    GROUP BY
        equipment_cd,
        machine_name
    ORDER BY abnormal_rate DESC
    """

    result = execute_query(query)

    print("\nEquipment summary")
    print(result.to_string(index=False))


def show_product_summary() -> None:
    query = """
    SELECT
        w.item_cd,
        i.item_name,
        COUNT(*) AS measurement_count,
        ROUND(AVG(w.weight), 2) AS avg_weight,
        ROUND(AVG(w.weight_diff), 2) AS avg_weight_diff,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN w.result_flag != 'OK'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS abnormal_rate
    FROM weight_rawdata AS w
    LEFT JOIN mst_item AS i
        ON w.item_cd = i.item_cd
    GROUP BY
        w.item_cd,
        i.item_name
    ORDER BY abnormal_rate DESC
    """

    result = execute_query(query)

    print("\nProduct summary")
    print(result.to_string(index=False))


def main() -> None:
    pd.set_option(
        "display.max_columns",
        None,
    )

    show_table_counts()
    show_equipment_summary()
    show_product_summary()


if __name__ == "__main__":
    main()