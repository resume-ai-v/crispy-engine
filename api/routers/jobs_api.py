import os
import requests
from fastapi import APIRouter, HTTPException, Body, Request
from typing import Optional, List
from functools import lru_cache
import json
from pathlib import Path

router = APIRouter()

# --- Helper: Load fallback jobs for demo/staging ---
@lru_cache(maxsize=1)
def _load_fallback_jobs():
    json_path = Path(__file__).parent.parent.parent / "jobs" / "fallback_jobs.json"
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("❌ Could not load fallback_jobs.json:", e)
        return []

def get_fallback_jobs():
    jobs = _load_fallback_jobs()
    return [
        {
            "id": str(i),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", "Remote"),
            "type": job.get("type", "Full Time"),
            "salary": job.get("salary", "$120k-$160k"),
            "posted": job.get("posted_at", "Recently"),
            "url": job.get("url", ""),
            "logo": "https://cdn-icons-png.flaticon.com/512/174/174872.png",
            "jd_text": job.get("jd_text", ""),
            "description": job.get("jd_text", "")[:300],
            "source": "Fallback"
        }
        for i, job in enumerate(jobs)
    ]

@router.post("/jobs")
def get_jobs(data: dict = Body(...), request: Request = None):
    try:
        resume = data.get("resume") or data.get("resume_text") or ""
        preferred_roles = data.get("preferredRoles") or data.get("preferred_roles") or []
        preferred_cities = data.get("preferredCities") or data.get("preferred_cities") or []
        employment_types = data.get("employmentTypes") or data.get("employment_types") or []

        role = preferred_roles[0] if preferred_roles else ""
        city = preferred_cities[0] if preferred_cities else None
        keyword = role or "Software Engineer"

        jobs_cleaned = []

        # --- LIVE JSearch API ---
        try:
            JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
            JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")
            if not JSEARCH_API_KEY or not JSEARCH_API_HOST:
                raise Exception("JSearch API key/host missing")

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
                "limit": 12,
            }
            if city:
                params["location"] = city

            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                raise Exception(f"JSearch returned {resp.status_code}: {resp.text}")
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
            print("❌ JSearch API error, using fallback. Details:", e)
            jobs_cleaned = get_fallback_jobs()

        return {"jobs": jobs_cleaned}

    except Exception as e:
        print("❌ Critical /jobs error:", e)
        raise HTTPException(status_code=500, detail="Could not fetch jobs.")
