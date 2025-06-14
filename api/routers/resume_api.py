import os
import io
import re
import openai
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from utils.resume.extract_text import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User
from docx import Document
from fpdf import FPDF

router = APIRouter()

# --- Utility functions for scoring ---

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

def compute_semantic_score(resume: str, jd: str) -> int:
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = (
            f"Resume:\n{resume}\n\nJob Description:\n{jd}\n\n"
            "Score from 0 to 100 how well this resume fits the job description, "
            "considering skills, responsibilities, and experience. Only output the number."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8,
            temperature=0.1,
        )
        content = response["choices"][0]["message"]["content"]
        score = int("".join(filter(str.isdigit, content)))
        return min(score, 100)
    except Exception as e:
        print(f"Semantic score error (LLM fallback): {e}")
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
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        text = extract_text_from_file(open(temp_path, "rb"), file.filename)
        user.resume_text = text
        db.add(user)
        await db.commit()
        onboarding = user.onboarding_data or {}
        onboarding["resume_text"] = text
        user.onboarding_data = onboarding
        db.add(user)
        await db.commit()
        return {"resume_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Tailor resume endpoint ---

@router.post("/tailor-resume")
async def tailor_resume(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    """
    Tailors a user's resume to a specific job description using OpenAI GPT.
    Returns tailored resume and both original and tailored match scores.
    """
    resume_text = payload.get("resume") or user.resume_text
    jd_text = payload.get("jd")
    role = payload.get("role", "Generic")
    company = payload.get("company", "Unknown")
    if not resume_text or not jd_text:
        raise HTTPException(status_code=400, detail="Missing resume or job description.")

    # Score original resume
    ats_score_orig = compute_ats_score(resume_text, jd_text)
    semantic_score_orig = compute_semantic_score(resume_text, jd_text)
    original_match = round((ats_score_orig + semantic_score_orig) / 2)

    # Tailor using OpenAI GPT
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = (
            "You are an expert resume editor. Given the following resume and job description, "
            f"tailor the resume so it maximizes the candidate's chance of getting this {role} job at {company}. "
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

    # Score tailored resume
    ats_score_tailored = compute_ats_score(tailored_resume, jd_text)
    semantic_score_tailored = compute_semantic_score(tailored_resume, jd_text)
    tailored_match = round((ats_score_tailored + semantic_score_tailored) / 2)

    # Optionally update user's tailored resume for later use
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

# --- PDF and DOCX Download ---

def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes

def generate_docx(text: str) -> bytes:
    doc = Document()
    for para in text.split('\n\n'):
        doc.add_paragraph(para)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()

@router.post("/download-resume")
async def download_resume(
    payload: dict = Body(...),
    user: User = Depends(get_current_user),
):
    text = payload.get("resume") or user.resume_text
    fmt = payload.get("format", "pdf").lower()
    filename = "AI_Resume." + fmt

    if not text:
        raise HTTPException(status_code=400, detail="No resume text provided.")

    if fmt == "pdf":
        pdf_bytes = generate_pdf(text)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})
    elif fmt == "docx":
        docx_bytes = generate_docx(text)
        return StreamingResponse(io.BytesIO(docx_bytes), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose pdf or docx.")
