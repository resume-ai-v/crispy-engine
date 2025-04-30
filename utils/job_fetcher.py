import requests

JSEARCH_API_KEY = "8a5fb61109mshe47ce5d8b9df44dp1e2bf9jsne5d0f209c82a'"
JSEARCH_API_URL = "jsearch.p.rapidapi.com"

def fetch_jobs(query, location="United States", num_pages=1):
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": num_pages
    }

    try:
        response = requests.get(JSEARCH_API_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Fetch Failed: {e}")
        return []
