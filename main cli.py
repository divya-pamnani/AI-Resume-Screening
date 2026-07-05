"""
main_cli.py
-----------
Command-line resume screener.

Basic usage:
    python main_cli.py --jd job_description.txt --resumes ./resumes_folder --out results.csv

With PDF and Excel reports too:
    python main_cli.py --jd job_description.txt --resumes ./resumes_folder \
        --out results.csv --pdf summary_report.pdf --excel results.xlsx \
        --candidate-pdfs ./candidate_reports

Place all candidate resumes (.pdf, .docx, or .txt) inside the resumes folder.
The job description can be a .txt, .pdf, or .docx file.
"""

import argparse
import os
import sys

import pandas as pd

from resume_parser import extract_text, extract_email, extract_phone, extract_name
from matcher import rank_resumes
from ats_score import compute_ats_score
from recommendation import generate_recommendation
from pdf_report import generate_summary_report_pdf, generate_candidate_report_pdf
from excel_export import export_results_to_excel


SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt")


def load_resumes_from_folder(folder_path: str) -> dict:
    """Read every supported resume file in a folder. Returns {filename: text}."""
    resumes = {}
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):
            full_path = os.path.join(folder_path, filename)
            try:
                resumes[filename] = extract_text(full_path)
            except Exception as e:
                print(f"⚠️  Skipping '{filename}': {e}", file=sys.stderr)
    return resumes


def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening Tool (CLI)")
    parser.add_argument("--jd", required=True,
                         help="Path to job description file (.txt/.pdf/.docx)")
    parser.add_argument("--resumes", required=True,
                         help="Path to folder containing resume files")
    parser.add_argument("--job-title", default="Job Opening",
                         help="Job title, used as a header in generated reports")
    parser.add_argument("--out", default="results.csv",
                         help="Output CSV file path (default: results.csv)")
    parser.add_argument("--top", type=int, default=None,
                         help="Only show/save top N candidates")
    parser.add_argument("--pdf", default=None,
                         help="If set, also write a ranking-summary PDF to this path")
    parser.add_argument("--excel", default=None,
                         help="If set, also write a formatted .xlsx workbook to this path")
    parser.add_argument("--candidate-pdfs", default=None,
                         help="If set, write one detailed PDF report per candidate into this folder")
    args = parser.parse_args()

    if not os.path.isfile(args.jd):
        sys.exit(f"Error: job description file not found: {args.jd}")
    if not os.path.isdir(args.resumes):
        sys.exit(f"Error: resumes folder not found: {args.resumes}")

    jd_text = extract_text(args.jd)
    resumes = load_resumes_from_folder(args.resumes)

    if not resumes:
        sys.exit(f"No supported resume files found in: {args.resumes}")

    print(f"Loaded job description ({len(jd_text)} chars).")
    print(f"Loaded {len(resumes)} resume(s). Scoring...\n")

    results = rank_resumes(jd_text, resumes)

    if args.top:
        results = results[: args.top]

    # Build a clean summary table (with ATS score + recommendation added)
    rows = []
    for r in results:
        resume_text = resumes[r["candidate"]]
        ats = compute_ats_score(resume_text)
        rec = generate_recommendation(r)
        rows.append({
            "Rank": r["rank"],
            "File": r["candidate"],
            "Candidate Name (guess)": extract_name(resume_text),
            "Email": extract_email(resume_text),
            "Phone": extract_phone(resume_text),
            "Final Score": r["final_score"],
            "ATS Score": ats["ats_score"],
            "ATS Rating": ats["rating"],
            "Verdict": rec["verdict"],
            "TF-IDF Similarity": r["tfidf_score"],
            "Skill Match %": r["skills_score"],
            "Experience Score": r["experience_score"],
            "Candidate Years Exp.": r["candidate_years"],
            "Required Years Exp.": r["required_years"],
            "Matched Skills": ", ".join(r["matched_skills"]),
            "Missing Skills": ", ".join(r["missing_skills"]),
        })

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)

    print(df[["Rank", "File", "Candidate Name (guess)", "Final Score",
              "ATS Score", "Verdict", "Candidate Years Exp."]].to_string(index=False))
    print(f"\n✅ Full results written to: {args.out}")

    if args.pdf:
        generate_summary_report_pdf(results, args.job_title, args.pdf)
        print(f"✅ Summary PDF written to: {args.pdf}")

    if args.excel:
        extra_fields = {
            r["candidate"]: {
                "name": extract_name(resumes[r["candidate"]]),
                "email": extract_email(resumes[r["candidate"]]),
            }
            for r in results
        }
        export_results_to_excel(results, args.job_title, args.excel, extra_fields)
        print(f"✅ Excel workbook written to: {args.excel}")

    if args.candidate_pdfs:
        os.makedirs(args.candidate_pdfs, exist_ok=True)
        for r in results:
            safe_name = os.path.splitext(r["candidate"])[0]
            out_path = os.path.join(args.candidate_pdfs, f"{safe_name}_report.pdf")
            generate_candidate_report_pdf(
                r["candidate"], r["candidate"], r, out_path,
                resume_text=resumes[r["candidate"]]
            )
        print(f"✅ Per-candidate PDF reports written to: {args.candidate_pdfs}/")


if __name__ == "__main__":
    main()