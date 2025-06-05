from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any

router = APIRouter()

class OnboardingData(BaseModel):
    firstStepSelections: Optional[List[str]] = Field(default_factory=list)
    educationStatus: Optional[str] = ""
    fieldOfStudy: Optional[str] = ""
    skills: Optional[List[str]] = Field(default_factory=list)
    resumeName: Optional[str] = ""
    preferredRoles: Optional[List[str]] = Field(default_factory=list)
    employmentTypes: Optional[List[str]] = Field(default_factory=list)
    preferredCities: Optional[List[str]] = Field(default_factory=list)

@router.post("/api/onboarding")
async def save_onboarding(data: OnboardingData, request: Request):
    try:
        # Validate types (just in case frontend sends wrong type)
        if not isinstance(data.firstStepSelections, list):
            raise HTTPException(status_code=400, detail="firstStepSelections must be a list")
        if not isinstance(data.skills, list):
            raise HTTPException(status_code=400, detail="skills must be a list")
        if not isinstance(data.preferredRoles, list):
            raise HTTPException(status_code=400, detail="preferredRoles must be a list")
        if not isinstance(data.employmentTypes, list):
            raise HTTPException(status_code=400, detail="employmentTypes must be a list")
        if not isinstance(data.preferredCities, list):
            raise HTTPException(status_code=400, detail="preferredCities must be a list")

        # Store in session for user
        request.session["onboarding_data"] = data.dict()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save onboarding data: {str(e)}")
