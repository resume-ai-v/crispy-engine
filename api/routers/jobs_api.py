import os
import requests
from fastapi import APIRouter, HTTPException, Body, Request
from typing import Optional, List, Dict, Any

router = APIRouter()

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

def fetch_remotive_jobs(keyword: str = "Software Engineer", city: Optional[str] = None, limit: int = 10):
    params = {"search": keyword}
    try:
        resp = requests.get(REMOTIVE_API, params=params, timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
    except Exception as e:
        print("❌ Remotive API error:", e)
        return []
    jobs_cleaned = []
    for job in jobs[:limit]:
        jobs_cleaned.append({
            "id": str(job["id"]),
            "title": job["title"],
            "company": job["company_name"],
            "location": job["candidate_required_location"],
            "salary": job.get("salary", "N/A"),
            "description": (job.get("description") or "")[:300],
            "link": job.get("url", ""),
            "posted": job.get("publication_date", ""),
            "type": job["job_type"],
            "logo": job.get("company_logo_url") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
            "source": "Remotive"
        })
    return jobs_cleaned

def fetch_jsearch_jobs(keyword: str, city: Optional[str] = None, limit: int = 10):
    jobs_cleaned = []
    JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
    JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")
    if not JSEARCH_API_KEY or not JSEARCH_API_HOST:
        print("JSearch API not configured. Skipping.")
        return []
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
        resp.raise_for_status()
        jobs_raw = resp.json().get("data", [])
        for job in jobs_raw:
            jobs_cleaned.append({
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
                "source": "JSearch"
            })
    except Exception as e:
        print("❌ JSearch API error:", e)
    return jobs_cleaned

@router.post("/jobs")
def get_jobs(data: dict = Body(...)):
    try:
        preferred_roles = data.get("preferredRoles") or data.get("preferred_roles") or []
        preferred_cities = data.get("preferredCities") or data.get("preferred_cities") or []
        role = preferred_roles[0] if preferred_roles else ""
        city = preferred_cities[0] if preferred_cities else None
        keyword = role or "Software Engineer"
        limit = 12

        jobs = fetch_jsearch_jobs(keyword, city, limit)
        if not jobs:
            jobs = fetch_remotive_jobs(keyword, city, limit)

        if not jobs:
            raise HTTPException(status_code=502, detail="Could not fetch jobs from any source.")

        return {"jobs": jobs}

    except Exception as e:
        print("❌ Critical /jobs error:", e)
        raise HTTPException(status_code=500, detail="Could not fetch jobs.")

@router.get("/job/{job_id}")
def get_job_detail(job_id: str):
    # Try JSearch detail first (if you have API, else skip)
    JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
    JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")
    if JSEARCH_API_KEY and JSEARCH_API_HOST:
        try:
            url = f"https://{JSEARCH_API_HOST}/job-details"
            headers = {
                "X-RapidAPI-Key": JSEARCH_API_KEY,
                "X-RapidAPI-Host": JSEARCH_API_HOST,
            }
            params = {"job_id": job_id}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                job = resp.json()
                if job:
                    return {
                        "id": job.get("job_id", job_id),
                        "title": job.get("job_title", ""),
                        "company": job.get("employer_name", ""),
                        "location": job.get("job_city", "") or job.get("job_country", ""),
                        "salary": job.get("job_min_salary") or "N/A",
                        "description": job.get("job_description", ""),
                        "link": job.get("job_apply_link", ""),
                        "posted": job.get("job_posted_at_datetime_utc", ""),
                        "type": job.get("job_employment_type") or "Unknown",
                        "logo": job.get("employer_logo") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
                        "source": "JSearch"
                    }
        except Exception as e:
            print("❌ JSearch detail error:", e)
    # Remotive fallback
    try:
        resp = requests.get(f"{REMOTIVE_API}", timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
        for job in jobs:
            if str(job["id"]) == str(job_id):
                return {
                    "id": str(job["id"]),
                    "title": job["title"],
                    "company": job["company_name"],
                    "location": job["candidate_required_location"],
                    "salary": job.get("salary", "N/A"),
                    "description": job.get("description", ""),
                    "link": job.get("url", ""),
                    "posted": job.get("publication_date", ""),
                    "type": job["job_type"],
                    "logo": job.get("company_logo_url") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
                    "source": "Remotive"
                }
    except Exception as e:
        print("❌ Remotive detail error:", e)
    raise HTTPException(status_code=404, detail="Job not found")
