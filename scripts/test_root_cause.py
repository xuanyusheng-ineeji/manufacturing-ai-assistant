from app.services.root_cause_service import (
    analyze_root_cause,
)


def main() -> None:
    result = analyze_root_cause()

    print("\nTarget equipment:")
    print(
        result.target_equipment_cd,
        result.target_equipment_name,
    )

    print("\nRoot-cause analysis:")
    print(result.answer)

    print("\nEquipment ranking:")
    print(
        result.equipment_ranking_df
        .to_string(index=False)
    )

    print("\nAbnormal type distribution:")
    print(
        result.abnormal_type_df
        .to_string(index=False)
    )

    print("\nProduct contribution:")
    print(
        result.product_contribution_df
        .to_string(index=False)
    )

    print("\nHourly contribution:")
    print(
        result.hourly_contribution_df
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()