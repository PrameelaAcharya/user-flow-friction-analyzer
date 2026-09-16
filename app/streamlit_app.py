import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.loader import load_session_log
from src.detector import detect_friction
from src.scoring import calculate_score
from src.summarizer import summarize_with_ollama, fallback_summary


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="User Flow Friction Analyzer",
    page_icon="🔎",
    layout="wide",
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🔎 User Flow Friction Analyzer")

st.caption(
    "Analyze a bounded usability session and identify repeated actions, "
    "failed attempts, pauses, and navigation friction."
)


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
# Prepare summary values
# --------------------------------------------------

total_steps = len(df)
friction_count = len(scored_points)

high_count = sum(
    p.severity == "High"
    for p in scored_points
)

medium_count = sum(
    p.severity == "Medium"
    for p in scored_points
)

low_count = sum(
    p.severity == "Low"
    for p in scored_points
)


# --------------------------------------------------
# Session overview
# --------------------------------------------------

st.subheader("Session overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total steps",
    total_steps,
)

c2.metric(
    "Friction points",
    friction_count,
)

c3.metric(
    "High severity",
    high_count,
)

c4.metric(
    "Medium / Low",
    medium_count + low_count,
)


st.caption(
    "Pipeline: Session Log → Friction Detection → Severity Scoring → "
    "Top Friction Analysis → UX Summary"
)


# ==================================================
# VISUALIZATIONS
# ==================================================

if scored_points:

    # --------------------------------------------------
    # Visualization 1: Severity distribution
    # --------------------------------------------------

    st.subheader("Friction severity distribution")

    severity_data = {
        "Severity": [
            "High",
            "Medium",
            "Low",
        ],
        "Count": [
            high_count,
            medium_count,
            low_count,
        ],
    }

    st.bar_chart(
        severity_data,
        x="Severity",
        y="Count",
        use_container_width=True,
    )

    st.caption(
        "Number of detected friction points by calculated severity."
    )


    # --------------------------------------------------
    # Visualization 2: Friction score by step
    # --------------------------------------------------

    st.subheader("Friction score by step")

    score_data = {
        "Step": [
            f"Step {p.step_id}"
            for p in scored_points
        ],
        "Score": [
            p.score
            for p in scored_points
        ],
    }

    st.bar_chart(
        score_data,
        x="Step",
        y="Score",
        use_container_width=True,
    )

    st.caption(
        "Higher scores indicate a stronger combination of friction signals."
    )


    # --------------------------------------------------
    # Visualization 3: Session timeline
    # --------------------------------------------------

    st.subheader("Session timeline")

    friction_by_step = {
        p.step_id: p
        for p in scored_points
    }

    timeline_columns = st.columns(
        min(total_steps, 8)
    )

    for index, row in df.iterrows():

        step_id = int(row["step_id"])

        if step_id in friction_by_step:
            friction = friction_by_step[step_id]

            if friction.severity == "High":
                marker = "🔴"
            elif friction.severity == "Medium":
                marker = "🟠"
            else:
                marker = "🟡"

            label = (
                f"{marker} **Step {step_id}**"
            )

            with timeline_columns[index % len(timeline_columns)]:
                st.markdown(label)
                st.caption(
                    f"{', '.join(friction.friction_types)}"
                )

        else:
            with timeline_columns[index % len(timeline_columns)]:
                st.markdown(
                    f"🟢 **Step {step_id}**"
                )
                st.caption(
                    str(row["action"])
                )

    st.caption(
        "🟢 Normal step   🟡 Low friction   "
        "🟠 Medium friction   🔴 High friction"
    )


# ==================================================
# REQUIRED OUTPUTS
# ==================================================


# --------------------------------------------------
# 1. Friction points
# --------------------------------------------------

st.subheader("1. Friction points")

if not scored_points:

    st.success(
        "No friction signals were detected in this session."
    )

else:

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
        hide_index=True,
    )


# --------------------------------------------------
# 2. Severity / impact
# --------------------------------------------------

st.subheader("2. Severity / impact")

c1, c2, c3 = st.columns(3)

c1.metric(
    "High",
    high_count,
)

c2.metric(
    "Medium",
    medium_count,
)

c3.metric(
    "Low",
    low_count,
)

if scored_points:

    st.info(
        "Severity is calculated from the combination of "
        "detected friction signals at each step."
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

    st.write(
        summarize_with_ollama(scored_points)
    )

else:

    st.write(
        fallback_summary(scored_points)
    )


# --------------------------------------------------
# Input session log
# --------------------------------------------------

with st.expander("View input session log"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Assumptions
# --------------------------------------------------

with st.expander("View analysis assumptions"):

    st.write(
        "• Long pause = 15+ seconds\n\n"
        "• Failed outcome = friction\n\n"
        "• Immediate repeated action = repetition\n\n"
        "• Repeated navigation cycle = possible backtracking\n\n"
        "• AI is only used for summarization"
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "Prototype built for usability-session friction analysis."
)