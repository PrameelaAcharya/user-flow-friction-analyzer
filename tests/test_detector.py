from pathlib import Path

from src.loader import load_session_log
from src.detector import detect_friction


def test_detects_expected_friction_types():
    points = detect_friction(
        load_session_log(Path("data/session_log.csv"))
    )

    types = {p.friction_type for p in points}

    assert {
        "Failed Attempt",
        "Repeated Action",
        "Long Pause",
    } <= types


def test_failed_attempt_is_detected():
    points = detect_friction(
        load_session_log(Path("data/session_log.csv"))
    )

    failed = [
        p for p in points
        if p.friction_type == "Failed Attempt"
    ]

    assert failed


def test_repeated_action_is_detected():
    points = detect_friction(
        load_session_log(Path("data/session_log.csv"))
    )

    repeated = [
        p for p in points
        if p.friction_type == "Repeated Action"
    ]

    assert repeated


def test_long_pause_is_detected():
    points = detect_friction(
        load_session_log(Path("data/session_log.csv"))
    )

    long_pauses = [
        p for p in points
        if p.friction_type == "Long Pause"
    ]

    assert long_pauses

def test_detects_navigation_backtracking():
    points = detect_friction(
        load_session_log(
            Path("tests/data/navigation_loop.csv")
        )
    )

    backtracking = [
        p for p in points
        if p.friction_type == "Backtracking"
    ]

    assert backtracking