import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


def select_top_friction(points, limit=3):
    """Select top friction points while preserving score ties."""

    if not points or limit <= 0:
        return []

    sorted_points = sorted(
        points,
        key=lambda point: (-point.score, point.step_id),
    )

    if len(sorted_points) <= limit:
        return sorted_points

    cutoff_score = sorted_points[limit - 1].score

    return [
        point
        for point in sorted_points
        if point.score >= cutoff_score
    ]


def fallback_summary(points) -> str:
    """Create an evidence-based UX summary without AI."""

    if not points:
        return (
            "The session completed successfully without "
            "detected friction signals."
        )

    top_points = select_top_friction(points)

    observations = []

    for point in top_points:
        friction = ", ".join(
            point.friction_types
        ).lower()

        reason = " ".join(point.reasons)

        observations.append(
            f"step {point.step_id} shows {friction}: {reason}"
        )

    observation_text = "; ".join(observations)

    return (
        "The session was mostly successful, but the analysis "
        f"identified several areas of friction: "
        f"{observation_text}. "
        "These issues may cause users to experience "
        "difficulty, hesitation, or interruption while "
        "completing the task. "
        "Overall, the flow appears functional but could "
        "benefit from clearer error recovery and a smoother "
        "interaction experience."
    )


def summarize_with_ollama(points) -> str:
    """Summarize the highest-priority friction points using local Ollama."""

    if not points:
        return fallback_summary(points)

    # Send the top 3 priority positions to the AI,
    # including all records tied with the 3rd position.
    top_points = select_top_friction(points)

    friction_data = []

    for point in top_points:
        friction_data.append(
            {
                "step": point.step_id,
                "friction_types": point.friction_types,
                "score": point.score,
                "severity": point.severity,
                "impact": point.impact,
                "reasons": point.reasons,
            }
        )

    prompt = f"""
You are a UX analyst reviewing a user-flow session.

Write ONE concise paragraph describing the overall flow experience.

Use ONLY the detected friction evidence provided below.

Your summary must:
- Mention the most important friction points first.
- Reference relevant step numbers.
- Explain what the evidence suggests about the user experience.
- Describe likely task impact such as interruption, hesitation, difficulty,
  repeated actions, or blocked progress.
- Mention successful progress through the flow when relevant.
- Treat severity as a prioritization signal, not as proof of user emotion.
- Do NOT assume the user's emotions, intentions, urgency, frustration,
  disappointment, or motivation unless directly supported by the data.
- Do NOT invent problems, metrics, or behaviors.
- Do NOT repeat every score.
- Do NOT simply list the friction points.
- Keep the language professional and suitable for a UX diagnosis report.
- Keep the response to 3-5 sentences.

Detected friction evidence:
{friction_data}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        summary = result.get("response", "").strip()

        if summary:
            return summary

        return (
            "Ollama returned an empty response. "
            "Showing the fallback summary instead.\n\n"
            + fallback_summary(points)
        )

    except requests.RequestException as error:
        return (
            f"Ollama summary unavailable: {error}. "
            "Showing the fallback summary instead.\n\n"
            + fallback_summary(points)
        )