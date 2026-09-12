from pathlib import Path
from src.loader import load_session_log
from src.detector import detect_friction

def test_detects_expected_friction_types():
    points = detect_friction(load_session_log(Path("data/session_log.csv")))
    types = {p.friction_type for p in points}
    assert {"Failed attempt", "Repeated action", "Long pause", "Backtracking"} <= types

def test_failed_attempt_is_high_severity():
    points = detect_friction(load_session_log(Path("data/session_log.csv")))
    failed = [p for p in points if p.friction_type == "Failed attempt"]
    assert failed and all(p.severity == "High" for p in failed)
