from dataclasses import dataclass
import pandas as pd

LONG_PAUSE_SECONDS = 15

@dataclass
class FrictionPoint:
    step_id: int
    friction_type: str
    severity: str
    impact: str
    reason: str

def detect_friction(df: pd.DataFrame) -> list[FrictionPoint]:
    points = []
    for i, row in df.iterrows():
        step_id = int(row["step_id"])
        if str(row["outcome"]).lower() == "failed":
            points.append(FrictionPoint(step_id, "Failed attempt", "High", "Blocks task progress", f"Action '{row['target']}' failed."))
        if float(row["duration_seconds"]) >= LONG_PAUSE_SECONDS:
            points.append(FrictionPoint(step_id, "Long pause", "Medium", "May indicate hesitation or confusion", f"Step took {row['duration_seconds']:.0f} seconds."))
        if i > 0:
            prev = df.iloc[i - 1]
            if str(prev["target"]).strip().lower() == str(row["target"]).strip().lower() and str(prev["action"]).strip().lower() == str(row["action"]).strip().lower():
                points.append(FrictionPoint(step_id, "Repeated action", "Medium", "Suggests the user may not get expected feedback", f"'{row['action']} {row['target']}' was repeated immediately."))
        if i > 0:
            previous_screen = str(df.iloc[i - 1]["screen"])
            current_screen = str(row["screen"])
            earlier_screens = set(df.iloc[:i]["screen"].astype(str))
            if current_screen in earlier_screens and current_screen != previous_screen:
                points.append(FrictionPoint(step_id, "Backtracking", "Low", "May indicate navigation difficulty", f"User returned to '{current_screen}' after moving away from it."))
    return points
