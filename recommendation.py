def generate_recommendation(result):
    score = result["final_score"]

    if score >= 80:
        return {
            "verdict": "Strong Match",
            "action": "Proceed to Interview",
            "strengths": [
                "Excellent overall match",
                "Relevant skills"
            ],
            "gaps": [],
            "next_steps": [
                "Schedule technical interview"
            ]
        }

    elif score >= 60:
        return {
            "verdict": "Good Match",
            "action": "Shortlist",
            "strengths": [
                "Reasonable skill match"
            ],
            "gaps": result.get("missing_skills", []),
            "next_steps": [
                "Conduct technical assessment"
            ]
        }

    else:
        return {
            "verdict": "Low Match",
            "action": "Reject",
            "strengths": [],
            "gaps": result.get("missing_skills", []),
            "next_steps": [
                "Not recommended for this role"
            ]
        }