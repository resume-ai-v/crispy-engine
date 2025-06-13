import os
import requests
from fastapi import APIRouter, HTTPException, Body
from typing import Optional

router = APIRouter()

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

def fetch_remotive_jobs(keyword: str = "Software Engineer", limit: int = 12):
    params = {"search": keyword}
    try:
        resp = requests.get(REMOTIVE_API, params=params, timeout=12)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
    except Exception as e:
        print("❌ Remotive API error:", e)
        return []
    jobs_cleaned = []
    for job in jobs[:limit]:
        jobs_cleaned.append({
            "id": f"remotive_{job['id']}",
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("candidate_required_location", "Remote"),
            "salary": job.get("salary", "N/A"),
            "description": (job.get("description", "") or "")[:300],
            "jd_text": job.get("description", "") or "",
            "link": job.get("url", ""),
            "posted": job.get("publication_date", ""),
            "type": job.get("job_type", "Unknown"),
            "logo": job.get("company_logo_url") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
            "source": "Remotive",
        })
    return jobs_cleaned

def fetch_jsearch_jobs(keyword: str, city: Optional[str] = None, limit: int = 12):
    jobs_cleaned = []
    JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
    JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")
    if not JSEARCH_API_KEY or not JSEARCH_API_HOST:
        print("JSearch API not configured.")
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
        resp = requests.get(url, headers=headers, params=params, timeout=18)
        resp.raise_for_status()
        jobs_raw = resp.json().get("data", [])
        for job in jobs_raw:
            jobs_cleaned.append({
                "id": f"jsearch_{job.get('job_id')}",
                "title": job.get("job_title", ""),
                "company": job.get("employer_name", ""),
                "location": job.get("job_city", "") or job.get("job_country", ""),
                "salary": job.get("job_min_salary") or "N/A",
                "description": (job.get("job_description") or "")[:300],
                "jd_text": job.get("job_description", "") or "",
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
    preferred_roles = data.get("preferredRoles") or data.get("preferred_roles") or []
    preferred_cities = data.get("preferredCities") or data.get("preferred_cities") or []
    role = preferred_roles[0] if preferred_roles else ""
    city = preferred_cities[0] if preferred_cities else None
    keyword = role or "Software Engineer"
    limit = 12

    # Prefer JSearch, fallback to Remotive if empty
    jobs = fetch_jsearch_jobs(keyword, city, limit)
    if not jobs:
        jobs = fetch_remotive_jobs(keyword, limit)
    if not jobs:
        raise HTTPException(status_code=502, detail="Could not fetch jobs from any source.")

    return {"jobs": jobs}

@router.post("/job/{job_id}")
def get_job_detail(job_id: str):
    JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
    JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")

    # --- JSearch detail ---
    if job_id.startswith("jsearch_") and JSEARCH_API_KEY and JSEARCH_API_HOST:
        actual_id = job_id.replace("jsearch_", "")
        try:
            url = f"https://{JSEARCH_API_HOST}/job-details"
            headers = {
                "X-RapidAPI-Key": JSEARCH_API_KEY,
                "X-RapidAPI-Host": JSEARCH_API_HOST,
            }
            params = {"job_id": actual_id}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            print("Job detail API status:", resp.status_code)
            if resp.status_code == 200:
                data = resp.json()
                # JSearch job-details returns a 'data' list
                if data.get("status") == "OK" and data.get("data"):
                    job = data["data"][0]
                    return {
                        "job": {
                            "id": f"jsearch_{job.get('job_id', actual_id)}",
                            "title": job.get("job_title", ""),
                            "company": job.get("employer_name", ""),
                            "location": job.get("job_city", "") or job.get("job_country", ""),
                            "salary": job.get("job_min_salary") or "N/A",
                            "description": job.get("job_description", ""),
                            "jd_text": job.get("job_description", ""),
                            "link": job.get("job_apply_link", ""),
                            "posted": job.get("job_posted_at_datetime_utc", ""),
                            "type": job.get("job_employment_type") or "Unknown",
                            "logo": job.get("employer_logo") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
                            "source": "JSearch",
                            "match_score": 0  # Set real value if you calculate
                        }
                    }
                else:
                    print("JSearch job-details: No job found for that ID.")
            else:
                print("Job details API failed:", resp.status_code, resp.text)
        except Exception as e:
            print("❌ JSearch job detail error:", e)

    # --- Remotive fallback ---
    if job_id.startswith("remotive_"):
        actual_id = job_id.replace("remotive_", "")
        try:
            resp = requests.get(REMOTIVE_API, timeout=12)
            resp.raise_for_status()
            jobs = resp.json().get("jobs", [])
            for job in jobs:
                if str(job["id"]) == str(actual_id):
                    return {
                        "job": {
                            "id": f"remotive_{job['id']}",
                            "title": job.get("title", ""),
                            "company": job.get("company_name", ""),
                            "location": job.get("candidate_required_location", "Remote"),
                            "salary": job.get("salary", "N/A"),
                            "description": job.get("description", ""),
                            "jd_text": job.get("description", "") or "",
                            "link": job.get("url", ""),
                            "posted": job.get("publication_date", ""),
                            "type": job.get("job_type", "Unknown"),
                            "logo": job.get("company_logo_url") or "https://cdn-icons-png.flaticon.com/512/174/174872.png",
                            "source": "Remotive",
                            "match_score": 0
                        }
                    }
        except Exception as e:
            print("❌ Remotive detail error:", e)

    raise HTTPException(status_code=404, detail="Job not found")
