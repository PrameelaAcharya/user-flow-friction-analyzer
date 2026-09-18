import pandas as pd

from src.validator import validate_session_data


def test_valid_session_data():
    data = pd.DataFrame({
        "session_id": ["S001"],
        "step_id": [1],
        "timestamp": ["2026-09-15 10:00:01"],
        "action": ["open"],
        "screen": ["Login Page"],
        "target": ["Login Form"],
        "duration_seconds": [2],
        "outcome": ["success"],
        "error_message": [""],
        "navigation_type": ["direct"],
    })

    valid, message = validate_session_data(data)

    assert valid is True
    assert message == "Session data is valid."


def test_missing_required_column():
    data = pd.DataFrame({
        "session_id": ["S001"],
        "step_id": [1],
    })

    valid, message = validate_session_data(data)

    assert valid is False
    assert "Missing required columns" in message


def test_empty_session_data():
    data = pd.DataFrame()

    valid, message = validate_session_data(data)

    assert valid is False
    assert message == "The session log is empty."


def test_missing_step_id():
    data = pd.DataFrame({
        "session_id": ["S001"],
        "step_id": [None],
        "timestamp": ["2026-09-15 10:00:01"],
        "action": ["open"],
        "screen": ["Login Page"],
        "target": ["Login Form"],
        "duration_seconds": [2],
        "outcome": ["success"],
        "error_message": [""],
        "navigation_type": ["direct"],
    })

    valid, message = validate_session_data(data)

    assert valid is False
    assert message == "Step ID contains missing values."