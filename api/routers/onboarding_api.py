from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from api.extensions.db import get_db
from api.utils.auth import get_current_user  # import as above

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
async def save_onboarding(
    data: OnboardingData,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        user.onboarding_data = data.dict()
        db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save onboarding data: {str(e)}")

@router.get("/api/onboarding")
async def get_onboarding(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return user.onboarding_data or {}
