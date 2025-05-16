from fastapi import FastAPI, UploadFile, File, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
from utils.resume.pdf_exporter import text_to_pdf_bytes
from utils.system.temp_storage_manager import save_temp_file, load_temp_file, get_temp_files
from utils.system.notify_user import notify_missing_fields
from utils.resume.extract_text import extract_text_from_file
from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.q_generator.tool import generate_interview_questions
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume
from utils.interview_utils import generate_question_and_response
from jobs.scrape_job import scrape_job_posting

import io

app = FastAPI(title="CareerAI Agent API")

# -----------------------------
# Models
# -----------------------------
class ResumeAndJD(BaseModel):
    resume: str
    jd: str
    role: str = "Generic"
    company: str = "Unknown"

class AnswerInput(BaseModel):
    answer: str
    jd: str

class ApplicationData(BaseModel):
    resume: str
    jd: str
    job_url: str
    phone_number: str
    user_name: str

# -----------------------------
# Resume Tailoring + Match
# -----------------------------
@app.post("/tailor")
def tailor(data: ResumeAndJD):
    result = tailor_resume(data.resume, data.jd)
    pdf_bytes = text_to_pdf_bytes(result)
    save_temp_file(pdf_bytes, data.role, data.company, "resume")
    return {"tailored_resume": result}

@app.post("/match")
def match(data: ResumeAndJD):
    return {"match_score": match_resume_to_jd(data.resume, data.jd)}


from api import feedback_api
app.include_router(feedback_api.router)


@app.post("/evaluate")
def evaluate_answer_route(data: AnswerInput):
    return {"feedback": evaluate_answer(data.answer, data.jd)}

# -----------------------------
# Cover Letter + Resume Parser
# -----------------------------
@app.post("/cover-letter")
def generate_cover_letter(data: ResumeAndJD):
    content = f"""
Dear {data.company},

I am writing to express my interest in the {data.role} role. With relevant skills that match your job description, I believe I’d be a great fit.

Highlights:
{data.resume[:250]}

Sincerely,
Your Candidate
"""
    pdf_bytes = text_to_pdf_bytes(content)
    save_temp_file(pdf_bytes, data.role, data.company, "cover_letter")
    return {"cover_letter": content}

@app.post("/parse-resume")
def parse_resume_text(data: ResumeAndJD):
    return {"parsed": parse_resume(data.resume)}

@app.post("/parse-upload")
def parse_resume_upload(file: UploadFile = File(...)):
    content = extract_text_from_file(file.file, file.filename)
    return {"parsed": parse_resume(content)}

# -----------------------------
# Avatar Interview API
# -----------------------------
@app.get("/generate-avatar-question")
def avatar_qna():
    return generate_question_and_response("Technical")

# -----------------------------
# Resume Downloader
# -----------------------------
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"/tmp/career_ai_vault/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="application/pdf")
    return {"error": "File not found."}

# -----------------------------
# Job Scraper Utility
# -----------------------------
@app.get("/scrape")
def scrape(url: str):
    jd, role, company = scrape_job_posting(url)
    return {"jd": jd, "role": role, "company": company}

# -----------------------------
# Intelligent Apply Flow
# -----------------------------
@app.post("/apply-smart")
def apply_job(data: ApplicationData):
    tailored_resume = tailor_resume(data.resume, data.jd)
    pdf = text_to_pdf_bytes(tailored_resume)
    filename = save_temp_file(pdf, data.role, data.company, "resume")
    missing = ["email"]  # Placeholder until autofill is built
    notify_missing_fields(data.phone_number, data.role, missing)
    return {"status": "resume tailored & user notified", "file": filename, "missing": missing}
