# api/routers/resume_api.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ResumePayload(BaseModel):
    resume: str
    jd: str


@router.post("/tailor-resume")
async def tailor_resume_route(data: ResumePayload):
    """
    Endpoint: POST /tailor-resume
    Expects JSON: { "resume": "<the resume text>", "jd": "<the job description>" }

    Returns JSON:
      {
        "tailored_resume": "<GPT-tailored résumé>",
        "original_match": "<X% Match – explanation>",
        "tailored_match": "<Y% Match – explanation>"
      }
    """
    if not data.resume or not data.jd:
        raise HTTPException(status_code=400, detail="Missing 'resume' or 'jd' field.")

    # Import the function from our updated ai_agents code
    from ai_agents.resume_tailor.tool import tailor_resume

    try:
        result = tailor_resume(data.resume, data.jd)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while tailoring the résumé. {str(e)}"
        )
