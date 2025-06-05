import os
import requests
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_API_HOST = os.getenv("JSEARCH_API_HOST")

def extract_keywords_gpt(resume):
    """
    Uses OpenAI GPT to extract the most relevant job title or keywords for job search.
    """
    import openai
    openai.api_key = OPENAI_API_KEY
    prompt = (
        "Given the following resume text, extract the **single most relevant job title** or, if not possible, "
        "the top 3 most relevant job keywords or skills (comma-separated, no explanation):\n\n"
        f"Resume:\n{resume}\n\nJob Title or Top 3 Keywords:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are an expert resume parser."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=32,
            temperature=0.2,
        )
        result = response["choices"][0]["message"]["content"].strip()
        # Clean up: Only take first line/first phrase, remove explanations or sentences
        if "," in result:
            # Top 3 skills/keywords
            return ",".join([kw.strip() for kw in result.split(",")[:3]])
        return result.split("\n")[0][:48]  # Never longer than 48 chars
    except Exception as e:
        print(f"❌ GPT extraction failed: {e}")
        # Fallback: just "Software Engineer"
        return "Software Engineer"

def query_jsearch(keyword, limit=10, location="United States"):
    """
    Queries JSearch for jobs matching the given keyword(s).
    """
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
    Production endpoint: returns job recommendations based on resume using GPT + JSearch (RapidAPI).
    """
    try:
        resume = data.get("resume", "").strip()
        if not resume or len(resume) < 8:
            keyword = "Software Engineer"
        else:
            keyword = extract_keywords_gpt(resume)
        jobs = query_jsearch(keyword)
        return jobs or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")
