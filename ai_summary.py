"""
ai_summary.py
AI Candidate Summary Generator
"""

from recommendation import generate_recommendation


def generate_summary(candidate_name, result):
    """
    Generate summary from result dictionary.
    """

    recommendation = generate_recommendation(result)

    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])

    summary = f"""
Candidate Name: {candidate_name}

Final Score: {result.get('final_score',0)}

TF-IDF Score: {result.get('tfidf_score',0)}

Skill Match: {result.get('skills_score',0)}%

Experience Score: {result.get('experience_score',0)}

Matched Skills:
{', '.join(matched) if matched else 'None'}

Missing Skills:
{', '.join(missing) if missing else 'None'}

Recommendation:
{recommendation['verdict']}

Action:
{recommendation['action']}
"""

    return summary.strip()