# jobs/job_fetcher.py

import requests
from bs4 import BeautifulSoup

def fetch_jobs_from_api(keyword="data scientist", limit=20):
    jobs = []

    # ✅ Remotive API
    try:
        remotive_url = f"https://remotive.io/api/remote-jobs?search={keyword}"
        res = requests.get(remotive_url)
        for job in res.json().get("jobs", [])[:limit]:
            jobs.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "type": job.get("job_type", ""),
                "url": job.get("url"),
                "jd_text": job.get("description", ""),
                "h1b_sponsor": "remote" in job.get("candidate_required_location", "").lower()
            })
    except Exception as e:
        print(f"❌ Remotive failed: {e}")

    # ✅ Wellfound (AngelList) Authenticated Scraping
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Cookie": "session_id=your_actual_session_cookie_here"
        }
        url = f"https://wellfound.com/jobs?keyword={keyword}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for i, div in enumerate(soup.select("div[data-job-id]")[:limit]):
            try:
                job_id = div.get("data-job-id")
                title_tag = div.select_one("h3")
                company_tag = div.select_one("h2")
                location_tag = div.select_one(".location")

                jobs.append({
                    "id": job_id,
                    "title": title_tag.text.strip() if title_tag else "Unknown",
                    "company": company_tag.text.strip() if company_tag else "Unknown",
                    "location": location_tag.text.strip() if location_tag else "N/A",
                    "type": "Full Time",
                    "url": f"https://wellfound.com/jobs/{job_id}",
                    "jd_text": "Details fetched via Wellfound scraping.",
                    "h1b_sponsor": False
                })
            except Exception as e:
                print(f"⚠️ Parsing failed: {e}")
    except Exception as e:
        print(f"❌ Wellfound failed: {e}")

    return jobs
