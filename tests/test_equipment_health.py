from app.services.equipment_health_service import (
    calculate_health_score,
    get_health_status,
)


def test_perfect_health_score() -> None:
    score = calculate_health_score(
        abnormal_rate=0,
        rework_rate=0,
        abnormal_rate_change=0,
        avg_weight_diff_rate=0,
    )

    assert score == 100.0


def test_health_score_is_never_negative() -> None:
    score = calculate_health_score(
        abnormal_rate=100,
        rework_rate=100,
        abnormal_rate_change=100,
        avg_weight_diff_rate=100,
    )

    assert score == 0.0


def test_health_score_decreases_with_risk() -> None:
    healthy_score = calculate_health_score(
        abnormal_rate=1,
        rework_rate=1,
        abnormal_rate_change=0,
        avg_weight_diff_rate=0.5,
    )

    risky_score = calculate_health_score(
        abnormal_rate=8,
        rework_rate=5,
        abnormal_rate_change=3,
        avg_weight_diff_rate=4,
    )

    assert healthy_score > risky_score


def test_health_status() -> None:
    assert get_health_status(90) == "Healthy"
    assert get_health_status(75) == "Watch"
    assert get_health_status(60) == "Risk"
    assert get_health_status(40) == "Critical"