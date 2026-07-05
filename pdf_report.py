from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_summary_report_pdf(results, job_title, output_path):
    """
    Generate summary PDF of all candidates.
    """
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"<b>{job_title}</b>", styles["Title"]))
    elements.append(Paragraph("Resume Screening Summary", styles["Heading2"]))

    for r in results:
        elements.append(
            Paragraph(
                f"Rank {r['rank']} : {r['candidate']} "
                f"(Score: {r['final_score']})",
                styles["BodyText"],
            )
        )

    doc.build(elements)


def generate_candidate_report_pdf(candidate_name, display_name, result, output_path, resume_text=""):
    """
    Generate PDF report for one candidate.
    """
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(f"<b>{candidate_name}</b>", styles["Title"]))
    elements.append(
        Paragraph(f"Final Score : {result['final_score']}", styles["BodyText"])
    )
    elements.append(
        Paragraph(f"TF-IDF Score : {result['tfidf_score']}", styles["BodyText"])
    )
    elements.append(
        Paragraph(f"Skill Match : {result['skills_score']}", styles["BodyText"])
    )
    elements.append(
        Paragraph(
            f"Experience Score : {result['experience_score']}",
            styles["BodyText"],
        )
    )

    elements.append(
        Paragraph(
            f"Matched Skills : {', '.join(result['matched_skills']) or 'None'}",
            styles["BodyText"],
        )
    )

    elements.append(
        Paragraph(
            f"Missing Skills : {', '.join(result['missing_skills']) or 'None'}",
            styles["BodyText"],
        )
    )

    if resume_text:
        elements.append(Paragraph("<br/><b>Resume Preview</b>", styles["Heading2"]))
        elements.append(Paragraph(resume_text[:2000], styles["BodyText"]))

    doc.build(elements)