"""
ats_score.py
"""

import re


def compute_ats_score(resume_text, jd_text="", matched_skills=None, missing_skills=None):

    matched_skills = matched_skills or []
    missing_skills = missing_skills or []

    score = 0
    checks = []

    # -----------------------
    # Resume Length
    # -----------------------

    words = len(resume_text.split())

    if words >= 300:
        score += 20
        checks.append({
            "check": "Resume Length",
            "passed": True,
            "points": 20,
            "max_points": 20,
            "note": "Good resume length"
        })
    else:
        score += 10
        checks.append({
            "check": "Resume Length",
            "passed": False,
            "points": 10,
            "max_points": 20,
            "note": "Resume is short"
        })

    # -----------------------
    # Email
    # -----------------------

    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text):
        score += 10
        checks.append({
            "check": "Email",
            "passed": True,
            "points": 10,
            "max_points": 10,
            "note": "Email found"
        })
    else:
        checks.append({
            "check": "Email",
            "passed": False,
            "points": 0,
            "max_points": 10,
            "note": "Email missing"
        })

    # -----------------------
    # Phone
    # -----------------------

    if re.search(r"(?:\+91[- ]?)?[6-9]\d{9}", resume_text):
        score += 10
        checks.append({
            "check": "Phone",
            "passed": True,
            "points": 10,
            "max_points": 10,
            "note": "Phone number found"
        })
    else:
        checks.append({
            "check": "Phone",
            "passed": False,
            "points": 0,
            "max_points": 10,
            "note": "Phone number missing"
        })

    # -----------------------
    # Skills
    # -----------------------

    total = len(matched_skills) + len(missing_skills)

    if total > 0:
        skill_score = int((len(matched_skills) / total) * 40)
    else:
        skill_score = 20

    score += skill_score

    checks.append({
        "check": "Skills",
        "passed": skill_score >= 20,
        "points": skill_score,
        "max_points": 40,
        "note": "Skill match calculated"
    })

    # -----------------------
    # JD Match
    # -----------------------

    jd_score = 20 if jd_text else 10

    score += jd_score

    checks.append({
        "check": "Job Description Match",
        "passed": True,
        "points": jd_score,
        "max_points": 20,
        "note": "Basic JD comparison"
    })

    score = min(score, 100)

    if score >= 90:
        rating = "Excellent"
    elif score >= 75:
        rating = "Very Good"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Average"
    else:
        rating = "Poor"

    return {
        "ats_score": round(score, 2),
        "rating": rating,
        "checks": checks
    }