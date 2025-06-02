# api/routers/jobs_api.py

import re
import time
import traceback
from fastapi import APIRouter, Request, HTTPException, Path, Query
from jobs.job_fetcher import fetch_jobs_from_api
from jobs.job_fallback import fetch_jobs_with_gpt
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.job_explainer.tool import explain_job_match  # if you still use it

router = APIRouter()

# ─── Global In-Memory Cache (refresh every 10 minutes) ──────────────────────────
JOB_CACHE = {
    "timestamp": 0,
    "jobs": []
}
CACHE_DURATION = 600  # seconds (10 minutes)


# ─── Helper: extract a float from strings like "85% Match" or "75 percent match" ──
def extract_numeric_score(score_str: str) -> float:
    """
    Given strings like "85% Match" or "75 percent match", return 85.0 or 75.0.
    If no number is found, return 0.0.
    """
    try:
        match = re.search(r"(\d{1,3})(?:\s*%|\s+percent)?", score_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 0.0
    except Exception:
        return 0.0


def extract_resume_from_payload(payload: dict) -> str:
    """
    Robustly extract a 'resume' string from the JSON body.
    If payload["resume"] is nested inside another dict, dig one level deeper.
    """
    resume = payload.get("resume", "")
    if isinstance(resume, dict) and "resume" in resume:
        resume = resume["resume"]
    if not isinstance(resume, str):
        resume = ""
    return resume.strip()


# ─── POST /api/jobs ───────────────────────────────────────────────────────────────
@router.post("/api/jobs")
async def get_filtered_jobs(
    request: Request,
    keyword: str = Query("software engineer"),
    top_n: int = Query(10, ge=1, le=100),
    h1b_only: bool = Query(False),
    remote_only: bool = Query(False),
    fulltime_only: bool = Query(False),
    sort_by: str = Query("TopMatched"),
):
    """
    1. Reads { resume: "..." } from the request body.
    2. Fetches a list of jobs (from cache or external API).
    3. Runs match_resume_to_jd(...) to compute "match_score" (string) and "numeric_score" (float).
    4. Filters by H1B/remote/fulltime flags.
    5. Sorts by numeric_score (default) or by recency.
    6. Returns up to top_n jobs.
    """
    try:
        body = await request.json()
        resume_text = extract_resume_from_payload(body)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Missing resume (string expected).")

        now_ts = time.time()

        # Use cache if it is still fresh
        if (now_ts - JOB_CACHE["timestamp"] < CACHE_DURATION) and JOB_CACHE["jobs"]:
            jobs_list = JOB_CACHE["jobs"]
        else:
            # Fetch fresh from external sources
            try:
                jobs_list = fetch_jobs_from_api(keyword=keyword)
                if not jobs_list:
                    # Fall back to GPT-based fallback if needed
                    jobs_list = fetch_jobs_with_gpt(keyword)
            except Exception as e:
                print("Job fetching main source failed:", e)
                traceback.print_exc()
                jobs_list = fetch_jobs_with_gpt(keyword)

            JOB_CACHE["jobs"] = jobs_list
            JOB_CACHE["timestamp"] = now_ts

        enriched = []
        for job in jobs_list:
            jd_text = job.get("jd_text", "") or ""
            try:
                raw_score = match_resume_to_jd(resume_text, jd_text)
            except Exception as e:
                print(f"Resume-JD match failed: {e}")
                raw_score = "0% Match – Unable to compute match."

            numeric = extract_numeric_score(raw_score)
            job_copy = job.copy()
            job_copy["match_score"] = raw_score
            job_copy["numeric_score"] = numeric
            enriched.append(job_copy)

        # Apply filters (if location or type is missing, treat as empty string)
        filtered = []
        for job in enriched:
            # Some job postings may lack location or type fields
            loc = (job.get("location") or "").lower()
            jtype = (job.get("type") or "").lower()

            if h1b_only and not job.get("h1b_sponsor", False):
                continue
            if remote_only and "remote" not in loc:
                continue
            if fulltime_only and "full" not in jtype:
                continue

            filtered.append(job)

        # Sort by either recency or match score
        if sort_by == "MostRecent":
            sorted_jobs = sorted(filtered, key=lambda j: j.get("timestamp", 0), reverse=True)
        else:
            sorted_jobs = sorted(filtered, key=lambda j: j["numeric_score"], reverse=True)

        return sorted_jobs[:top_n]

    except HTTPException:
        raise
    except Exception as e:
        print("API /api/jobs failed:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Job fetch failed: {e}")


# ─── POST /api/job/{job_id} ────────────────────────────────────────────────────────
@router.post("/api/job/{job_id}")
async def get_job_details(job_id: str = Path(...), request: Request = None):
    """
    1. Reads { resume: "..." } from the request body.
    2. Ensures our JOB_CACHE is fresh (fetch if stale).
    3. Looks up job_id in JOB_CACHE["jobs"].
    4. Runs explain_job_match(...) or match_resume_to_jd(...) to generate an explanation & numeric score.
    5. Returns { "job": { …job fields… plus match_score, explanation } }.
    """
    try:
        body = await request.json()
        resume_text = extract_resume_from_payload(body)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Missing resume (string expected).")

        # Refresh the cache if empty or expired
        now_ts = time.time()
        if not JOB_CACHE["jobs"] or (now_ts - JOB_CACHE["timestamp"] > CACHE_DURATION):
            try:
                refreshed = fetch_jobs_from_api()
                if not refreshed:
                    refreshed = fetch_jobs_with_gpt("")
                JOB_CACHE["jobs"] = refreshed
                JOB_CACHE["timestamp"] = now_ts
            except Exception as e:
                print("Cache refresh failed, continuing with what we have:", e)

        # Find the requested job by ID
        job = next((j for j in JOB_CACHE["jobs"] if str(j.get("id")) == job_id), None)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Compute a GPT-based explanation string (e.g. "85% Match – Here’s why...")
        try:
            explanation = explain_job_match(resume_text, job.get("jd_text", ""))
        except Exception as e:
            print("Job explanation failed:", e)
            explanation = ""

        numeric = extract_numeric_score(explanation) if explanation else 0.0

        response_job = job.copy()
        response_job["match_score"] = f"{numeric:g}%"
        response_job["explanation"] = explanation

        return {"job": response_job}

    except HTTPException:
        raise
    except Exception as e:
        print("API /api/job/{job_id} failed:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Job detail fetch failed: {e}")
