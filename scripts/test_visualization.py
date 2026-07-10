from app.database.connection import execute_query
from app.services.visualization_service import (
    generate_visualization,
)


def test_daily_trend() -> None:
    query = """
    SELECT
        DATE(event_time) AS event_date,
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
    GROUP BY DATE(event_time)
    ORDER BY event_date
    """

    dataframe = execute_query(query)

    result = generate_visualization(
        dataframe=dataframe,
        question="每天的异常率趋势",
    )

    print("Daily trend")
    print("Chart type:", result.chart_type)
    print("Reason:", result.reason)

    if result.figure:
        result.figure.show()


def test_equipment_ranking() -> None:
    query = """
    SELECT
        machine_name,
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
    GROUP BY machine_name
    ORDER BY abnormal_rate DESC
    """

    dataframe = execute_query(query)

    result = generate_visualization(
        dataframe=dataframe,
        question="哪个设备异常率最高",
    )

    print("Equipment ranking")
    print("Chart type:", result.chart_type)
    print("Reason:", result.reason)

    if result.figure:
        result.figure.show()


def main() -> None:
    test_daily_trend()
    test_equipment_ranking()


if __name__ == "__main__":
    main()