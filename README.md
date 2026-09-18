````markdown
# User Flow Friction Analyzer

A lightweight UX analysis tool that analyzes a bounded user session log and identifies potential points of friction such as failed attempts, repeated actions, long pauses, and backtracking.

The project combines rule-based friction detection and severity scoring with a local AI summarization step to provide a concise overview of the overall flow experience.

---

## Problem Statement

Users can experience friction while completing a digital task without the issue being immediately visible.

Examples of possible friction include:

- Failed interactions
- Repeated actions
- Long pauses during a task
- Moving backward and forward between screens
- Temporary blocks that interrupt task progress

The goal of this project is to analyze a session-level event log and convert these interaction patterns into structured UX insights.

The prototype produces three main outputs:

1. A friction list with step references
2. Severity and likely impact for each friction point
3. A concise summary of the overall flow experience

---

## Solution

The analyzer processes a session log through a simple end-to-end pipeline:

```text
Session Log
     |
     v
Data Loading
     |
     v
Friction Detection
     |
     v
Severity Scoring
     |
     v
Top Friction Selection
     |
     v
AI Summary
     |
     v
Streamlit Dashboard
````

The system intentionally separates deterministic analysis from AI.

Rule-based logic is used to detect friction and calculate severity. A local language model is used only to summarize the highest-priority detected friction points and their likely impact.

---

## Key Features

### 1. Failed Attempt Detection

Detects interactions where the session log records:

```text
outcome = failed
```

The analyzer records the affected step, target, and available error information.

---

### 2. Repeated Action Detection

Detects repeated actions following a failed attempt.

For example:

```text
Step 4 → Click Login Button → Failed

Step 5 → Click Login Button → Failed
```

The second interaction is also identified as a repeated action.

---

### 3. Long Pause Detection

A step taking 15 seconds or longer is treated as a possible long pause.

Example:

```text
Step 10 → Search Button → 20 seconds
```

A long pause is treated as a possible indicator of hesitation or difficulty rather than proof of user confusion.

---

### 4. Backtracking Detection

Detects repeated movement between screens in opposite directions.

Example:

```text
Products Page
      |
      v
Product Details
      |
      v
Products Page
      |
      v
Product Details
```

This can indicate possible navigation difficulty.

---

### 5. Severity Scoring

Each detected friction type has a predefined score:

| Friction Type   | Score |
| --------------- | ----: |
| Failed Attempt  |     3 |
| Repeated Action |     2 |
| Long Pause      |     2 |
| Backtracking    |     1 |

When multiple friction signals occur at the same step, their scores are combined.

Severity is assigned using the total score:

| Total Score | Severity |
| ----------: | -------- |
|   5 or more | High     |
|         3–4 | Medium   |
|         1–2 | Low      |

Severity is used as a prioritization signal and does not represent a direct measurement of user emotion.

---

## AI Usage

The project intentionally uses AI for one core task:

> Summarizing the top detected friction points and their likely impact on the user experience.

The AI does **not** determine whether an event is a friction point.

The analysis pipeline is:

```text
Session Log
     |
     v
Rule-Based Detection
     |
     v
Severity Scoring
     |
     v
Top Friction Points
     |
     v
Local LLM
     |
     v
UX Flow Summary
```

### Local AI

The project uses Ollama with a locally available language model.

Default configuration:

```text
Ollama
Model: llama3
Endpoint: http://localhost:11434/api/generate
```

Using a local model allows the prototype to run without requiring a paid external AI API.

If Ollama is unavailable, the application provides an evidence-based fallback summary.

---

## Sample User Flow

The included synthetic session contains 20 steps representing a common shopping flow:

```text
Login
  |
  v
Product Search
  |
  v
Product Details
  |
  v
Cart
  |
  v
