# utils/job_fetcher.py

import requests
import os

# You can also load from environment securely (especially on Replit)
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY") or "8a5fb61109mshe47ce5d8b9df44dp1e2bf9jsne5d0f209c82a"
JSEARCH_API_URL = "https://jsearch.p.rapidapi.com/search"

def get_jobs_from_jsearch(query, location="United States", num_pages=1):
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": f"{query} in {location}",
        "page": "1",
        "num_pages": str(num_pages)
    }

    try:
        response = requests.get(JSEARCH_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Fetch Failed: {e}")
        return []
