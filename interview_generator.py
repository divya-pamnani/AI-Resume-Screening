"""
interview_generator.py
----------------------
Generate interview questions based on resume analysis.
"""

def generate_interview_questions(result):
    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])

    technical_questions = [
        f"Explain your experience with {skill}."
        for skill in matched[:5]
    ]

    skill_gap_questions = [
        f"How would you learn or improve your knowledge of {skill}?"
        for skill in missing[:5]
    ]

    experience_questions = [
        "Describe your most challenging project.",
        "What was your role in your last project?",
        "How did you solve a difficult technical problem?"
    ]

    behavioral_questions = [
        "Tell me about yourself.",
        "How do you handle tight deadlines?",
        "Describe a time you worked in a team.",
        "Why should we hire you?"
    ]

    return {
        "technical_questions": technical_questions,
        "skill_gap_questions": skill_gap_questions,
        "experience_questions": experience_questions,
        "behavioral_questions": behavioral_questions
    }