# -------------------------------------
# ✅ FILE: api/resume_api.py
# -------------------------------------

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from docx import Document
from io import BytesIO
from dotenv import load_dotenv
import openai
import os

from utils.system.temp_storage_manager import load_temp_file

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Single APIRouter declaration
router = APIRouter()

# Request model for resume generation
class ResumeRequest(BaseModel):
    name: str
    job_description: str

# ✅ Endpoint: Generate Resume (.docx) from AI
@router.post("/generate-resume")
def generate_resume(data: ResumeRequest):
    try:
        prompt = f"""
        Create a professional resume for {data.name}, tailored to this job description:
        {data.job_description}
        Include Summary, Skills, Experience, and Education sections.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content

        # Generate .docx resume
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

# ✅ Endpoint: Download any resume (PDF or DOCX)
@router.get("/download/{filename}")
def download_resume(filename: str):
    file_path = f"/tmp/career_ai_vault/{filename}"
    if os.path.exists(file_path):
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if filename.endswith(".docx")
            else "application/pdf"
        )
        return FileResponse(path=file_path, filename=filename, media_type=media_type)

    return {"error": "File not found."}
