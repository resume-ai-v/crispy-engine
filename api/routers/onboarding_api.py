# backend/onboarding_api.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Define the request body schema
class OnboardingData(BaseModel):
    firstStepSelections: List[str]
    educationStatus: str
    fieldOfStudy: str
    skills: List[str]
    preferredRoles: List[str]
    employmentTypes: List[str]
    preferredCities: List[str]

@router.post("/onboarding")
async def save_onboarding(data: OnboardingData, request: Request):
    # Save to session for now (later: save to DB)
    request.session["onboarding_data"] = data.dict()

    return {"status": "success"}
