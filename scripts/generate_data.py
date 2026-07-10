from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

import numpy as np
import pandas as pd


RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_items() -> pd.DataFrame:
    """生成产品主数据。"""

    items = [
        {
            "item_cd": "ITEM001",
            "item_name": "Vanilla Cream",
            "std_weight": 300.0,
            "lower_limit": 290.0,
            "upper_limit": 315.0,
            "product_category": "Cream",
        },
        {
            "item_cd": "ITEM002",
            "item_name": "Chocolate Cream",
            "std_weight": 500.0,
            "lower_limit": 485.0,
            "upper_limit": 525.0,
            "product_category": "Cream",
        },
        {
            "item_cd": "ITEM003",
            "item_name": "Strawberry Filling",
            "std_weight": 250.0,
            "lower_limit": 240.0,
            "upper_limit": 265.0,
            "product_category": "Filling",
        },
        {
            "item_cd": "ITEM004",
            "item_name": "Custard Filling",
            "std_weight": 400.0,
            "lower_limit": 385.0,
            "upper_limit": 420.0,
            "product_category": "Filling",
        },
        {
            "item_cd": "ITEM005",
            "item_name": "Condensed Milk Cream",
            "std_weight": 350.0,
            "lower_limit": 338.0,
            "upper_limit": 368.0,
            "product_category": "Cream",
        },
    ]

    return pd.DataFrame(items)


def generate_equipment() -> pd.DataFrame:
    """生成设备主数据。"""

    equipment = [
        {
            "equipment_cd": "EQ001",
            "equipment_name": "Filling Machine 1",
            "line_name": "Line A",
            "status": "ACTIVE",
            "installation_date": "2021-03-15",
        },
        {
            "equipment_cd": "EQ002",
            "equipment_name": "Filling Machine 2",
            "line_name": "Line A",
            "status": "ACTIVE",
            "installation_date": "2022-07-01",
        },
        {
            "equipment_cd": "EQ003",
            "equipment_name": "Weight Checker 1",
            "line_name": "Line B",
            "status": "ACTIVE",
            "installation_date": "2020-11-20",
        },
        {
            "equipment_cd": "EQ004",
            "equipment_name": "Weight Checker 2",
            "line_name": "Line B",
            "status": "MAINTENANCE",
            "installation_date": "2019-05-10",
        },
    ]

    return pd.DataFrame(equipment)


def generate_orders(
    items_df: pd.DataFrame,
    equipment_df: pd.DataFrame,
    number_of_days: int = 60,
    orders_per_day: int = 4,
) -> pd.DataFrame:
    """生成生产订单数据。"""

    orders = []

    start_date = datetime.now().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - timedelta(days=number_of_days)

    active_equipment = equipment_df[
        equipment_df["status"] == "ACTIVE"
    ]["equipment_cd"].tolist()

    order_sequence = 1

    for day_offset in range(number_of_days):
        order_date = start_date + timedelta(days=day_offset)

        daily_order_count = random.randint(
            max(1, orders_per_day - 1),
            orders_per_day + 1,
        )

        for _ in range(daily_order_count):
            item = items_df.sample(
                n=1,
                random_state=random.randint(1, 100000),
            ).iloc[0]

            equipment_cd = random.choice(active_equipment)

            plan_qty = random.randint(600, 1800)

            production_rate = np.random.uniform(0.92, 1.02)
            result_qty = int(plan_qty * production_rate)

            rework_rate = np.random.uniform(0.005, 0.04)
            rework_qty = int(result_qty * rework_rate)

            work_time = round(
                result_qty / np.random.uniform(250, 450),
                2,
            )

            orders.append(
                {
                    "order_id": f"ORD{order_sequence:06d}",
                    "order_date": order_date.strftime("%Y-%m-%d"),
                    "item_cd": item["item_cd"],
                    "equipment_cd": equipment_cd,
                    "plan_qty": plan_qty,
                    "result_qty": result_qty,
                    "rework_qty": rework_qty,
                    "work_time": work_time,
                }
            )

            order_sequence += 1

    return pd.DataFrame(orders)


