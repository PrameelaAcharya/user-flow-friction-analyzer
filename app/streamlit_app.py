import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.loader import load_session_log
from src.detector import detect_friction
from src.scoring import rank_friction
from src.summarizer import summarize_with_ollama, fallback_summary

st.set_page_config(page_title="User Flow Friction Analyzer", layout="wide")
st.title("User Flow Friction Analyzer")
st.caption("Synthetic usability-session analysis prototype")

df = load_session_log(ROOT / "data" / "session_log.csv")
points = rank_friction(detect_friction(df))

st.subheader("1. Friction points")
st.dataframe([{"Step": p.step_id, "Friction": p.friction_type, "Severity": p.severity, "Likely impact": p.impact, "Reason": p.reason} for p in points], use_container_width=True)

st.subheader("2. Severity / impact")
c1, c2, c3 = st.columns(3)
c1.metric("High", sum(p.severity == "High" for p in points))
c2.metric("Medium", sum(p.severity == "Medium" for p in points))
c3.metric("Low", sum(p.severity == "Low" for p in points))

st.subheader("3. Flow experience summary")
use_ai = st.toggle("Use local AI summary (Ollama)", value=False)
st.write(summarize_with_ollama(points) if use_ai else fallback_summary(points))

with st.expander("Input session log"):
    st.dataframe(df, use_container_width=True)
with st.expander("Assumptions"):
    st.write("Long pause = 15+ seconds; failed outcome = friction; immediate repeated action = repetition; returning to an earlier screen = possible backtracking; AI is only used for summarization.")
