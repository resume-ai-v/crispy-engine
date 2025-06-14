import os
import io
import re
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
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
    except Exception as e:
        logging.error(f"Semantic score error (LLM fallback): {e}")
        return compute_ats_score(resume, jd)

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
        logging.info(f"[Upload] Resume uploaded for {user.email}")
        return {"resume_text": text}
    except Exception as e:
        logging.error(f"Error in upload_resume: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@router.post("/tailor-resume")
async def tailor_resume(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    # Read from payload, fallback to user.resume_text (which must exist)
    resume_text = (payload.get("resume") or getattr(user, "resume_text", "") or "").strip()
    jd_text = (payload.get("jd") or "").strip()
    role = payload.get("role", "Generic")
    company = payload.get("company", "Unknown")

    logging.info(f"[Tailor Resume] User: {getattr(user, 'email', 'unknown')} | Resume present: {bool(resume_text)} | JD present: {bool(jd_text)}")

    if not resume_text:
        raise HTTPException(status_code=400, detail="Missing resume text. Upload a resume first or provide it in the request.")
    if not jd_text:
        raise HTTPException(status_code=400, detail="Missing job description text. Please provide JD.")

    max_len = 6000
    if len(resume_text) > max_len or len(jd_text) > max_len:
        raise HTTPException(
            status_code=400,
            detail=f"Resume or JD too long (>{max_len} chars). Please shorten and try again."
        )

    ats_score_orig = compute_ats_score(resume_text, jd_text)
    semantic_score_orig = compute_semantic_score(resume_text, jd_text)
    original_match = round((ats_score_orig + semantic_score_orig) / 2)

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OpenAI API Key. Contact support.")
        client = openai.OpenAI(api_key=api_key)
        prompt = (
            "You are an expert resume editor. Given the following resume and job description, "
            f"tailor the resume so it maximizes the candidate's chance of getting this {role} job at {company}. "
            "Use relevant keywords, highlight key skills, and make the resume ATS-friendly. "
            "Return only the improved resume text (no extra comments).\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}\n\nTailored Resume:"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional ATS resume optimization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.4,
        )
        tailored_resume = response.choices[0].message.content.strip()
        if not tailored_resume or len(tailored_resume) < 100:
            logging.error("OpenAI returned empty or too short tailored resume.")
            raise HTTPException(status_code=500, detail="OpenAI did not return a valid tailored resume.")
    except Exception as e:
        logging.error(f"Unexpected error in OpenAI tailoring: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    ats_score_tailored = compute_ats_score(tailored_resume, jd_text)
    semantic_score_tailored = compute_semantic_score(tailored_resume, jd_text)
    tailored_match = round((ats_score_tailored + semantic_score_tailored) / 2)

    # Persist tailored resume if needed (optional)
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

def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.set_font("Arial", size=12)
    except:
        pdf.set_font("helvetica", size=12)
    for line in text.split('\n'):
        safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 10, safe_line)
    try:
        pdf_bytes = pdf.output(dest="S").encode("latin1")
        return pdf_bytes
    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

def generate_docx(text: str) -> bytes:
    doc = Document()
    for para in text.split('\n\n'):
        clean_para = para.replace('\x00', '').strip()
        doc.add_paragraph(clean_para)
    file_stream = io.BytesIO()
    try:
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.read()
    except Exception as e:
        logging.error(f"DOCX generation error: {e}")
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {e}")

@router.post("/download-resume")
async def download_resume(
    payload: dict = Body(...),
    user: User = Depends(get_current_user),
):
    text = (payload.get("resume") or getattr(user, "resume_text", "") or "").strip()
    fmt = payload.get("format", "pdf").lower()
    filename = "AI_Resume." + fmt

    if not text:
        raise HTTPException(status_code=400, detail="No resume text provided.")

    if fmt == "pdf":
        pdf_bytes = generate_pdf(text)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    elif fmt == "docx":
        docx_bytes = generate_docx(text)
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(docx_bytes))
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose pdf or docx.")
