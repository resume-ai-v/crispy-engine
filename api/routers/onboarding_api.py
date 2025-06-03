from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List

router = APIRouter()

class OnboardingData(BaseModel):
    firstStepSelections: List[str]
    educationStatus: str
    fieldOfStudy: str
    skills: List[str]
    resumeName: str = ""
    preferredRoles: List[str]
    employmentTypes: List[str]
    preferredCities: List[str]

@router.post("/api/onboarding")
async def save_onboarding(data: OnboardingData, request: Request):
    request.session["onboarding_data"] = data.dict()
    return {"status": "success"}
