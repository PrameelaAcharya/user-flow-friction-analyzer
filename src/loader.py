from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"step_id", "timestamp", "screen", "action", "target", "duration_seconds", "outcome"}

def load_session_log(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Session log not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Session log is empty.")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce")
    if df["timestamp"].isna().any():
        raise ValueError("Invalid timestamp found.")
    if df["duration_seconds"].isna().any() or (df["duration_seconds"] < 0).any():
        raise ValueError("duration_seconds must be valid and non-negative.")
    return df.sort_values("step_id").reset_index(drop=True)
