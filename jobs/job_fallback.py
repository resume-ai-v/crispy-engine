import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_jobs_with_gpt(keyword: str = "data scientist") -> list:
    prompt = f"""
    Act as a job recommender assistant. Return a JSON array of 5 remote job openings matching this keyword: "{keyword}". 
    For each job, return:
    - id
    - title
    - company
    - location
    - jd_text (short JD)
    - url (apply link)
    - type (Full-time, Part-time, etc.)
    - posted_at (as "2 hours ago", etc.)
    - applicants_count (estimated number like "35")
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content.strip()

        import json
        jobs = json.loads(raw)
        print(f"[fetch_jobs_with_gpt] {len(jobs)} jobs from GPT fallback")
        return jobs
    except Exception as e:
        print("❌ GPT fallback failed:", str(e))
        return []
