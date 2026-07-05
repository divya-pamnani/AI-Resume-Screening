"""
skills_data.py
--------------
A curated bank of skill keywords grouped by category. Used to detect which
skills appear in a resume / job description via simple, fast keyword matching.

You can freely add more keywords to any category, or add new categories.
Keep everything lowercase — matching is done on lowercased text.
"""

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
        "html", "css", "bash", "shell scripting"
    ],
    "data_science_ml": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "pandas", "numpy", "scikit-learn", "sklearn",
        "tensorflow", "pytorch", "keras", "opencv", "data analysis",
        "data visualization", "matplotlib", "seaborn", "statistics",
        "predictive modeling", "feature engineering", "xgboost", "llm",
        "generative ai", "transformers", "hugging face"
    ],
    "web_frameworks": [
        "django", "flask", "fastapi", "react", "react.js", "angular", "vue",
        "vue.js", "node.js", "express.js", "next.js", "spring", "spring boot",
        ".net", "asp.net", "ruby on rails"
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle",
        "sql server", "redis", "cassandra", "dynamodb", "elasticsearch",
        "firebase"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "ci/cd", "git", "github", "gitlab",
        "linux", "nginx", "microservices", "serverless"
    ],
    "soft_skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "critical thinking", "time management", "collaboration",
        "adaptability", "project management", "agile", "scrum", "mentoring",
        "stakeholder management"
    ],
    "degrees": [
        "b.tech", "btech", "bachelor of technology", "b.e", "bachelor of engineering",
        "m.tech", "mtech", "master of technology", "mba", "m.s.", "ms",
        "master of science", "b.sc", "bsc", "m.sc", "msc", "bachelor of science",
        "phd", "ph.d", "doctorate", "b.com", "bca", "mca"
    ],
}


def all_skills_flat():
    """Return a single flat list of every skill keyword (excludes degrees)."""
    flat = []
    for category, skills in SKILL_CATEGORIES.items():
        if category == "degrees":
            continue
        flat.extend(skills)
    return sorted(set(flat))