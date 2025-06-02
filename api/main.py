from fastapi import FastAPI, UploadFile, File, Request, Body, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import io

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize FastAPI app
app = FastAPI(title="Career AI Dev API")

# --------------- CORS (LOCAL + PROD AUTO-SWITCH) ---------------
ENV = os.getenv("ENVIRONMENT", "production")  # set ENVIRONMENT=local for local dev

if ENV == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://launch-hire.vercel.app",
            "https://launch-hire-vijays-projects-10840c84.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# ---------------------------------------------------------------

# ✅ Enable Session support
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

# ✅ Include API routers
from api.routers.auth_api import router as auth_router
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(feedback_router)
app.include_router(jobs_router)
app.include_router(interview_router)
app.include_router(apply_router)

# ✅ AI tools and helpers
from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume
from jobs.scrape_job import scrape_job_posting
from utils.resume.pdf_exporter import text_to_pdf_bytes
from utils.resume.docx_exporter import text_to_docx_bytes
from utils.system.temp_storage_manager import save_temp_file
from utils.system.notify_user import notify_missing_fields
from utils.resume.extract_text import extract_text_from_file
from api.playwright.auto_apply import apply_to_job_site

# ✅ Pydantic input models
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

# ✅ Health check
@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

# ✅ Resume & JD Match
@app.post("/match")
def match(data: ResumeAndJD):
    try:
        score = match_resume_to_jd(data.resume, data.jd)
        return {"match_score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Resume Text Parsing
@app.post("/parse-resume")
def parse_resume_text(data: ResumeAndJD):
    try:
        return {"parsed": parse_resume(data.resume)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ File Upload Parsing
@app.post("/parse-upload")
def parse_resume_upload(file: UploadFile = File(...)):
    try:
        content = extract_text_from_file(file.file, file.filename)
        return {"parsed": parse_resume(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Answer Evaluation
@app.post("/api/evaluate")
def evaluate_answer_route(data: AnswerInput):
    try:
        if not data.answer or not data.jd:
            raise HTTPException(status_code=422, detail="Missing answer or JD in request body.")
        feedback = evaluate_answer(data.answer, data.jd)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ JD Scraper
@app.get("/scrape")
def scrape(url: str):
    try:
        jd, role, company = scrape_job_posting(url)
        return {"jd": jd, "role": role, "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Resume PDF Download (for old direct file serving)
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"/tmp/career_ai_vault/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="application/pdf")
    return {"error": "File not found."}

# ✅ Smart Job Application
@app.post("/apply-smart")
def apply_job(data: ApplicationData):
    try:
        tailored_resume = tailor_resume(data.resume, data.jd)
        pdf = text_to_pdf_bytes(tailored_resume)
        filename = save_temp_file(pdf, data.role, data.company, "resume")
        notify_missing_fields(data.phone_number, data.role, ["email"])  # Optional
        return {
            "status": "resume tailored & user notified",
            "file": filename,
            "missing": ["email"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Onboarding session
@app.post("/onboarding")
async def save_onboarding(request: Request, data: dict = Body(...)):
    try:
        request.session["onboarding"] = data
        return {"status": "success", "message": "Onboarding data saved in session"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- Tailor Resume Endpoint ----
class TailorInput(BaseModel):
    resume: str
    jd: str
    role: str = "Generic"
    company: str = "Unknown"

@app.post("/tailor-resume")
def tailor_resume_route(data: TailorInput):
    result = tailor_resume(data.resume, data.jd)
    def parse_score(s):
        try:
            return int(str(s).split('%')[0].strip())
        except:
            return 0
    return {
        "tailored_resume": result["tailored_resume"],
        "original_match": parse_score(result["original_match"]),
        "tailored_match": parse_score(result["tailored_match"]),
        "original_match_text": result["original_match"],
        "tailored_match_text": result["tailored_match"],
    }

# ---- Download Resume Endpoint (PDF/DOCX) ----
class DownloadInput(BaseModel):
    resume: str
    format: str = "pdf"

@app.post("/download-resume")
def download_resume(data: DownloadInput):
    if data.format == "pdf":
        pdf_bytes = text_to_pdf_bytes(data.resume)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=resume.pdf"}
        )
    elif data.format == "docx":
        docx_bytes = text_to_docx_bytes(data.resume)
        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=resume.docx"}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

# ---- Auto-Apply via Playwright ----
class AutoApplyInput(BaseModel):
    resume: str
    job_url: str
    job_title: str
    company: str

@app.post("/auto-apply")
def auto_apply_route(data: AutoApplyInput):
    result = apply_to_job_site(data.resume, data.job_url, data.job_title, data.company)
    return {"status": "Auto-apply triggered", "result": result}

# ✅ Serve static files (audio, resume, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Database init (leave as-is if you already have migrations)
from api.extensions.db import Base, engine
from api.models.user import User
Base.metadata.create_all(bind=engine)
