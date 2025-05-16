from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ai_agents.agent_flow import CareerAgentFlow
from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.q_generator.tool import generate_interview_questions
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume
from utils.resume.pdf_exporter import text_to_pdf_bytes
from utils.system.temp_storage_manager import save_temp_file, clean_old_files
import fitz  # PyMuPDF for PDF parsing

app = FastAPI(title="Career AI Dev Agent Sandbox")

# Auto-clean up old temp files
clean_old_files()

# =====================
# Pydantic Request Models
# =====================

class ResumeAndJD(BaseModel):
    resume: str
    jd: str
    role: str = "Software Engineer"
    company: str = "Sample Company"

class AnswerInput(BaseModel):
    answer: str
    jd: str

class ResumeInput(BaseModel):
    resume: str

# =====================
# Agent Routes
# =====================

@app.post("/tailor/")
def tailor(data: ResumeAndJD):
    tailored = tailor_resume(data.resume, data.jd)
    pdf_bytes = text_to_pdf_bytes(tailored)
    save_temp_file(pdf_bytes, role=data.role, company=data.company, file_type="resume")
    return {"tailored_resume": tailored}

@app.post("/match/")
def match(data: ResumeAndJD):
    return {"match_report": match_resume_to_jd(data.resume, data.jd)}

@app.post("/generate-questions/")
def generate_questions(data: ResumeAndJD):
    return {"questions": generate_interview_questions(data.resume, data.jd)}

@app.post("/evaluate/")
def evaluate(data: AnswerInput):
    return {"feedback": evaluate_answer(data.answer, data.jd)}

@app.post("/parse/")
def parse(data: ResumeInput):
    return {"parsed_resume": parse_resume(data.resume)}

@app.post("/parse-pdf/")
def parse_pdf(file: UploadFile = File(...)):
    pdf = fitz.open(stream=file.file.read(), filetype="pdf")
    full_text = "".join(page.get_text() for page in pdf)
    return {"parsed_resume": parse_resume(full_text)}

@app.post("/optimize/")
def optimize_pipeline(data: ResumeAndJD):
    results = CareerAgentFlow.full_pipeline(data.resume, data.jd)
    resume_pdf = text_to_pdf_bytes(results["tailored_resume"])
    save_temp_file(resume_pdf, role=data.role, company=data.company, file_type="resume")

    cover_letter = f"""Dear {data.company},

{results['tailored_resume'].splitlines()[0]}

Best regards,  
[Your Name]"""
    cl_pdf = text_to_pdf_bytes(cover_letter)
    save_temp_file(cl_pdf, role=data.role, company=data.company, file_type="cover_letter")

    return {
        **results,
        "cover_letter": cover_letter
    }
