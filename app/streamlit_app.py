import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.loader import load_session_log
from src.detector import detect_friction
from src.scoring import calculate_score
from src.summarizer import summarize_with_ollama, fallback_summary


st.set_page_config(
    page_title="User Flow Friction Analyzer",
    layout="wide",
)

st.title("User Flow Friction Analyzer")
st.caption("Synthetic usability-session analysis prototype")


# --------------------------------------------------
# Load session data
# --------------------------------------------------

df = load_session_log(
    ROOT / "data" / "session_log.csv"
)


# --------------------------------------------------
# Detect friction
# --------------------------------------------------

points = detect_friction(df)


# --------------------------------------------------
# Calculate severity scores
# --------------------------------------------------

scored_points = calculate_score(points)


# --------------------------------------------------
# 1. Friction points
# --------------------------------------------------

st.subheader("1. Friction points")

st.dataframe(
    [
        {
            "Step": p.step_id,
            "Friction": ", ".join(p.friction_types),
            "Score": p.score,
            "Severity": p.severity,
            "Likely impact": p.impact,
            "Reason": " ".join(p.reasons),
        }
        for p in scored_points
    ],
    use_container_width=True,
)


# --------------------------------------------------
# 2. Severity / impact
# --------------------------------------------------

st.subheader("2. Severity / impact")

c1, c2, c3 = st.columns(3)

c1.metric(
    "High",
    sum(p.severity == "High" for p in scored_points),
)

c2.metric(
    "Medium",
    sum(p.severity == "Medium" for p in scored_points),
)

c3.metric(
    "Low",
    sum(p.severity == "Low" for p in scored_points),
)


# --------------------------------------------------
# 3. Flow experience summary
# --------------------------------------------------

st.subheader("3. Flow experience summary")

use_ai = st.toggle(
    "Use local AI summary (Ollama)",
    value=False,
)

if use_ai:
    st.write(summarize_with_ollama(scored_points))
else:
    st.write(fallback_summary(scored_points))


# --------------------------------------------------
# Input session log
# --------------------------------------------------

with st.expander("Input session log"):
    st.dataframe(
        df,
        use_container_width=True,
    )


# --------------------------------------------------
# Assumptions
# --------------------------------------------------

with st.expander("Assumptions"):
    st.write(
        "Long pause = 15+ seconds; "
        "failed outcome = friction; "
        "immediate repeated action = repetition; "
        "repeated navigation cycle = possible backtracking; "
        "AI is only used for summarization."
    )