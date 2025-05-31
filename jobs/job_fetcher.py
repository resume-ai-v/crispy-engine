import requests
import time
import os
from functools import lru_cache

# Load API keys from environment variables
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")

# In-memory cache to avoid excessive external calls
_cached_jobs = []
_cache_timestamp = 0
_CACHE_EXPIRY = 300  # 5 minutes

# ✅ JSON safe converter
def make_json_safe(job):
    return {
        k: list(v) if isinstance(v, set) else v
        for k, v in job.items()
    }

def fetch_jobs_from_api(keyword="software engineer", location="United States"):
    global _cached_jobs, _cache_timestamp

    now = time.time()
    if _cached_jobs and (now - _cache_timestamp) < _CACHE_EXPIRY:
        return _cached_jobs

    remotive_jobs = fetch_remotive_jobs(keyword)
    jsearch_jobs = fetch_jsearch_jobs(keyword)

    combined = [make_json_safe(job) for job in remotive_jobs + jsearch_jobs]

    _cached_jobs = combined
    _cache_timestamp = now
    return combined


def fetch_remotive_jobs(keyword):
    try:
        url = f"https://remotive.io/api/remote-jobs?search={keyword}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        jobs = []
        for job in data.get("jobs", []):
            jobs.append({
                "id": str(job["id"]),
                "title": job["title"],
                "company": job["company_name"],
                "location": job.get("candidate_required_location", "Remote"),
                "type": job.get("job_type", "Full Time"),
                "salary": job.get("salary", "$100k - $150k"),
                "posted": job.get("publication_date", "Today"),
                "url": job["url"],
                "logo": job.get("company_logo_url", ""),
                "jd_text": job.get("description", ""),
                "source": "Remotive"
            })
        return jobs
    except Exception as e:
        print("❌ Remotive failed:", e)
        return []


def fetch_jsearch_jobs(keyword):
    try:
        url = f"https://jsearch.p.rapidapi.com/search?query={keyword}&page=1&num_pages=1"
        headers = {
            "X-RapidAPI-Key": JSEARCH_API_KEY,
            "X-RapidAPI-Host": JSEARCH_API_HOST,
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        jobs = []
        for job in data.get("data", []):
            jobs.append({
                "id": str(job["job_id"]),
                "title": job["job_title"],
                "company": job["employer_name"],
                "location": job.get("job_city", "Remote"),
                "type": job.get("job_employment_type", "Full Time"),
                "salary": job.get("job_salary", "$120k - $160k"),
                "posted": job.get("job_posted_at_datetime_utc", "Recently"),
                "url": job.get("job_apply_link", ""),
                "logo": job.get("employer_logo", ""),
                "jd_text": job.get("job_description", ""),
                "source": "JSearch"
            })
        return jobs
    except Exception as e:
        print("❌ JSearch failed:", e)
        return []
