import matplotlib.pyplot as plt


def plot_score_comparison(results):
    """
    Compare final scores of all candidates.
    """
    names = [r["candidate"] for r in results]
    scores = [r["final_score"] for r in results]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, scores)
    ax.set_title("Candidate Final Scores")
    ax.set_xlabel("Candidates")
    ax.set_ylabel("Final Score")
    plt.xticks(rotation=20)

    return fig


def plot_score_breakdown(result):
    """
    Show TF-IDF, Skills and Experience scores.
    """
    labels = ["TF-IDF", "Skills", "Experience"]
    values = [
        result["tfidf_score"],
        result["skills_score"],
        result["experience_score"]
    ]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(labels, values)
    ax.set_ylim(0, 100)
    ax.set_title("Score Breakdown")

    return fig


def plot_skill_coverage(result):
    """
    Pie chart of matched vs missing skills.
    """
    matched = len(result.get("matched_skills", []))
    missing = len(result.get("missing_skills", []))

    fig, ax = plt.subplots(figsize=(5, 4))

    if matched == 0 and missing == 0:
        ax.text(
            0.5,
            0.5,
            "No skills detected",
            ha="center",
            va="center"
        )
        ax.axis("off")
    else:
        ax.pie(
            [matched, missing],
            labels=["Matched", "Missing"],
            autopct="%1.1f%%",
        )
        ax.set_title("Skill Coverage")

    return fig