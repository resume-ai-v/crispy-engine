import os
import requests
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")

def query_jsearch(resume, limit=10, location="United States"):
    """
    Queries JSearch for jobs matching the user's resume.
    """
    url = f"https://{JSEARCH_API_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_API_HOST,
    }
    params = {
        "query": resume if resume else "Software Engineer",  # Fallback keyword
        "num_pages": 1,
        "page": 1,
        "country": "us",
        "remote_jobs_only": True,
        "limit": limit
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code in [401, 403]:
        raise Exception("JSearch API key/host error: Check your credentials or quota.")
    if resp.status_code != 200:
        raise Exception(f"JSearch API error: {resp.text}")
    data = resp.json()
    jobs = []
    for result in data.get("data", []):
        jobs.append({
            "id": result.get("job_id", ""),
            "title": result.get("job_title", ""),
            "company": result.get("employer_name", ""),
            "location": result.get("job_city", "") or result.get("job_country", ""),
            "salary": result.get("job_min_salary", "") or "N/A",
            "description": result.get("job_description", "")[:300],
            "link": result.get("job_apply_link", ""),
            "posted_at": result.get("job_posted_at_datetime_utc", ""),
        })
    return jobs

@router.post("/api/jobs")
def get_jobs(data: dict = Body(...)):
    """
    Production endpoint: returns job recommendations based on resume using JSearch (RapidAPI).
    """
    try:
        resume = data.get("resume", "").strip()
        jobs = query_jsearch(resume)
        return jobs or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")
