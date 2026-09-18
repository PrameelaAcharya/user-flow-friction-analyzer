REQUIRED_COLUMNS = {
    "session_id",
    "step_id",
    "timestamp",
    "action",
    "screen",
    "target",
    "duration_seconds",
    "outcome",
    "error_message",
    "navigation_type",
}


def validate_session_data(data):
    """
    Validate that the uploaded session log contains
    all columns required by the analysis pipeline.
    """

    if data.empty:
        return False, "The session log is empty."

    missing_columns = REQUIRED_COLUMNS - set(data.columns)

    if missing_columns:
        return False, (
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if data["step_id"].isnull().any():
        return False, "Step ID contains missing values."

    if data["duration_seconds"].isnull().any():
        return False, "Duration contains missing values."

    return True, "Session data is valid."