from app.services.equipment_health_service import (
    calculate_equipment_health,
)


def main() -> None:
    result = calculate_equipment_health()

    print("\nEquipment Health Summary")
    print("=" * 80)

    if result.summary_df.empty:
        print("No equipment health data.")
        return

    print(
        result.summary_df.to_string(
            index=False
        )
    )

    print("\nDetailed Metrics")
    print("=" * 80)

    print(
        result.detail_df.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
    