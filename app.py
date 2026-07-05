"""
app.py
------
Streamlit web UI for the AI Resume Screening tool.

Run with:
    streamlit run app.py

Then open the local URL it prints (usually http://localhost:8501).
"""

import os
import tempfile

import pandas as pd
import streamlit as st

from resume_parser import extract_text, extract_email, extract_phone, extract_name
from matcher import rank_resumes
from ats_score import compute_ats_score
from recommendation import generate_recommendation
from ai_summary import generate_summary
from interview_generator import generate_interview_questions
from charts import plot_score_comparison, plot_score_breakdown, plot_skill_coverage
from pdf_report import generate_summary_report_pdf, generate_candidate_report_pdf
from excel_export import export_results_to_excel


st.set_page_config(page_title="AI Resume Screening", layout="wide")

st.title("📄 AI Resume Screening")
st.caption(
    "Paste a job description, upload candidate resumes, and get a ranked, "
    "explainable match score for each candidate — plus ATS scoring, hiring "
    "recommendations, interview questions, and downloadable reports."
)

# ---------------------------------------------------------------------------
# Sidebar: scoring weight controls
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Scoring Weights")
w_tfidf = st.sidebar.slider("Overall relevance (TF-IDF)", 0.0, 1.0, 0.50, 0.05)
w_skills = st.sidebar.slider("Skill match", 0.0, 1.0, 0.35, 0.05)
w_experience = st.sidebar.slider("Experience match", 0.0, 1.0, 0.15, 0.05)

total_weight = w_tfidf + w_skills + w_experience
if total_weight == 0:
    st.sidebar.error("Weights cannot all be zero.")
    weights = {"tfidf": 0.5, "skills": 0.35, "experience": 0.15}
else:
    weights = {
        "tfidf": w_tfidf / total_weight,
        "skills": w_skills / total_weight,
        "experience": w_experience / total_weight,
    }
    st.sidebar.caption(
        f"Normalized: TF-IDF {weights['tfidf']:.2f} | "
        f"Skills {weights['skills']:.2f} | "
        f"Experience {weights['experience']:.2f}"
    )

st.sidebar.divider()
job_title = st.sidebar.text_input("Job title (for report headers)", value="Job Opening")

# ---------------------------------------------------------------------------
# Main inputs
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    jd_input_method = st.radio(
        "Provide the JD via:", ["Paste text", "Upload file"], horizontal=True
    )
    jd_text = ""
    if jd_input_method == "Paste text":
        jd_text = st.text_area("Paste job description here", height=300)
    else:
        jd_file = st.file_uploader(
            "Upload JD file", type=["pdf", "docx", "txt"], key="jd_upload"
        )
        if jd_file is not None:
           temp_path = os.path.join(tempfile.gettempdir(), jd_file.name)
           with open(temp_path, "wb") as f:
               f.write(jd_file.getbuffer())
               jd_text = extract_text(temp_path)
               st.text_area("Extracted JD text (preview)", jd_text, height=250)

with col2:
    st.subheader("2. Candidate Resumes")
    resume_files = st.file_uploader(
        "Upload one or more resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="resume_upload",
    )
    if resume_files:
        st.write(f"{len(resume_files)} resume(s) uploaded.")

# ---------------------------------------------------------------------------
# Run screening
# ---------------------------------------------------------------------------
run_button = st.button(
    "🔍 Screen Resumes",
    type="primary",
    width="stretch"
)

if run_button:
    if not jd_text.strip():
        st.error("Please provide a job description first.")
    elif not resume_files:
        st.error("Please upload at least one resume.")
    else:
        resumes_dict = {}
        resume_raw_text = {}
        with st.spinner("Extracting text and scoring candidates..."):
            for rf in resume_files:
               temp_path = os.path.join(tempfile.gettempdir(), rf.name)
               with open(temp_path, "wb") as f:
                   f.write(rf.getbuffer())
                   try:
                       text = extract_text(temp_path)
                       resumes_dict[rf.name] = text
                       resume_raw_text[rf.name] = text
                   except Exception as e:
                       st.warning(f"Could not read {rf.name}: {e}")

            results = rank_resumes(jd_text, resumes_dict, weights)

            # Precompute ATS scores and recommendations once, reused everywhere below
            ats_by_candidate = {
    r["candidate"]: compute_ats_score(
        resume_raw_text[r["candidate"]],
        jd_text
    )
    for r in results
}
        
            rec_by_candidate = {r["candidate"]: generate_recommendation(r) for r in results}

        st.success(f"Screened {len(results)} candidate(s).")

        # Store in session_state so downloads / reruns don't lose results
        st.session_state["results"] = results
        st.session_state["resume_raw_text"] = resume_raw_text
        st.session_state["ats_by_candidate"] = ats_by_candidate
        st.session_state["rec_by_candidate"] = rec_by_candidate
        st.session_state["job_title"] = job_title

