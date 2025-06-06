from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os

router = APIRouter()

# Optional: Use your LLM for semantic match (OpenAI, etc.)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class MatchRequest(BaseModel):
    resume: str
    jd: str

def compute_ats_score(resume: str, jd: str) -> int:
    """Basic ATS match: % of JD keywords found in resume."""
    import re
    import string

    # Lowercase & tokenize
    resume_words = set(re.findall(r'\w+', resume.lower()))
    jd_words = set(re.findall(r'\w+', jd.lower()))

    # Remove stopwords for better accuracy (optional)
    stopwords = {"the", "and", "is", "in", "to", "of", "a", "for", "on", "with"}
    jd_keywords = [w for w in jd_words if w not in stopwords and len(w) > 2]
    if not jd_keywords:
        return 0

    match_count = sum(1 for word in jd_keywords if word in resume_words)
    ats_score = int((match_count / len(jd_keywords)) * 100)
    return min(ats_score, 100)

def compute_semantic_score(resume: str, jd: str) -> int:
    """Semantic score using OpenAI or other LLM API (or use spaCy similarity)."""
    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        prompt = (
            f"Resume:\n{resume}\n\nJob Description:\n{jd}\n\n"
            "Score from 0 to 100 how well this resume fits the job description, "
            "considering skills, responsibilities, and experience. Only output the number."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8,
            temperature=0.1,
        )
        score = int("".join(filter(str.isdigit, response["choices"][0]["message"]["content"])))
        return min(score, 100)
    except Exception as e:
        print(f"Semantic score error (LLM fallback): {e}")
        # Fallback: use ATS score as a proxy
        return compute_ats_score(resume, jd)

def generate_match_explanation(ats, semantic):
    if ats >= 80 and semantic >= 80:
        return "Excellent match! Both ATS and semantic fit are strong."
    elif ats >= 60 and semantic >= 60:
        return "Good match. Resume covers most key requirements."
    elif ats >= 40 or semantic >= 40:
        return "Partial match. Consider adding more relevant skills or experience."
    else:
        return "Weak match. Resume may not meet core requirements for this job."

@router.post("/api/match")
def match_resume_to_jd(data: MatchRequest):
    try:
        resume, jd = data.resume.strip(), data.jd.strip()
        if not resume or not jd:
            raise HTTPException(status_code=422, detail="Both resume and job description are required.")

        ats_score = compute_ats_score(resume, jd)
        semantic_score = compute_semantic_score(resume, jd)
        explanation = generate_match_explanation(ats_score, semantic_score)

        return {
            "ats_score": ats_score,
            "semantic_score": semantic_score,
            "explanation": explanation
        }
    except Exception as e:
        print(f"Resume–JD match error: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute resume match.")
