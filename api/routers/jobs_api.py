from fastapi import APIRouter, HTTPException, Body
from ai_agents.jd_matcher.tool import match_resume_to_jd
from jobs.scrape_job import scrape_job_posting

router = APIRouter()

@router.post("/api/match")
def match(data: dict = Body(...)):
    try:
        score = match_resume_to_jd(data['resume'], data['jd'])
        return {"match_score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape")
def scrape(url: str):
    try:
        jd, role, company = scrape_job_posting(url)
        return {"jd": jd, "role": role, "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
