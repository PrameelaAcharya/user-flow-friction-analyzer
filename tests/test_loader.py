from pathlib import Path
from src.loader import load_session_log

def test_load_sample_data():
    df = load_session_log(Path("data/session_log.csv"))
    assert len(df) == 20
    assert "step_id" in df.columns
