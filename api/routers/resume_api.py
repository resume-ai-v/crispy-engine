from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from utils.resume.extract_text import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User
import openai
import os

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    try:
        # Save file to temp location
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        # Extract plain text from PDF/DOCX/TXT
        text = extract_text_from_file(open(temp_path, "rb"), file.filename)
        # Save resume text to user profile for all future sessions/features
        user.resume_text = text
        db.add(user)
        await db.commit()
        # Also update onboarding_data in DB if exists
        onboarding = user.onboarding_data or {}
        onboarding["resume_text"] = text
        user.onboarding_data = onboarding
        db.add(user)
        await db.commit()
        return {"resume_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tailor-resume")
async def tailor_resume(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    """
    Tailors a user's resume to a specific job description using OpenAI GPT.
    Expects payload = { "resume": "...", "jd": "..." }
    """
    resume_text = payload.get("resume") or user.resume_text
    jd_text = payload.get("jd")
    if not resume_text or not jd_text:
        raise HTTPException(status_code=400, detail="Missing resume or job description.")

    # Call OpenAI to tailor the resume
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = (
            "You are an expert resume editor. Given the following resume and job description, "
            "tailor the resume so it maximizes the candidate's chance of getting this job. "
            "Use relevant keywords, highlight key skills, and make the resume ATS-friendly. "
            "Return only the improved resume text (no extra comments).\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}\n\nTailored Resume:"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional ATS resume optimization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.4,
        )
        tailored_resume = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

    # Optionally update user's tailored resume (future use)
    if hasattr(user, "tailored_resume"):
        user.tailored_resume = tailored_resume
        db.add(user)
        await db.commit()

    return {"tailored_resume": tailored_resume}