# ---------------------------------------------------------------------------
# Display results (persisted in session_state so button clicks don't reset it)
# ---------------------------------------------------------------------------
if "results" in st.session_state:
    results = st.session_state["results"]
    resume_raw_text = st.session_state["resume_raw_text"]
    ats_by_candidate = st.session_state["ats_by_candidate"]
    rec_by_candidate = st.session_state["rec_by_candidate"]
    job_title = st.session_state["job_title"]

    # Build display table
    rows = []
    for r in results:
        text = resume_raw_text[r["candidate"]]
        ats = ats_by_candidate[r["candidate"]]
        rec = rec_by_candidate[r["candidate"]]
        rows.append({
            "Rank": r["rank"],
            "File": r["candidate"],
            "Name (guess)": extract_name(text),
            "Email": extract_email(text),
            "Phone": extract_phone(text),
            "Final Score": r["final_score"],
            "ATS Score": ats["ats_score"],
            "Verdict": rec["verdict"],
            "Relevance": r["tfidf_score"],
            "Skill Match %": r["skills_score"],
            "Experience Score": r["experience_score"],
            "Years (candidate/required)":
                f"{r['candidate_years']} / {r['required_years']}",
            "Matched Skills": ", ".join(r["matched_skills"]) or "—",
            "Missing Skills": ", ".join(r["missing_skills"]) or "—",
        })

    df = pd.DataFrame(rows)

    st.subheader("📊 Ranked Results")
    st.dataframe(
    df.style.background_gradient(subset=["Final Score"], cmap="Greens"),
    width="stretch",
    hide_index=True,
)

    st.subheader("📈 Score Comparison")
    st.pyplot(plot_score_comparison(results))

    # Per-candidate detail expanders
    st.subheader("🔎 Candidate Details")
    for r in results:
        text = resume_raw_text[r["candidate"]]
        ats = ats_by_candidate[r["candidate"]]
        rec = rec_by_candidate[r["candidate"]]

        with st.expander(
            f"#{r['rank']} — {r['candidate']}  "
            f"(Score: {r['final_score']} | Verdict: {rec['verdict']})"
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Relevance (TF-IDF)", r["tfidf_score"])
            c2.metric("Skill Match %", r["skills_score"])
            c3.metric("Experience Score", r["experience_score"])
            c4.metric("ATS Score", ats["ats_score"], ats["rating"])

            tab_overview, tab_ats, tab_summary, tab_questions, tab_charts = st.tabs(
                ["Overview", "ATS Details", "AI Summary", "Interview Questions", "Charts"]
            )

            with tab_overview:
                st.markdown(f"**Verdict:** {rec['verdict']} — {rec['action']}")
                st.markdown("**Strengths:**")
                for s in rec["strengths"]:
                    st.markdown(f"- {s}")
                st.markdown("**Gaps:**")
                for g in rec["gaps"]:
                    st.markdown(f"- {g}")
                st.markdown("**Suggested next steps:**")
                for step in rec["next_steps"]:
                    st.markdown(f"- {step}")

            with tab_ats:
                st.markdown(f"**ATS Compatibility Score:** {ats['ats_score']}/100 ({ats['rating']})")
                for check in ats["checks"]:
                    icon = "✅" if check["passed"] else "⚠️"
                    st.markdown(
                        f"{icon} **{check['check']}** — {check['points']}/{check['max_points']} "
                        f"— {check['note']}"
                    )

            with tab_summary:
                summary_text = generate_summary(r["candidate"], r)
                st.write(summary_text)

            with tab_questions:
                questions = generate_interview_questions(r)
                for category, label in [
                    ("technical_questions", "🧠 Technical"),
                    ("skill_gap_questions", "❓ Skill Gap Probes"),
                    ("experience_questions", "📅 Experience"),
                    ("behavioral_questions", "🤝 Behavioral"),
                ]:
                    qs = questions.get(category, [])
                    if not qs:
                        continue
                    st.markdown(f"**{label}**")
                    for q in qs:
                        st.markdown(f"- {q}")

            with tab_charts:
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.pyplot(plot_score_breakdown({**r, "candidate": r["candidate"]}))
                with cc2:
                    st.pyplot(plot_skill_coverage(r))

            # Per-candidate PDF report
            with tempfile.TemporaryDirectory() as tmp_dir:
                candidate_pdf_path = os.path.join(tmp_dir, "candidate_report.pdf")
                generate_candidate_report_pdf(
                    r["candidate"], r["candidate"], r, candidate_pdf_path,
                    resume_text=text
                )
                with open(candidate_pdf_path, "rb") as f:
                    st.download_button(
                        f"⬇️ Download PDF report for {r['candidate']}",
                        data=f.read(),
                        file_name=f"report_{r['candidate']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{r['candidate']}",
                    )

    # -----------------------------------------------------------------------
    # Bulk downloads
    # -----------------------------------------------------------------------
    st.subheader("⬇️ Download Reports")
    d1, d2, d3 = st.columns(3)

    with d1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "CSV (raw data)",
            data=csv_data,
            file_name="resume_screening_results.csv",
            mime="text/csv",
            width="stretch"
        )

    with d2:
        with tempfile.TemporaryDirectory() as tmp_dir:
            xlsx_path = os.path.join(tmp_dir, "results.xlsx")
            extra_fields = {
                r["candidate"]: {
                    "name": extract_name(resume_raw_text[r["candidate"]]),
                    "email": extract_email(resume_raw_text[r["candidate"]]),
                }
                for r in results
            }
            export_results_to_excel(results, job_title, xlsx_path, extra_fields)
            with open(xlsx_path, "rb") as f:
                st.download_button(
                    "Excel (formatted)",
                    data=f.read(),
                    file_name="resume_screening_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    with d3:
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary_pdf_path = os.path.join(tmp_dir, "summary_report.pdf")
            generate_summary_report_pdf(results, job_title, summary_pdf_path)
            with open(summary_pdf_path, "rb") as f:
                st.download_button(
                    "PDF (ranking summary)",
                    data=f.read(),
                    file_name="resume_screening_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )