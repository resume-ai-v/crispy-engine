from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from utils.resume.extract_text import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User

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