def generate_weight_data(
    orders_df: pd.DataFrame,
    items_df: pd.DataFrame,
    equipment_df: pd.DataFrame,
) -> pd.DataFrame:
    """根据订单生成每次称重原始数据。"""

    measurements = []

    item_lookup = items_df.set_index("item_cd").to_dict("index")
    equipment_lookup = equipment_df.set_index(
        "equipment_cd"
    ).to_dict("index")

    measurement_sequence = 1

    for _, order in orders_df.iterrows():
        item = item_lookup[order["item_cd"]]
        equipment = equipment_lookup[order["equipment_cd"]]

        order_date = datetime.strptime(
            order["order_date"],
            "%Y-%m-%d",
        )

        start_hour = random.choice([6, 8, 10, 13, 15, 18])
        start_time = order_date + timedelta(hours=start_hour)

        sample_count = min(
            max(int(order["result_qty"] * 0.08), 80),
            180,
        )

        equipment_bias = {
            "EQ001": 1.5,
            "EQ002": 4.0,
            "EQ003": -0.5,
            "EQ004": 6.0,
        }.get(order["equipment_cd"], 0.0)

        process_std = {
            "ITEM001": 5.0,
            "ITEM002": 8.0,
            "ITEM003": 4.0,
            "ITEM004": 7.0,
            "ITEM005": 6.0,
        }[order["item_cd"]]

        drift = np.random.uniform(-2.0, 5.0)

        for sample_index in range(sample_count):
            event_time = start_time + timedelta(
                seconds=sample_index * random.randint(8, 20)
            )

            progressive_drift = drift * (
                sample_index / max(sample_count - 1, 1)
            )

            weight = np.random.normal(
                loc=(
                    item["std_weight"]
                    + equipment_bias
                    + progressive_drift
                ),
                scale=process_std,
            )

            if random.random() < 0.015:
                weight += np.random.choice([-1, 1]) * np.random.uniform(
                    15,
                    35,
                )

            weight = round(float(weight), 2)

            if weight > item["upper_limit"]:
                result_flag = "OVER"
            elif weight < item["lower_limit"]:
                result_flag = "UNDER"
            else:
                result_flag = "OK"

            measurements.append(
                {
                    "measurement_id": (
                        f"MSR{measurement_sequence:09d}"
                    ),
                    "event_time": event_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "order_id": order["order_id"],
                    "item_cd": order["item_cd"],
                    "equipment_cd": order["equipment_cd"],
                    "machine_name": equipment["equipment_name"],
                    "weight": weight,
                    "std_weight": item["std_weight"],
                    "upper_limit": item["upper_limit"],
                    "lower_limit": item["lower_limit"],
                    "result_flag": result_flag,
                    "weight_diff": round(
                        weight - item["std_weight"],
                        2,
                    ),
                }
            )

            measurement_sequence += 1

    return pd.DataFrame(measurements)


def save_dataframe(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    """保存DataFrame为CSV。"""

    output_path = RAW_DATA_DIR / filename

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Saved: {output_path} "
        f"({len(dataframe):,} rows)"
    )


def main() -> None:
    items_df = generate_items()
    equipment_df = generate_equipment()

    orders_df = generate_orders(
        items_df=items_df,
        equipment_df=equipment_df,
    )

    weight_df = generate_weight_data(
        orders_df=orders_df,
        items_df=items_df,
        equipment_df=equipment_df,
    )

    save_dataframe(
        items_df,
        "mst_item.csv",
    )

    save_dataframe(
        equipment_df,
        "mst_equipment.csv",
    )

    save_dataframe(
        orders_df,
        "wrk_order.csv",
    )

    save_dataframe(
        weight_df,
        "weight_rawdata.csv",
    )

    print("\nData generation completed.")
    print(f"Items: {len(items_df):,}")
    print(f"Equipment: {len(equipment_df):,}")
    print(f"Orders: {len(orders_df):,}")
    print(f"Measurements: {len(weight_df):,}")


if __name__ == "__main__":
    main()