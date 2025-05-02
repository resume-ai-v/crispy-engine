
# utils/job_fetcher.py

import requests
import os
from dotenv import load_dotenv
load_dotenv()

JSEARCH_API_URL = "https://jsearch.p.rapidapi.com/search"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") or "8a5fb61109mshe47ce5d8b9df44dp1e2bf9jsne5d0f209c82a'"
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

def get_jobs_from_jsearch(role="Software Engineer", location="Remote", limit=10):
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    params = {
        "query": f"{role} in {location}",
        "num_pages": 1
    }

    response = requests.get(JSEARCH_API_URL, headers=headers, params=params)
    data = response.json()

    jobs = []
    for job in data.get("data", [])[:limit]:
        jobs.append({
            "job_title": job.get("job_title"),
            "employer_name": job.get("employer_name"),
            "job_city": job.get("job_city", "Remote"),
            "job_apply_link": job.get("job_apply_link"),
            "job_description": job.get("job_description", "")
        })

    return jobs
