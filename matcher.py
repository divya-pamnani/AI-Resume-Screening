from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes(jd_text, resumes_dict, weights):
    docs = [jd_text] + list(resumes_dict.values())

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs)

    jd_vec = tfidf[0]
    resume_vecs = tfidf[1:]

    results = []

    for i, (candidate, resume_text) in enumerate(resumes_dict.items()):
        similarity = cosine_similarity(jd_vec, resume_vecs[i])[0][0]

        tfidf_score = round(similarity * 100, 2)
        skills_score = tfidf_score
        experience_score = 70

        final_score = round(
            (
                similarity * weights["tfidf"]
                + (skills_score / 100) * weights["skills"]
                + (experience_score / 100) * weights["experience"]
            ) * 100,
            2,
        )

        results.append({
            "candidate": candidate,
            "tfidf_score": tfidf_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "final_score": final_score,
            "candidate_years": 2,
            "required_years": 2,
            "matched_skills": [],
            "missing_skills": [],
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)

    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    return results