from fastapi import FastAPI, UploadFile, File, Request, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os

from ai_agents.resume_tailor.tool import tailor_resume
from utils.resume.pdf_exporter import text_to_pdf_bytes
from utils.system.temp_storage_manager import save_temp_file, load_temp_file
from utils.system.notify_user import notify_missing_fields
from utils.resume.extract_text import extract_text_from_file
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume
from jobs.scrape_job import scrape_job_posting

# Load env variables
load_dotenv()

app = FastAPI(title="Career AI Dev API")

# ✅ Routers
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

app.include_router(resume_router)
app.include_router(feedback_router)
app.include_router(jobs_router)
app.include_router(interview_router)
app.include_router(apply_router)

# ✅ MODELS
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
    role: str = "Job"
    company: str = "Company"

# ✅ ROOT
@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

# ✅ CORE ENDPOINTS
@app.post("/match")
def match(data: ResumeAndJD):
    return {"match_score": match_resume_to_jd(data.resume, data.jd)}

@app.post("/parse-resume")
def parse_resume_text(data: ResumeAndJD):
    return {"parsed": parse_resume(data.resume)}

@app.post("/parse-upload")
def parse_resume_upload(file: UploadFile = File(...)):
    content = extract_text_from_file(file.file, file.filename)
    return {"parsed": parse_resume(content)}

@app.post("/evaluate")
def evaluate_answer_route(data: AnswerInput):
    return {"feedback": evaluate_answer(data.answer, data.jd)}

@app.get("/scrape")
def scrape(url: str):
    jd, role, company = scrape_job_posting(url)
    return {"jd": jd, "role": role, "company": company}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"/tmp/career_ai_vault/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="application/pdf")
    return {"error": "File not found."}

@app.post("/apply-smart")
def apply_job(data: ApplicationData):
    tailored_resume = tailor_resume(data.resume, data.jd)
    pdf = text_to_pdf_bytes(tailored_resume)
    filename = save_temp_file(pdf, data.role, data.company, "resume")
    missing = ["email"]
    notify_missing_fields(data.phone_number, data.role, missing)
    return {"status": "resume tailored & user notified", "file": filename, "missing": missing}

# ✅ NEW: Onboarding Endpoint
@app.post("/onboarding")
async def save_onboarding(request: Request, data: dict = Body(...)):
    request.session["onboarding"] = data
    return {"status": "success", "message": "Onboarding data saved in session"}
