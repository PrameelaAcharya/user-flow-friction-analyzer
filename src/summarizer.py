import requests

def fallback_summary(points):
    if not points:
        return "The session shows no detected friction under the configured rules."
    high = sum(p.severity == "High" for p in points)
    medium = sum(p.severity == "Medium" for p in points)
    low = sum(p.severity == "Low" for p in points)
    types = list(dict.fromkeys(p.friction_type for p in points))
    return (f"The flow shows {len(points)} detected friction points, including {high} high, {medium} medium, and {low} low impact events. "
            f"The main patterns are {', '.join(types)}. Failed and repeated interactions are the strongest signals of user difficulty, "
            "while long pauses and backtracking suggest hesitation or navigation uncertainty.")

def summarize_with_ollama(points, model="llama3"):
    if not points:
        return fallback_summary(points)
    events = [f"Step {p.step_id}: {p.friction_type} ({p.severity}) - {p.reason}" for p in points[:8]]
    prompt = "Write one concise paragraph summarizing only these detected usability friction points and their likely user impact. Do not invent events:\n" + "\n".join(events)
    try:
        r = requests.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False}, timeout=10)
        r.raise_for_status()
        text = r.json().get("response", "").strip()
        return text or fallback_summary(points)
    except (requests.RequestException, ValueError, KeyError):
        return fallback_summary(points)
