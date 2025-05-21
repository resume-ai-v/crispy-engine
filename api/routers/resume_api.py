# ----------------------------------
# ✅ FILE: api/routers/resume_api.py
# ----------------------------------

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from utils.resume.extract_text import extract_text_from_file
from utils.resume.pdf_exporter import text_to_pdf_bytes
from docx import Document
from io import BytesIO
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# -----------------------------
# 1️⃣ Upload and Store Resume in Session
# -----------------------------
@router.post("/upload-resume")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    try:
        content = extract_text_from_file(file.file, file.filename)
        request.session["resume"] = content
        return {"message": "Resume uploaded and stored in session.", "parsed_resume": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 2️⃣ Retrieve Stored Resume
# -----------------------------
@router.get("/get-resume")
async def get_resume(request: Request):
    resume = request.session.get("resume")
    if not resume:
        return {"message": "No resume found in session."}
    return {"resume": resume}


# -----------------------------
# 3️⃣ AI Resume Generator
# -----------------------------
class ResumeRequest(BaseModel):
    name: str
    job_description: str

@router.post("/generate-resume")
async def generate_resume(request: Request, data: ResumeRequest):
    try:
        prompt = f"""
        Create a professional resume for {data.name}, tailored to this job description:
        {data.job_description}
        Include Summary, Skills, Experience, and Education sections.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content
        request.session["resume"] = content  # Store generated resume in session

        # Generate DOCX
        doc = Document()
        doc.add_heading(f"{data.name} - AI Resume", 0)
        for line in content.split("\n"):
            if line.strip():
                doc.add_paragraph(line.strip())

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={data.name.replace(' ', '_')}_resume.docx"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 4️⃣ Download Resume (DOCX / PDF)
# -----------------------------
class FinalResume(BaseModel):
    resume_text: str
    file_name: str = "final_resume"

@router.post("/download-docx")
def download_docx(data: FinalResume):
    doc = Document()
    for line in data.resume_text.split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={data.file_name}.docx"}
    )

@router.post("/download-pdf")
def download_pdf(data: FinalResume):
    pdf_bytes = text_to_pdf_bytes(data.resume_text)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={data.file_name}.pdf"}
    )
