import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


def fallback_summary(points) -> str:
    """Create a simple summary without using AI."""

    if not points:
        return (
            "The session completed without major friction signals."
        )

    types = []

    for point in points:
        types.extend(point.friction_types)

    types = list(dict.fromkeys(types))

    high_count = sum(
        point.severity == "High"
        for point in points
    )

    medium_count = sum(
        point.severity == "Medium"
        for point in points
    )

    low_count = sum(
        point.severity == "Low"
        for point in points
    )

    friction_text = ", ".join(types)

    return (
        f"The flow shows {len(points)} friction points, "
        f"including {friction_text}. "
        f"There are {high_count} high-severity, "
        f"{medium_count} medium-severity, and "
        f"{low_count} low-severity issues. "
        "The highest-severity points suggest areas where "
        "users may experience difficulty or blocked progress."
    )


def summarize_with_ollama(points) -> str:
    """Summarize scored friction points using local Ollama."""

    if not points:
        return fallback_summary(points)

    friction_data = []

    for point in points:
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
You are a UX analyst.

Summarize the following detected friction points from a
user session.

Only use the information provided.
Do not invent additional problems, metrics, or user behavior.

Explain:
1. The most important friction points.
2. Their likely impact on the user experience.
3. The overall flow experience.

Keep the response to one concise paragraph.

Detected friction points:
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

    except requests.RequestException:
        pass

    return fallback_summary(points)