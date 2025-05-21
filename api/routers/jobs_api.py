# ----------------------------------
# ✅ FILE: api/routers/jobs_api.py
# ----------------------------------
from fastapi import APIRouter, Request, Query, HTTPException
from jobs.job_fetcher import fetch_jobs_from_api
from ai_agents.jd_matcher.tool import match_resume_to_jd
import re
from ai_agents.job_explainer.tool import explain_job_match
from jobs.job_fetcher import fetch_jobs_from_api
router = APIRouter()

def extract_numeric_score(score_str: str) -> float:
    try:
        match = re.search(r"(\d{1,3})", score_str)
        return float(match.group(1)) if match else 0.0
    except:
        return 0.0

@router.post("/jobs")
async def get_filtered_jobs(
    request: Request,
    keyword: str = Query("data scientist"),
    top_n: int = Query(10, ge=1, le=50),
    h1b_only: bool = Query(False),
    remote_only: bool = Query(False),
    fulltime_only: bool = Query(False)
):
    try:
        body = await request.json()
        resume = body.get("resume", "")
        jobs = fetch_jobs_from_api(keyword=keyword)

        enriched = []
        for job in jobs:
            jd_text = job.get("jd_text", "")
            try:
                raw_score = match_resume_to_jd(resume, jd_text)
                job["match_score"] = raw_score
                job["numeric_score"] = extract_numeric_score(raw_score)
            except:
                job["match_score"] = "error"
                job["numeric_score"] = 0.0
            enriched.append(job)

        filtered = [
            job for job in enriched
            if (not h1b_only or job.get("h1b_sponsor", False)) and
               (not remote_only or "remote" in job.get("location", "").lower()) and
               (not fulltime_only or job.get("type", "").lower() == "full time")
        ]

        sorted_jobs = sorted(filtered, key=lambda j: j["numeric_score"], reverse=True)
        return sorted_jobs[:top_n]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# ✅ GET /job/{id} - Job Details
# ------------------------------
from fastapi import Path
from jobs.job_fetcher import fetch_jobs_from_api  # ensure this fetcher includes job IDs


# ✅ Full job detail by ID
@router.post("/job/{job_id}")
async def get_job_details(job_id: str, request: Request):
    resume = (await request.json()).get("resume", "")
    jobs = fetch_jobs_from_api()  # could be cached later

    job = next((j for j in jobs if str(j["id"]) == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    explanation = explain_job_match(resume, job["jd_text"])
    return {
        "job": job,
        "match_explanation": explanation
    }