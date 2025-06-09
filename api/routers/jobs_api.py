import os
import requests
from fastapi import APIRouter, HTTPException, Body, Request, Query
from typing import Optional, List
from functools import lru_cache
import json
from pathlib import Path

router = APIRouter()

# --- Environment Setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")


# --- Helper function to load suggestions from fallback JSON ---
@lru_cache(maxsize=1)
def _load_fallback_jobs():
    # Correctly locate the fallback_jobs.json file relative to this script
    json_path = Path(__file__).parent.parent.parent / "jobs" / "fallback_jobs.json"
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return []


def get_suggestions(category: str, query: str) -> List[str]:
    """Provides suggestions for roles, skills, or cities based on a query."""
    if not query or len(query) < 2:
        return []

    jobs = _load_fallback_jobs()
    suggestions = set()
    query = query.lower()

    if category in ["roles", "skills"]:
        for job in jobs:
            title = job.get("job_title", "").lower()
            if query in title:
                suggestions.add(job.get("job_title"))  # Add the original title for proper capitalization
    elif category == "cities":
        for job in jobs:
            city = job.get("job_city", "").lower()
            if city and query in city:
                suggestions.add(job.get("job_city"))

    return sorted(list(suggestions))[:10]  # Return top 10 matches


# -------- NEW: Endpoints for Onboarding Suggestions -------- #
@router.get("/suggest/{category}")
def suggest_options(category: str, q: str = Query(..., min_length=2)):
    """Provides suggestions for 'roles', 'skills', or 'cities'."""
    if category not in ["roles", "skills", "cities"]:
        raise HTTPException(status_code=404, detail="Category not found")

    options = get_suggestions(category, q)
    return {"options": options}


# -------- GPT Keyword Extraction (with LRU cache for speed) -------- #
@lru_cache(maxsize=512)
def extract_keywords_gpt_cached(resume: str) -> str:
    # This function remains unchanged...
    import openai
    openai.api_key = OPENAI_API_KEY
    prompt = (
        "Given the following resume text, extract the single most relevant job title "
        "or, if not possible, the top 3 most relevant keywords or skills "
        "(comma-separated, no explanation):\n\n"
        f"Resume:\n{resume}\n\nJob Title or Top 3 Keywords:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume parser."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=32,
            temperature=0.2,
        )
        result = response["choices"][0]["message"]["content"].strip()
        if "," in result:
            return ",".join([kw.strip() for kw in result.split(",")[:3]])
        return result.split("\n")[0][:48]
    except Exception as e:
        print(f"❌ GPT fallback: {e}")
        return "Software Engineer"


# -------- JSearch Query -------- #
def query_jsearch(keyword: str, city: Optional[str] = None, limit: int = 12) -> List[dict]:
    # This function remains unchanged...
    url = f"https://{JSEARCH_API_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_API_HOST,
    }
    params = {
        "query": keyword,
        "num_pages": 1,
        "page": 1,
        "country": "us",
        "remote_jobs_only": False,
        "limit": limit,
    }
    if city:
        params["location"] = city
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSearch network error: {str(e)}")
    if resp.status_code in [401, 403]:
        raise HTTPException(status_code=500, detail="JSearch API key/host error")
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"JSearch API error: {resp.text}")
    return resp.json().get("data", [])


# -------- Personalized Scoring -------- #
def compute_match_score(job: dict, filters: dict) -> int:
    # This function remains unchanged...
    score = 60
    title = (job.get("job_title") or "").lower()
    city = (job.get("job_city") or job.get("job_country") or "").lower()
    role = filters.get("role", "").lower()
    pref_city = filters.get("city", "").lower()
    emp_type = filters.get("employment_type", "").lower()
    # +30 if job title matches user preferred role
    if role and role in title:
        score += 30
    # +20 if city matches
    if pref_city and pref_city in city:
        score += 20
    # +20 if user prefers remote and job is remote
    if emp_type == "remote" and (job.get("remote", False) or "remote" in city):
        score += 20
    return min(score, 100)


# -------- Data Cleanup for UI -------- #
def clean_job_data(job: dict, filters: dict) -> dict:
    # This function remains unchanged...
    score = compute_match_score(job, filters)
    return {
        "id": job.get("job_id") or job.get("jobkey") or "",
        "title": job.get("job_title", ""),
        "company": job.get("employer_name", ""),
        "location": job.get("job_city", "") or job.get("job_country", ""),
        "salary": job.get("job_min_salary") or "N/A",
        "description": (job.get("job_description") or "")[:300],
        "link": job.get("job_apply_link", ""),
        "posted": job.get("job_posted_at_datetime_utc", ""),
        "type": job.get("job_employment_type") or "Unknown",
        "logo": job.get("employer_logo") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
        "numeric_score": score,
    }


# -------- Main Endpoint (FIXED) -------- #
@router.post("/jobs")  # Removed /api prefix here as it's handled by main.py
def get_jobs(data: dict = Body(...), request: Request = None):
    # This endpoint signature and logic remains mostly the same...
    try:
        resume = data.get("resume", "").strip()
        preferred_roles = data.get("preferredRoles", [])
        preferred_cities = data.get("preferredCities", [])
        employment_types = data.get("employmentTypes", [])

        role = preferred_roles[0] if preferred_roles else ""
        city = preferred_cities[0] if preferred_cities else None
        keyword = role or (extract_keywords_gpt_cached(resume) if resume else "Software Engineer")

        jobs_raw = query_jsearch(keyword, city=city)
        jobs_cleaned = [
            clean_job_data(job, {
                "role": role,
                "city": city,
                "employment_type": employment_types[0] if employment_types else ""
            })
            for job in jobs_raw
        ]

        jobs_cleaned.sort(key=lambda j: j["numeric_score"], reverse=True)
        # FIX: Return data in the format the frontend expects
        return {"jobs": jobs_cleaned}
    except Exception as e:
        print(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")