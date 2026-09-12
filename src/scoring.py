SEVERITY_SCORE = {"High": 3, "Medium": 2, "Low": 1}

def rank_friction(points):
    return sorted(points, key=lambda p: (SEVERITY_SCORE.get(p.severity, 0), p.step_id), reverse=True)
