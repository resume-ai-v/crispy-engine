# ----------------------------------
# ✅ FILE: jobs/job_fetcher.py
# ----------------------------------

import requests
import os

REMOTIVE_API_URL = "https://remotive.io/api/remote-jobs"
JSEARCH_API_URL = "https://jsearch.p.rapidapi.com/search"

# Load from .env if needed
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")

def fetch_jobs_from_remotive(keyword="data"):
    try:
        response = requests.get(REMOTIVE_API_URL, params={"search": keyword})
        data = response.json()
        jobs = []
        for job in data["jobs"]:
            jobs.append({
                "title": job["title"],
                "company": job["company_name"],
                "location": job["candidate_required_location"],
                "type": job["job_type"],
                "apply_url": job["url"],
                "jd_text": job["description"],
                "h1b_sponsor": False  # Remotive doesn’t give H1B info
            })
        return jobs
    except Exception as e:
        print("❌ Remotive Error:", e)
        return []

def fetch_jobs_from_jsearch(keyword="data"):
    try:
        headers = {
            "X-RapidAPI-Key": JSEARCH_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {"query": keyword, "num_pages": 1}
        response = requests.get(JSEARCH_API_URL, headers=headers, params=params)
        data = response.json()
        jobs = []
        for item in data.get("data", []):
            jobs.append({
                "title": item["job_title"],
                "company": item["employer_name"],
                "location": item["job_city"] + ", " + item["job_state"],
                "type": item.get("job_employment_type", "Full Time"),
                "apply_url": item["job_apply_link"],
                "jd_text": item["job_description"],
                "h1b_sponsor": "H1B" in item["job_description"]
            })
        return jobs
    except Exception as e:
        print("❌ JSearch Error:", e)
        return []

def fetch_jobs_from_api(keyword="data"):
    remotive_jobs = fetch_jobs_from_remotive(keyword)
    jsearch_jobs = fetch_jobs_from_jsearch(keyword)
    return remotive_jobs + jsearch_jobs
