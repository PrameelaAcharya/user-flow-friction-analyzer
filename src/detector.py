from dataclasses import dataclass

import pandas as pd


LONG_PAUSE_THRESHOLD = 15
NAVIGATION_LOOP_THRESHOLD = 2


@dataclass
class FrictionPoint:
    step_id: int
    friction_type: str
    severity: str
    impact: str
    reason: str


def detect_friction(df: pd.DataFrame) -> list[FrictionPoint]:
    """
    Detect usability friction using deterministic rules.

    Rules:
    1. Failed attempt
    2. Repeated failed action
    3. Long pause
    4. Repeated navigation loop
    """

    friction_points = []

    rows = df.to_dict("records")

    # Track navigation transitions.
    transitions = []

    for index, row in enumerate(rows):

        step_id = int(row["step_id"])
        action = str(row["action"])
        screen = str(row["screen"])
        target = str(row["target"])
        outcome = str(row["outcome"])
        duration = float(row["duration_seconds"])
        navigation_type = str(row["navigation_type"])

        # --------------------------------------------------
        # Rule 1: Failed attempt
        # --------------------------------------------------

        if outcome == "failed":

            error_message = str(row["error_message"]).strip()

            reason = f"Action '{target}' failed."

            if error_message:
                reason = (
                    f"Action '{target}' failed: "
                    f"{error_message}"
                )

            friction_points.append(
                FrictionPoint(
                    step_id=step_id,
                    friction_type="Failed Attempt",
                    severity="High",
                    impact="Blocks task progress",
                    reason=reason,
                )
            )

        # --------------------------------------------------
        # Rule 2: Repeated failed action
        # --------------------------------------------------

        if index > 0:

            previous = rows[index - 1]

            same_action = (
                action == str(previous["action"])
            )

            same_target = (
                target == str(previous["target"])
            )

            same_screen = (
                screen == str(previous["screen"])
            )

            previous_failed = (
                str(previous["outcome"]) == "failed"
            )

            current_failed = (
                outcome == "failed"
            )

            if (
                same_action
                and same_target
                and same_screen
                and previous_failed
                and current_failed
            ):

                friction_points.append(
                    FrictionPoint(
                        step_id=step_id,
                        friction_type="Repeated Action",
                        severity="Medium",
                        impact=(
                            "Suggests the user may not "
                            "get expected feedback"
                        ),
                        reason=(
                            f"'{action} {target}' was repeated "
                            "after a failed attempt."
                        ),
                    )
                )

        # --------------------------------------------------
        # Rule 3: Long pause
        # --------------------------------------------------

        if duration >= LONG_PAUSE_THRESHOLD:

            friction_points.append(
                FrictionPoint(
                    step_id=step_id,
                    friction_type="Long Pause",
                    severity="Medium",
                    impact="May indicate hesitation or confusion",
                    reason=f"Step took {duration:.0f} seconds.",
                )
            )

        # --------------------------------------------------
        # Track navigation transitions
        # --------------------------------------------------

        if index > 0:

            previous = rows[index - 1]

            previous_screen = str(previous["screen"])

            transition = (
                previous_screen,
                screen,
                navigation_type,
            )

            transitions.append(transition)

        # --------------------------------------------------
        # Rule 4: Repeated navigation loop
        # --------------------------------------------------

        if len(transitions) >= 4:

            recent = transitions[-4:]

            first_transition = recent[0]
            second_transition = recent[1]
            third_transition = recent[2]
            fourth_transition = recent[3]

            # Pattern:
            #
            # A -> B
            # B -> A
            # A -> B
            # B -> A
            #
            # This indicates repeated navigation between
            # the same two screens.

            repeated_cycle = (
                first_transition[0] == third_transition[0]
                and first_transition[1] == third_transition[1]
                and second_transition[0] == fourth_transition[0]
                and second_transition[1] == fourth_transition[1]
            )

            has_back_navigation = (
                first_transition[2] == "back"
                or second_transition[2] == "back"
                or third_transition[2] == "back"
                or fourth_transition[2] == "back"
            )

            if repeated_cycle and has_back_navigation:

                friction_points.append(
                    FrictionPoint(
                        step_id=step_id,
                        friction_type="Backtracking",
                        severity="Low",
                        impact="May indicate navigation difficulty",
                        reason=(
                            "User repeatedly moved between "
                            f"'{first_transition[0]}' and "
                            f"'{first_transition[1]}'."
                        ),
                    )
                )

                # Prevent the same loop from generating
                # another friction point on every step.
                transitions = []

    return friction_points