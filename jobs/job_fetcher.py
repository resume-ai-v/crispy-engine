import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("JSEARCH_API_KEY")
API_HOST = os.getenv("JSEARCH_API_HOST")

def get_jobs_from_jsearch(query="data analyst", location="remote"):
    url = f"https://{API_HOST}/search"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data.get("data", [])[:5]
    except Exception as e:
        print("❌ JSearch error:", e)
        return load_fallback_jobs()

def load_fallback_jobs():
    import json
    try:
        with open("jobs/fallback_jobs.json") as f:
            return json.load(f)
    except:
        return []
