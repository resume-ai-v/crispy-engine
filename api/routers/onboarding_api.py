from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User

router = APIRouter()

class OnboardingData(BaseModel):
    firstStepSelections: Optional[List[str]] = Field(default_factory=list)
    educationStatus: Optional[str] = ""
    fieldOfStudy: Optional[str] = ""
    skills: Optional[List[str]] = Field(default_factory=list)
    resumeName: Optional[str] = ""
    resumeText: Optional[str] = ""   # NEW: Save plain text of resume
    preferredRoles: Optional[List[str]] = Field(default_factory=list)
    employmentTypes: Optional[List[str]] = Field(default_factory=list)
    preferredCities: Optional[List[str]] = Field(default_factory=list)

@router.post("/onboarding")
async def save_onboarding(
    data: OnboardingData,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    user.onboarding_data = data.dict()
    if data.resumeText:
        user.resume_text = data.resumeText
    db.add(user)
    await db.commit()
    return {"status": "success"}

@router.get("/onboarding")
async def get_onboarding(
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user)
):
    onboarding = user.onboarding_data or {}
    onboarding["resume_text"] = user.resume_text or ""
    return onboarding

# --- Static Suggestions ---
SKILLS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "C++", "C#", "AWS", "Django",
    "Flask", "FastAPI", "Machine Learning", "Deep Learning", "Data Analysis", "TensorFlow",
    "Pandas", "Keras", "NLP", "Docker", "Kubernetes", "Linux", "HTML", "CSS", "Git"
]
ROLES = [
    "Software Engineer", "Data Scientist", "Frontend Developer", "Backend Developer", "AI Engineer",
    "Machine Learning Engineer", "DevOps Engineer", "Full Stack Developer", "Product Manager",
    "QA Engineer", "Data Analyst", "Cloud Engineer", "Mobile Developer"
]
CITIES = [
    "San Francisco", "New York", "Dallas", "Austin", "Houston", "Seattle", "Chicago", "Atlanta",
    "Boston", "Los Angeles", "Denver", "San Diego", "Remote"
]

def search_options(options, q):
    q_lower = (q or "").strip().lower()
    results = [opt for opt in options if q_lower in opt.lower()]
    return results[:10]

@router.get("/suggest/skills")
async def suggest_skills(q: str = Query(..., min_length=1)):
    return {"options": search_options(SKILLS, q)}

@router.get("/suggest/roles")
async def suggest_roles(q: str = Query(..., min_length=1)):
    return {"options": search_options(ROLES, q)}

@router.get("/suggest/cities")
async def suggest_cities(q: str = Query(..., min_length=1)):
    return {"options": search_options(CITIES, q)}
