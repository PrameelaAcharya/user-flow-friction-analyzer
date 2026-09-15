from collections import defaultdict
from dataclasses import dataclass

from src.detector import FrictionPoint


FRICTION_SCORES = {
    "Failed Attempt": 3,
    "Repeated Action": 2,
    "Long Pause": 2,
    "Backtracking": 1,
}


@dataclass
class ScoredFriction:
    step_id: int
    friction_types: list[str]
    score: int
    severity: str
    impact: str
    reasons: list[str]


def calculate_score(friction_points: list[FrictionPoint]) -> list[ScoredFriction]:
    """
    Combine friction signals occurring at the same step
    and calculate an overall severity.
    """

    grouped = defaultdict(list)

    for point in friction_points:
        grouped[point.step_id].append(point)

    scored_points = []

    for step_id, points in grouped.items():

        score = sum(
            FRICTION_SCORES.get(point.friction_type, 0)
            for point in points
        )

        if score >= 5:
            severity = "High"
        elif score >= 3:
            severity = "Medium"
        else:
            severity = "Low"

        friction_types = [
            point.friction_type
            for point in points
        ]

        reasons = [
            point.reason
            for point in points
        ]

        # Use the strongest impact associated with the signals.
        if severity == "High":
            impact = "Strong evidence of user friction"
        elif severity == "Medium":
            impact = "May indicate hesitation or difficulty"
        else:
            impact = "May indicate minor navigation difficulty"

        scored_points.append(
            ScoredFriction(
                step_id=step_id,
                friction_types=friction_types,
                score=score,
                severity=severity,
                impact=impact,
                reasons=reasons,
            )
        )

    return sorted(
        scored_points,
        key=lambda point: (
            -point.score,
            point.step_id,
        ),
    )