Checkout
```

The session intentionally contains multiple friction scenarios while still completing the overall task successfully.

### Sample friction scenarios

#### Step 4 — Failed Attempt

The login interaction fails because of an invalid password.

```text
Failed Attempt
```

#### Step 5 — Failed Attempt + Repeated Action

The login interaction fails again and the Login Button is repeated after the previous failed attempt.

```text
Failed Attempt
+
Repeated Action
```

#### Step 10 — Long Pause

The Search Button interaction takes 20 seconds.

```text
Long Pause
```

#### Step 14 — Backtracking

The user repeatedly moves between the Products Page and Product Details.

```text
Backtracking
```

The session subsequently continues through the cart and checkout flow.

---

## Example Analysis

For the included sample session, the detector identifies the following friction points:

| Step | Friction                         |
| ---: | -------------------------------- |
|    4 | Failed Attempt                   |
|    5 | Failed Attempt + Repeated Action |
|   10 | Long Pause                       |
|   14 | Backtracking                     |

Step 5 contains two friction signals, so the scoring system combines both signals when determining its priority.

---

## Dashboard

The project provides an interactive Streamlit dashboard.

The dashboard includes:

### Session Overview

Displays high-level information about the analyzed session, including:

* Total steps
* Number of detected friction points
* Severity distribution

### Severity Distribution

A visualization showing the distribution of detected friction across severity levels.

### Friction Score by Step

A visualization showing the calculated friction score for affected steps.

### Session Timeline

A visual timeline of the session showing normal steps and detected friction points.

### Detected Friction Points

Displays:

* Step reference
* Friction type
* Severity
* Impact
* Reason

### Flow Experience Summary

Displays the AI-generated summary of the overall flow experience.

### Raw Session Log

The original session data can also be inspected from the dashboard.

---

## Technology Stack

| Technology | Purpose                |
| ---------- | ---------------------- |
| Python     | Core application logic |
| Pandas     | Session-log processing |
| Streamlit  | Interactive dashboard  |
| Ollama     | Local AI inference     |
| Llama 3    | Local language model   |
| Pytest     | Automated testing      |
| Git        | Version control        |

---

## Project Structure

```text
user_flow_friction_analyzer/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── __init__.py
│   ├── loader.py
│   ├── detector.py
│   ├── scoring.py
│   └── summarizer.py
│
├── data/
│   └── session_log.csv
│
├── tests/
│   ├── __init__.py
│   ├── test_loader.py
│   ├── test_detector.py
│   └── test_summarizer.py
│
├── docs/
│   ├── COMMIT_PLAN.md
│   ├── ASSUMPTIONS.md
│   ├── LIMITATIONS.md
│   └── DEMO_GUIDE.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Input Data

The analyzer uses a CSV session log.

The current dataset contains 20 steps and the following fields:

```text
session_id
step_id
timestamp
action
screen
target
duration_seconds
outcome
error_message
navigation_type
```

Example:

```csv
session_id,step_id,timestamp,action,screen,target,duration_seconds,outcome,error_message,navigation_type
S001,4,2026-09-15 10:00:14,click,Login Page,Login Button,2,failed,Invalid password,direct
```

---

## Detection Logic

### Failed Attempt

A failed attempt is detected when:

```text
outcome == "failed"
```

The detector records the step and the relevant error information.

### Repeated Action

A repeated action is detected when the same action and target are performed immediately after a failed attempt in the same interaction context.

### Long Pause

A step with a duration of 15 seconds or more is treated as a possible long pause.

### Backtracking

Backtracking is identified from repeated movement between the same screens in opposite directions.

---

## Severity Calculation

The scoring system assigns weights to each friction type:

```text
Failed Attempt  = 3
Repeated Action = 2
Long Pause      = 2
Backtracking    = 1
```

For example, Step 5 contains:

```text
Failed Attempt  = 3
Repeated Action = 2
--------------------
Total Score     = 5
```

Therefore:

```text
Total Score = 5
Severity    = High
```

The score is intended to prioritize areas for UX investigation. It should not be interpreted as an absolute measurement of user frustration.

---

## Installation

### Prerequisites

The following are required:

* Python 3.10 or later
* Git

Ollama is optional if the fallback summary is being used.

---

### Clone the Repository

```bash
git clone https://github.com/PrameelaAcharya/user-flow-friction-analyzer.git
cd user-flow-friction-analyzer
```

---

### Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

From the project root:

```bash
streamlit run app/streamlit_app.py
```

The Streamlit dashboard will open in the browser.

---

## Running Tests

From the project root:

```bash
pytest -q
```

The test suite covers the core analysis functionality, including:

* Session-log loading
* Friction detection
* Scoring behavior
* Top-friction selection
* Edge cases in the summarization logic

Current test result:

```text
18 passed
```

---

## Running Ollama

Check the installed models:

```bash
ollama list
```

If the configured model is not available:

```bash
ollama pull llama3
```

Start Ollama if required:

```bash
ollama serve
```

Then start the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

The application will attempt to generate the flow experience summary using the local model.

If Ollama is unavailable, the application uses the fallback evidence-based summary.

