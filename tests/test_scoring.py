from src.detector import FrictionPoint
from src.scoring import calculate_score


def test_failed_attempt_is_medium():
    points = [
        FrictionPoint(
            step_id=4,
            friction_type="Failed Attempt",
            severity="High",
            impact="Blocks task progress",
            reason="Action 'Login Button' failed: Invalid password",
        )
    ]

    result = calculate_score(points)

    assert len(result) == 1
    assert result[0].step_id == 4
    assert result[0].score == 3
    assert result[0].severity == "Medium"


def test_failed_attempt_plus_repeated_action_is_high():
    points = [
        FrictionPoint(
            step_id=5,
            friction_type="Failed Attempt",
            severity="High",
            impact="Blocks task progress",
            reason="Action 'Login Button' failed: Invalid password",
        ),
        FrictionPoint(
            step_id=5,
            friction_type="Repeated Action",
            severity="Medium",
            impact="Suggests the user may not get expected feedback",
            reason="'click Login Button' was repeated after a failed attempt.",
        ),
    ]

    result = calculate_score(points)

    assert len(result) == 1
    assert result[0].step_id == 5
    assert result[0].score == 5
    assert result[0].severity == "High"


def test_long_pause_is_low():
    points = [
        FrictionPoint(
            step_id=10,
            friction_type="Long Pause",
            severity="Medium",
            impact="May indicate hesitation or confusion",
            reason="Step took 20 seconds.",
        )
    ]

    result = calculate_score(points)

    assert result[0].score == 2
    assert result[0].severity == "Low"


def test_multiple_steps_are_sorted_by_score():
    points = [
        FrictionPoint(
            step_id=10,
            friction_type="Long Pause",
            severity="Medium",
            impact="May indicate hesitation or confusion",
            reason="Step took 20 seconds.",
        ),
        FrictionPoint(
            step_id=4,
            friction_type="Failed Attempt",
            severity="High",
            impact="Blocks task progress",
            reason="Login failed.",
        ),
    ]

    result = calculate_score(points)

    assert result[0].step_id == 4
    assert result[0].score == 3
    assert result[1].step_id == 10
    assert result[1].score == 2