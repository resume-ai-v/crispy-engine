from fastapi import APIRouter, Request, Query, HTTPException
from jobs.job_fetcher import fetch_jobs_from_api
from ai_agents.jd_matcher.tool import match_resume_to_jd
import json, re

router = APIRouter()


def extract_numeric_score(score_str: str) -> float:
    """
    Converts a match score like 'Match: 82%' or '85%' to float.
    Returns 0.0 if parsing fails.
    """
    try:
        match = re.search(r"(\\d{1,3})", score_str)
        return float(match.group(1)) if match else 0.0
    except:
        return 0.0


@router.post("/jobs")
async def get_filtered_jobs(
    request: Request,
    top_n: int = Query(10, ge=1, le=50),
    h1b_only: bool = Query(False),
    remote_only: bool = Query(False),
    fulltime_only: bool = Query(False)
):
    """
    Returns a sorted and filtered list of job listings based on match score and filters.

    Filters:
    - h1b_only: whether to show only H1B-sponsoring companies
    - remote_only: only remote jobs
    - fulltime_only: only full-time roles
    - top_n: max number of jobs to return
    """

    try:
        data = await request.json()
        resume = data.get("resume", "")

        jobs = fetch_jobs_from_api()

        enriched_jobs = []
        for job in jobs:
            jd_text = job.get("jd_text", "")
            try:
                raw_score = match_resume_to_jd(resume, jd_text)
                score_value = extract_numeric_score(raw_score)
                job["match_score"] = raw_score
                job["numeric_score"] = score_value
                enriched_jobs.append(job)
            except:
                job["match_score"] = "error"
                job["numeric_score"] = 0.0
                enriched_jobs.append(job)

        # Apply filters
        filtered = [
            job for job in enriched_jobs
            if (not h1b_only or job.get("h1b_sponsor", False)) and
               (not remote_only or "remote" in job.get("location", "").lower()) and
               (not fulltime_only or job.get("type", "").lower() == "full time")
        ]

        # Sort by descending score
        sorted_jobs = sorted(filtered, key=lambda j: j["numeric_score"], reverse=True)

        return sorted_jobs[:top_n]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
