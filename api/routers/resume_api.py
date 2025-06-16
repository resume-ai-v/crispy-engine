import os
import io
import re
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse, JSONResponse
from utils.resume.extract_text import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User
from docx import Document
from fpdf import FPDF
import openai

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# --- Utility: Simple ATS Score
def compute_ats_score(resume: str, jd: str) -> int:
    resume_words = set(re.findall(r'\w+', resume.lower()))
    jd_words = set(re.findall(r'\w+', jd.lower()))
    stopwords = {"the", "and", "is", "in", "to", "of", "a", "for", "on", "with"}
    jd_keywords = [w for w in jd_words if w not in stopwords and len(w) > 2]
    if not jd_keywords:
        return 0
    match_count = sum(1 for word in jd_keywords if word in resume_words)
    ats_score = int((match_count / len(jd_keywords)) * 100)
    return min(ats_score, 100)

# --- Utility: Semantic Score (OpenAI v1.x syntax)
def compute_semantic_score(resume: str, jd: str) -> int:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("❌ OpenAI API Key missing in environment!")
            return compute_ats_score(resume, jd)
        client = openai.OpenAI(api_key=api_key)
        prompt = (
            f"Resume:\n{resume}\n\nJob Description:\n{jd}\n\n"
            "Score from 0 to 100 how well this resume fits the job description, "
            "considering skills, responsibilities, and experience. Only output the number."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8,
            temperature=0.1,
        )
        content = response.choices[0].message.content
        numbers = re.findall(r"\d+", content)
        score = int(numbers[0]) if numbers else compute_ats_score(resume, jd)
        return min(score, 100)
    except openai.RateLimitError as e:
        logging.error(f"OpenAI Rate Limit Error (Quota Exceeded) in semantic score: {e}")
        raise HTTPException(
            status_code=429,
            detail="You have exceeded your OpenAI API quota. Please check your plan and billing details."
        )
    except Exception as e:
        logging.error(f"Semantic score error (LLM fallback): {e}")
        return compute_ats_score(resume, jd)

# --- File upload endpoint ---
@router.post("/upload-resume")
async def upload_resume(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
):
    try:
        contents = await file.read()
        if not os.path.exists("/tmp"):
            os.makedirs("/tmp")
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        with open(temp_path, "rb") as f_read:
            text = extract_text_from_file(f_read, file.filename)

        os.remove(temp_path)

        user.resume_text = text
        db.add(user)
        await db.commit()
        if user.onboarding_data is not None:
            onboarding = user.onboarding_data or {}
            onboarding["resume_text"] = text
            user.onboarding_data = onboarding
            db.add(user)
            await db.commit()

        return {"resume_text": text}
    except Exception as e:
        logging.error(f"Error in upload_resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {e}")

# --- Tailor resume endpoint ---
@router.post("/tailor-resume")
async def tailor_resume(
        payload: dict = Body(...),
        db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
):
    try:
        resume_text = payload.get("resume") or getattr(user, "resume_text", None)
        jd_text = payload.get("jd")
        role = payload.get("role", "Generic")
        company = payload.get("company", "Unknown")
        logging.info(
            f"[Tailor Debug] User: {user.email if user else 'unknown'}, Resume present: {bool(resume_text)}, JD present: {bool(jd_text)}")

        if not resume_text or not jd_text:
            raise HTTPException(status_code=400, detail="Missing resume or job description.")

        max_len = 8000
        if len(resume_text) > max_len:
            resume_text = resume_text[:max_len]
        if len(jd_text) > max_len:
            jd_text = jd_text[:max_len]

        ats_score_orig = compute_ats_score(resume_text, jd_text)
        try:
            semantic_score_orig = compute_semantic_score(resume_text, jd_text)
        except HTTPException as he:
            if he.status_code == 429:
                semantic_score_orig = ats_score_orig
            else:
                raise
        original_match = round((ats_score_orig + semantic_score_orig) / 2)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OpenAI API Key on the server.")

        client = openai.OpenAI(api_key=api_key)
        prompt = (
            "You are an expert resume editor. Given the following resume and job description, "
            f"tailor the resume so it maximizes the candidate's chance of getting this {role} job at {company}. "
            "Use relevant keywords, highlight key skills, and make the resume ATS-friendly. "
            "Return only the improved resume text (no extra comments).\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}\n\nTailored Resume:"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are a professional ATS resume optimization assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3,
            )
            tailored_resume = response.choices[0].message.content.strip()
            if not tailored_resume or len(tailored_resume) < 100:
                logging.error("OpenAI returned empty or too short tailored resume.")
                raise HTTPException(status_code=500, detail="The AI failed to generate a valid tailored resume.")
        except openai.RateLimitError as e:
            logging.error(f"OpenAI Rate Limit Error (Quota Exceeded) during tailoring: {e}")
            return JSONResponse(
                status_code=429,
                content={"detail": "AI tailoring service is temporarily unavailable (quota exceeded or too many requests). Please try again later. [OpenAI Quota]"}
            )
        except Exception as e:
            logging.error(f"OpenAI tailoring error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred with the AI service: {e}")

        ats_score_tailored = compute_ats_score(tailored_resume, jd_text)
        try:
            semantic_score_tailored = compute_semantic_score(tailored_resume, jd_text)
        except HTTPException as he:
            if he.status_code == 429:
                semantic_score_tailored = ats_score_tailored
            else:
                raise
        tailored_match = round((ats_score_tailored + semantic_score_tailored) / 2)

        if hasattr(user, "tailored_resume"):
            user.tailored_resume = tailored_resume
            db.add(user)
            await db.commit()

        return {
            "tailored_resume": tailored_resume,
            "original_match": original_match,
            "tailored_match": tailored_match,
            "ats_score": ats_score_tailored,
            "semantic_score": semantic_score_tailored,
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"[TailorResume/ServerError] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

# --- PDF and DOCX Download ---
def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, text)
    return pdf.output(dest='S').encode('latin-1')

def generate_docx(text: str) -> bytes:
    doc = Document()
    text = text.replace('\x00', '')
    doc.add_paragraph(text)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()

@router.post("/download-resume")
async def download_resume(
        payload: dict = Body(...),
        user: User = Depends(get_current_user),
):
    text = payload.get("resume")
    fmt = payload.get("format", "pdf").lower()

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="No resume text provided.")

    filename = f"{user.email}_resume.{fmt}" if user and user.email else f"resume.{fmt}"

    if fmt == "pdf":
        file_bytes = generate_pdf(text)
        media_type = "application/pdf"
    elif fmt == "docx":
        file_bytes = generate_docx(text)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose pdf or docx.")

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
