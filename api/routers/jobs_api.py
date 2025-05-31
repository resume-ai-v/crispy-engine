from fastapi import APIRouter, Request, Query, HTTPException, Path
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.job_explainer.tool import explain_job_match
from jobs.job_fetcher import fetch_jobs_from_api
from jobs.job_fallback import fetch_jobs_with_gpt
from utils.simple_cache import simple_cache
import re
import time

router = APIRouter()

# ------------------------------
# ⏱️ Simple in-memory cache
# ------------------------------
JOB_CACHE = {"timestamp": 0, "jobs": []}
CACHE_DURATION = 600  # 10 minutes

# ------------------------------
# Extract numeric match score
# ------------------------------
def extract_numeric_score(score_str: str) -> float:
    try:
        match = re.search(r"(\d{1,3})", score_str)
        return float(match.group(1)) if match else 0.0
    except:
        return 0.0

# ------------------------------
# ✅ GET Recommended Jobs
# ------------------------------
@router.post("/api/jobs")
async def get_filtered_jobs(
    request: Request,
    keyword: str = Query("software engineer"),
    top_n: int = Query(10, ge=1, le=100),
    h1b_only: bool = Query(False),
    remote_only: bool = Query(False),
    fulltime_only: bool = Query(False),
    sort_by: str = Query("TopMatched")  # or "MostRecent"
):
    try:
        body = await request.json()
        resume = body.get("resume", "").strip()
        if not resume:
            raise HTTPException(status_code=400, detail="Missing resume.")

        now = time.time()

        # Use cache if fresh
        if now - JOB_CACHE["timestamp"] < CACHE_DURATION and JOB_CACHE["jobs"]:
            jobs = JOB_CACHE["jobs"]
        else:
            try:
                jobs = fetch_jobs_from_api(keyword=keyword)
                JOB_CACHE["jobs"] = jobs
                JOB_CACHE["timestamp"] = now
            except Exception:
                print("❌ Remotive failed. Using GPT fallback.")
                jobs = fetch_jobs_with_gpt(keyword)
                JOB_CACHE["jobs"] = jobs
                JOB_CACHE["timestamp"] = now

        enriched = []
        for job in jobs:
            jd_text = job.get("jd_text", "")
            try:
                raw_score = match_resume_to_jd(resume, jd_text)
                job["match_score"] = raw_score
                job["numeric_score"] = extract_numeric_score(raw_score)
            except:
                job["match_score"] = "N/A"
                job["numeric_score"] = 0.0
            enriched.append(job)

        # Apply filters
        filtered = [
            job for job in enriched
            if (not h1b_only or job.get("h1b_sponsor", False)) and
               (not remote_only or "remote" in job.get("location", "").lower()) and
               (not fulltime_only or "full" in job.get("type", "").lower())
        ]

        # Sort
        if sort_by == "MostRecent":
            sorted_jobs = sorted(filtered, key=lambda j: j.get("timestamp", 0), reverse=True)
        else:
            sorted_jobs = sorted(filtered, key=lambda j: j["numeric_score"], reverse=True)

        return sorted_jobs[:top_n]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job fetch failed: {e}")

# ------------------------------
# ✅ GET Job Detail with GPT Explanation
# ------------------------------
@router.post("/api/job/{job_id}")
async def get_job_details(job_id: str = Path(...), request: Request = None):
    try:
        body = await request.json()
        resume = body.get("resume", "")
        if not resume:
            raise HTTPException(status_code=400, detail="Missing resume.")

        jobs = JOB_CACHE["jobs"] or fetch_jobs_from_api()
        job = next((j for j in jobs if str(j["id"]) == job_id), None)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        explanation = explain_job_match(resume, job["jd_text"])
        job["match_score"] = extract_numeric_score(explanation[:5])  # assume starts with "95%" etc
        job["explanation"] = explanation

        return { "job": job }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job detail fetch failed: {e}")
