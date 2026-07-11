import os
from dataclasses import dataclass

import pandas as pd

from app.database.connection import execute_query
from app.services.knowledge_service import (
    answer_knowledge_question,
)
from app.services.retrieval_service import (
    RetrievalResult,
)
from app.services.text_to_sql_service import (
    get_llm_client,
)


ROOT_CAUSE_SYSTEM_PROMPT = """
You are a careful manufacturing root-cause analysis assistant.

You will receive several pieces of manufacturing evidence:

1. Equipment abnormal-rate ranking.
2. Abnormal type distribution.
3. Product contribution.
4. Date contribution.
5. Hourly contribution.
6. Recent trend comparison.
7. Relevant SOP or equipment manual excerpts.

Rules:
1. Never claim that a root cause is confirmed unless the evidence proves it.
2. Use phrases such as:
   - "the data indicates";
   - "the anomaly is concentrated in";
   - "this should be investigated";
   - "a possible contributing factor".
3. Clearly separate observed facts from possible explanations.
4. Use only supplied data and documents.
5. Never invent equipment, products, values or procedures.
6. Include important percentages and counts.
7. Answer in the same language as the user.
8. Cite document guidance using [Source 1], [Source 2], etc.
9. State limitations when process variables such as pressure,
   temperature or viscosity are unavailable.
10. Keep the response practical and structured.

Preferred structure:

### 分析对象

### 核心数据发现

### 重点异常模式

### 建议排查方向

### 文档依据

### 分析局限性
"""


@dataclass
class RootCauseResult:
    answer: str
    target_equipment_cd: str
    target_equipment_name: str
    equipment_ranking_df: pd.DataFrame
    abnormal_type_df: pd.DataFrame
    product_contribution_df: pd.DataFrame
    daily_contribution_df: pd.DataFrame
    hourly_contribution_df: pd.DataFrame
    trend_comparison_df: pd.DataFrame
    sources: list[RetrievalResult]


def get_equipment_ranking() -> pd.DataFrame:
    query = """
    SELECT
        equipment_cd,
        machine_name,
        COUNT(*) AS measurement_count,
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
    GROUP BY
        equipment_cd,
        machine_name
    ORDER BY abnormal_rate DESC
    """

    return execute_query(query)


def get_abnormal_type_distribution(
    equipment_cd: str,
) -> pd.DataFrame:
    query = """
    SELECT
        result_flag,
        COUNT(*) AS abnormal_count,
        ROUND(
            100.0 * COUNT(*)
            / NULLIF(
                SUM(COUNT(*)) OVER (),
                0
            ),
            2
        ) AS abnormal_share
    FROM weight_rawdata
    WHERE equipment_cd = ?
      AND result_flag != 'OK'
    GROUP BY result_flag
    ORDER BY abnormal_count DESC
    """

    return execute_query(
        query,
        (equipment_cd,),
    )


def get_product_contribution(
    equipment_cd: str,
) -> pd.DataFrame:
    query = """
    SELECT
        w.item_cd,
        i.item_name,
        COUNT(*) AS abnormal_count,
        ROUND(
            100.0 * COUNT(*)
            / NULLIF(
                SUM(COUNT(*)) OVER (),
                0
            ),
            2
        ) AS abnormal_share,
        ROUND(
            AVG(w.weight_diff),
            2
        ) AS avg_weight_diff
    FROM weight_rawdata AS w
    LEFT JOIN mst_item AS i
        ON w.item_cd = i.item_cd
    WHERE w.equipment_cd = ?
      AND w.result_flag != 'OK'
    GROUP BY
        w.item_cd,
        i.item_name
    ORDER BY abnormal_count DESC
    LIMIT 10
    """

    return execute_query(
        query,
        (equipment_cd,),
    )


def get_daily_contribution(
    equipment_cd: str,
) -> pd.DataFrame:
    query = """
    SELECT
        DATE(event_time) AS event_date,
        COUNT(*) AS measurement_count,
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
    WHERE equipment_cd = ?
    GROUP BY DATE(event_time)
    ORDER BY abnormal_rate DESC
    LIMIT 10
    """

    return execute_query(
        query,
        (equipment_cd,),
    )


def get_hourly_contribution(
    equipment_cd: str,
) -> pd.DataFrame:
    query = """
    SELECT
        CAST(
            STRFTIME('%H', event_time)
            AS INTEGER
        ) AS production_hour,
        COUNT(*) AS measurement_count,
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
    WHERE equipment_cd = ?
    GROUP BY production_hour
    ORDER BY abnormal_rate DESC
    """

    return execute_query(
        query,
        (equipment_cd,),
    )


