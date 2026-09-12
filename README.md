# User Flow Friction Analyzer

Simple 8–10 hour prototype for the Fresher Hackathon challenge.

## Objective
Review a bounded usability session step log and identify repeated actions, backtracking, long pauses, and failed attempts.

Required outputs:
1. Friction-point list with step references
2. Severity/impact tag per friction point
3. One-paragraph flow experience summary

AI is used for exactly one task: summarizing the top detected friction points and likely user impact.

## Pipeline
Synthetic CSV → validation → rule-based detection → severity scoring → AI summary → Streamlit dashboard

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Test
```bash
pytest -q
```

See `docs/COMMIT_PLAN.md` for the commit-by-commit workflow.
