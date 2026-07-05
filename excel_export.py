import pandas as pd

def export_results_to_excel(results, job_title, output_path, extra_fields=None):
    rows = []

    for r in results:
        extra = extra_fields.get(r["candidate"], {}) if extra_fields else {}

        rows.append({
            "Rank": r["rank"],
            "Candidate": r["candidate"],
            "Name": extra.get("name", ""),
            "Email": extra.get("email", ""),
            "Final Score": r["final_score"],
            "TF-IDF Score": r["tfidf_score"],
            "Skill Match": r["skills_score"],
            "Experience Score": r["experience_score"],
            "Matched Skills": ", ".join(r["matched_skills"]),
            "Missing Skills": ", ".join(r["missing_skills"]),
        })

    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)