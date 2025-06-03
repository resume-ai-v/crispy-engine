from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class OnboardingData(BaseModel):
    firstStepSelections: List[str]
    educationStatus: str
    fieldOfStudy: str
    skills: List[str]
    resumeName: str
    preferredRoles: List[str]
    employmentTypes: List[str]
    preferredCities: List[str]

@router.post("/onboarding")
async def save_onboarding(data: OnboardingData, request: Request):
    """
    This endpoint saves the onboarding data into the session (for now).
    Later, you can persist to the database or call some service.
    """
    try:
        request.session["onboarding_data"] = data.dict()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