---

## End-to-End Pipeline

The complete application flow is:

```text
                session_log.csv
                       |
                       v
                +-------------+
                | Data Loader |
                +-------------+
                       |
                       v
              +------------------+
              | Friction Detector|
              +------------------+
                       |
                       v
              +------------------+
              | Severity Scoring |
              +------------------+
                       |
                       v
              +------------------+
              | Top Friction     |
              | Selection        |
              +------------------+
                       |
                       v
              +------------------+
              | Local AI Summary |
              +------------------+
                       |
                       v
              +------------------+
              | Streamlit        |
              | Dashboard        |
              +------------------+
```

---

## Testing

The project includes automated tests for the core components.

The tests verify:

* Valid session-log loading
* Expected sample-data size
* Failed-attempt detection
* Repeated-action detection
* Long-pause detection
* Backtracking detection
* Severity scoring
* Score ordering
* Empty input handling
* Top-friction selection
* Score ties
* Unsorted input handling

Current test suite:

```text
18 passed
```

---

## Assumptions

The prototype makes the following assumptions:

* The input represents one bounded user session.
* The session log contains reliable timestamps and durations.
* A failed outcome represents an unsuccessful interaction.
* Repeated actions can be useful indicators of friction.
* A pause of 15 seconds or more is worth investigating.
* Repeated movement between screens may indicate navigation difficulty.
* Severity scores are prioritization signals.
* The AI summary should use only the detected friction evidence.
* Synthetic data is sufficient for demonstrating the prototype.

Detailed assumptions are documented in:

```text
docs/ASSUMPTIONS.md
```

---

## Limitations

### Synthetic Data

The current demonstration uses synthetic session data rather than production user sessions.

### Rule-Based Detection

The detector depends on predefined rules and thresholds. More complex real-world behavior may not be captured.

### Long Pauses

A long pause does not necessarily mean confusion. The user may have been interrupted or temporarily inactive.

### Backtracking

Returning to a previous screen can be intentional. Therefore, backtracking is treated as a possible friction signal rather than definitive evidence of a usability problem.

### Severity

Severity is a prioritization mechanism based on detected signals. It is not a direct measurement of user frustration, emotion, or satisfaction.

### AI Summary

The AI summarizes the evidence provided to it. It cannot identify friction that was missed by the rule-based detector.

### Scale

The current prototype is designed for a bounded session log and is not optimized for large-scale production analytics.

---

## Why Rule-Based Detection + AI?

The project intentionally avoids using AI for every stage of the pipeline.

Instead of:

```text
AI → Detect
AI → Score
AI → Explain
AI → Recommend
```

the project uses:

```text
Rules → Detect
Rules → Score
Rules → Prioritize
AI    → Summarize
```

This approach keeps the core analysis:

* Explainable
* Deterministic
* Easy to test
* Easy to reproduce

while still using AI for a meaningful task: generating a concise UX flow summary.

---

## Demo Flow

A typical demonstration follows these steps:

```text
1. Start the Streamlit application
2. Show the session overview
3. Explain the 20-step shopping flow
4. Show the failed login attempt
5. Show the repeated login action
6. Show the long pause during search
7. Show the backtracking behavior
8. Explain severity scoring
9. Show the dashboard visualizations
10. Show the detected friction list
11. Show the AI-generated flow summary
12. Show automated test results
13. Explain assumptions and limitations
```

---

## Future Improvements

Possible future improvements include:

* Support for multiple sessions
* Custom CSV upload through the dashboard
* Configurable friction thresholds
* More advanced navigation-pattern detection
* Comparison between multiple sessions
* UX trend analysis
* Exportable analysis reports
* Additional visualization options

These improvements are outside the scope of the current prototype.

---

## Project Outcome

The prototype demonstrates an end-to-end approach for converting raw session interaction data into structured UX insights.

The final workflow is:

```text
Raw Session Log
       |
       v
Friction Detection
       |
       v
Severity Scoring
       |
       v
Prioritized Friction Points
       |
       v
Likely User Impact
       |
       v
AI-Assisted Flow Summary
       |
       v
Interactive Dashboard
```

The project focuses on keeping the analysis simple, explainable, testable, and suitable for a bounded UX diagnosis task.

````

## Now save and commit

From the project root:

```bash
git status
````

Then:

```bash
git add README.md
git commit -m "docs: finalize project README"
git push origin main
```

Then verify:

```bash
git log --oneline -10
```