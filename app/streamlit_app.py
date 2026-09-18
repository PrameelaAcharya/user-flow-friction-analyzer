import os
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.detector import detect_friction
from src.scoring import calculate_score
from src.summarizer import (
    fallback_summary,
    summarize_with_ollama,
)
from src.validator import validate_session_data


SAMPLE_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "session_log.csv",
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="User Flow Friction Analyzer",
    page_icon="🔎",
    layout="wide",
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "session_data" not in st.session_state:
    st.session_state.session_data = None

if "scored_points" not in st.session_state:
    st.session_state.scored_points = []


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🔎 User Flow Friction Analyzer")

st.caption(
    "Analyze usability-session logs to identify friction, "
    "prioritize severity, and summarize the overall experience."
)


# ---------------------------------------------------------
# SESSION INPUT
# ---------------------------------------------------------

st.subheader("1. Session Input")

input_method = st.radio(
    "Choose how you want to provide the session log:",
    ["Use Sample Session", "Upload CSV"],
    horizontal=True,
)


session_data = None


if input_method == "Use Sample Session":

    st.info("Using the built-in 20-step sample session.")

    session_data = pd.read_csv(SAMPLE_FILE)


else:

    uploaded_file = st.file_uploader(
        "Upload a session log CSV",
        type=["csv"],
        help="Upload a CSV containing the required session-log columns.",
    )

    if uploaded_file is not None:

        try:
            session_data = pd.read_csv(uploaded_file)

        except Exception as error:

            st.error(
                f"Unable to read the CSV file: {error}"
            )


# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

analyze_clicked = st.button(
    "🔍 Analyze Session",
    type="primary",
    use_container_width=True,
)


if analyze_clicked:

    if session_data is None:

        st.warning(
            "Please upload a CSV or use the sample session."
        )

    else:

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        is_valid, validation_message = (
            validate_session_data(session_data)
        )

        if not is_valid:

            st.error(
                f"Invalid session log: {validation_message}"
            )

        else:

            # ---------------------------------------------
            # FRICTION DETECTION
            # ---------------------------------------------

            friction_points = detect_friction(
                session_data
            )

            # ---------------------------------------------
            # SEVERITY SCORING
            # ---------------------------------------------

            scored_points = calculate_score(
                friction_points
            )

            # ---------------------------------------------
            # SAVE RESULTS
            # ---------------------------------------------

            st.session_state.session_data = (
                session_data
            )

            st.session_state.scored_points = (
                scored_points
            )

            st.session_state.analysis_complete = True

            st.success(
                "Session analyzed successfully."
            )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.analysis_complete:

    session_data = st.session_state.session_data

    scored_points = st.session_state.scored_points


    # -----------------------------------------------------
    # SESSION OVERVIEW
    # -----------------------------------------------------

    st.subheader("2. Session Overview")

    total_steps = len(session_data)

    friction_count = len(scored_points)

    high_count = sum(
        point.severity == "High"
        for point in scored_points
    )

    medium_count = sum(
        point.severity == "Medium"
        for point in scored_points
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Steps",
        total_steps,
    )

    col2.metric(
        "Friction Points",
        friction_count,
    )

    col3.metric(
        "High Severity",
        high_count,
    )

    col4.metric(
        "Medium Severity",
        medium_count,
    )


    # -----------------------------------------------------
    # SEVERITY OVERVIEW
    # -----------------------------------------------------

    st.subheader("3. Severity Overview")

    severity_counts = pd.Series(
        {
            "High": sum(
                point.severity == "High"
                for point in scored_points
            ),
            "Medium": sum(
                point.severity == "Medium"
                for point in scored_points
            ),
            "Low": sum(
                point.severity == "Low"
                for point in scored_points
            ),
        }
    )

    st.bar_chart(severity_counts)


    # -----------------------------------------------------
    # DETECTED FRICTION
    # -----------------------------------------------------

    st.subheader("4. Detected Friction Points")

    if not scored_points:

        st.success(
            "No friction points were detected."
        )

    else:

        friction_rows = []

        for point in scored_points:

            friction_rows.append(
                {
                    "Step": point.step_id,
                    "Friction Type": ", ".join(
                        point.friction_types
                    ),
                    "Score": point.score,
                    "Severity": point.severity,
                    "Impact": point.impact,
                    "Reason": " ".join(
                        point.reasons
                    ),
                }
            )

        friction_df = pd.DataFrame(
            friction_rows
        )

        st.dataframe(
            friction_df,
            use_container_width=True,
            hide_index=True,
        )


    # -----------------------------------------------------
    # FRICTION SCORE BY STEP
    # -----------------------------------------------------

    if scored_points:

        st.subheader("5. Friction Score by Step")

        score_chart = pd.DataFrame(
            {
                "Step": [
                    point.step_id
                    for point in scored_points
                ],
                "Score": [
                    point.score
                    for point in scored_points
                ],
            }
        )

        st.bar_chart(
            score_chart.set_index("Step")
        )


    # -----------------------------------------------------
    # SESSION FLOW
    # -----------------------------------------------------

    st.subheader("6. Session Flow")

    friction_by_step = {
        point.step_id: point
        for point in scored_points
    }

    total_steps = len(session_data)

    timeline_columns = st.columns(
        min(total_steps, 5)
    )

    for index, (_, row) in enumerate(
        session_data.iterrows()
    ):

        column = timeline_columns[
            index % len(timeline_columns)
        ]

        step_id = int(row["step_id"])

        with column:

            if step_id in friction_by_step:

                point = friction_by_step[step_id]

                if point.severity == "High":

                    marker = "🔴"

                elif point.severity == "Medium":

                    marker = "🟠"

                else:

                    marker = "🟡"

                st.markdown(
                    f"**{marker} Step {step_id}**"
                )

                st.caption(
                    f"{point.severity} · "
                    f"Score {point.score}"
                )

            else:

                st.markdown(
                    f"🟢 **Step {step_id}**"
                )

                st.caption("Normal")


    # -----------------------------------------------------
    # FLOW EXPERIENCE SUMMARY
    # -----------------------------------------------------

    st.subheader(
        "7. Flow Experience Summary"
    )

    if scored_points:

        summary_type = st.radio(
            "Choose summary type:",
            [
                "Normal Summary",
                "AI Summary",
            ],
            horizontal=True,
            key="summary_type",
        )

        if summary_type == "Normal Summary":

            summary = fallback_summary(
                scored_points
            )

            st.info(summary)

        else:

            st.caption(
                "AI summary generated using local Ollama."
            )

            summary = summarize_with_ollama(
                scored_points
            )

            st.info(summary)

    else:

        st.success(
            "The session completed without "
            "detected friction signals."
        )


    # -----------------------------------------------------
    # RAW SESSION LOG
    # -----------------------------------------------------

    st.subheader("8. Session Log")

    with st.expander(
        "View raw session data"
    ):

        st.dataframe(
            session_data,
            use_container_width=True,
            hide_index=True,
        )


    # -----------------------------------------------------
    # ASSUMPTIONS
    # -----------------------------------------------------

    with st.expander("Assumptions"):

        st.markdown(
            """
            - A long pause is defined as 15 seconds or more.
            - Failed outcomes are treated as friction signals.
            - Immediate repeated actions may indicate difficulty.
            - Repeated navigation between screens may indicate backtracking.
            - Severity is calculated from friction-type scores.
            - The AI is used only to summarize detected friction.
            """
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "User Flow Friction Analyzer · "
    "Rule-based friction detection + local AI summary"
)