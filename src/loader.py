from pathlib import Path

import pandas as pd


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


def load_session_log(file_path: str | Path) -> pd.DataFrame:
    """Load and validate a usability session log."""

    df = pd.read_csv(file_path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError("Session log is empty.")

    # Validate timestamps
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    if df["timestamp"].isna().any():
        raise ValueError("Invalid timestamp found in session log.")

    # Validate duration
    df["duration_seconds"] = pd.to_numeric(
        df["duration_seconds"],
        errors="coerce",
    )

    if df["duration_seconds"].isna().any():
        raise ValueError(
            "Invalid duration_seconds value found."
        )

    if (df["duration_seconds"] < 0).any():
        raise ValueError(
            "duration_seconds cannot be negative."
        )

    # Validate step IDs
    if df["step_id"].duplicated().any():
        raise ValueError("Duplicate step_id values found.")

        # Validate outcomes
    valid_outcomes = {"success", "failed"}

    invalid_outcomes = (
        set(df["outcome"].dropna()) - valid_outcomes
    )

    if invalid_outcomes:
        raise ValueError(
            f"Invalid outcome values: {sorted(invalid_outcomes)}"
        )

    # Validate navigation types
    valid_navigation_types = {"forward", "back", "direct"}

    invalid_navigation_types = (
        set(df["navigation_type"].dropna())
        - valid_navigation_types
    )

    if invalid_navigation_types:
        raise ValueError(
            "Invalid navigation_type values: "
            f"{sorted(invalid_navigation_types)}"
        )

    df = df.sort_values("step_id").reset_index(drop=True)

    return df