def get_trend_comparison(
    equipment_cd: str,
) -> pd.DataFrame:
    query = """
    WITH max_date AS (
        SELECT
            MAX(DATE(event_time)) AS latest_date
        FROM weight_rawdata
    ),
    period_data AS (
        SELECT
            CASE
                WHEN DATE(event_time) >
                     DATE(
                         (SELECT latest_date FROM max_date),
                         '-7 day'
                     )
                THEN 'recent_7_days'

                WHEN DATE(event_time) >
                     DATE(
                         (SELECT latest_date FROM max_date),
                         '-14 day'
                     )
                THEN 'previous_7_days'

                ELSE NULL
            END AS period_name,
            result_flag
        FROM weight_rawdata
        WHERE equipment_cd = ?
    )
    SELECT
        period_name,
        COUNT(*) AS measurement_count,
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
    FROM period_data
    WHERE period_name IS NOT NULL
    GROUP BY period_name
    ORDER BY period_name
    """

    return execute_query(
        query,
        (equipment_cd,),
    )


def dataframe_to_text(
    name: str,
    dataframe: pd.DataFrame,
    max_rows: int = 20,
) -> str:
    if dataframe.empty:
        return f"{name}: no data"

    return (
        f"{name}\n"
        f"{dataframe.head(max_rows).to_csv(index=False)}"
    )


def build_source_context(
    sources: list[RetrievalResult],
) -> str:
    parts: list[str] = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        page_text = (
            f", page {source.page}"
            if source.page is not None
            else ""
        )

        parts.append(
            f"[Source {index}] "
            f"{source.source}{page_text}\n"
            f"{source.text}"
        )

    return "\n\n".join(parts)


def analyze_root_cause() -> RootCauseResult:
    equipment_ranking_df = (
        get_equipment_ranking()
    )

    if equipment_ranking_df.empty:
        raise ValueError(
            "No equipment data is available."
        )

    target_row = equipment_ranking_df.iloc[0]

    equipment_cd = str(
        target_row["equipment_cd"]
    )

    equipment_name = str(
        target_row["machine_name"]
    )

    abnormal_type_df = (
        get_abnormal_type_distribution(
            equipment_cd
        )
    )

    product_contribution_df = (
        get_product_contribution(
            equipment_cd
        )
    )

    daily_contribution_df = (
        get_daily_contribution(
            equipment_cd
        )
    )

    hourly_contribution_df = (
        get_hourly_contribution(
            equipment_cd
        )
    )

    trend_comparison_df = (
        get_trend_comparison(
            equipment_cd
        )
    )

    knowledge_question = """
When a filling or weight-checking machine has an elevated abnormal
weight rate, what inspections, calibration checks and quality
procedures should be followed?
"""

    knowledge_result = (
        answer_knowledge_question(
            knowledge_question
        )
    )

    evidence = "\n\n".join(
        [
            dataframe_to_text(
                "Equipment ranking",
                equipment_ranking_df,
            ),
            dataframe_to_text(
                "Abnormal type distribution",
                abnormal_type_df,
            ),
            dataframe_to_text(
                "Product contribution",
                product_contribution_df,
            ),
            dataframe_to_text(
                "Daily contribution",
                daily_contribution_df,
            ),
            dataframe_to_text(
                "Hourly contribution",
                hourly_contribution_df,
            ),
            dataframe_to_text(
                "Recent trend comparison",
                trend_comparison_df,
            ),
        ]
    )

    source_context = build_source_context(
        knowledge_result.sources
    )

    user_prompt = f"""
Target equipment:

Equipment code: {equipment_cd}
Equipment name: {equipment_name}

Manufacturing evidence:

{evidence}

Document answer:

{knowledge_result.answer}

Document context:

{source_context}

Produce a grounded root-cause analysis report.
"""

    client = get_llm_client()

    model = os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-chat",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": ROOT_CAUSE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
        max_tokens=1200,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The language model returned "
            "an empty root-cause analysis."
        )

    return RootCauseResult(
        answer=content.strip(),
        target_equipment_cd=equipment_cd,
        target_equipment_name=equipment_name,
        equipment_ranking_df=equipment_ranking_df,
        abnormal_type_df=abnormal_type_df,
        product_contribution_df=product_contribution_df,
        daily_contribution_df=daily_contribution_df,
        hourly_contribution_df=hourly_contribution_df,
        trend_comparison_df=trend_comparison_df,
        sources=knowledge_result.sources,
    )