from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.q_generator.tool import generate_interview_questions
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume
from utils.temp_storage_manager import save_temp_file, clean_old_files
from utils.pdf_exporter import text_to_pdf_bytes
import fitz  # For /parse-pdf/

app = FastAPI(title="Career AI Agent API", version="1.0")

# 🧹 Cleanup old files on startup
clean_old_files()

# ======================
# 📦 Pydantic Models
# ======================
class ResumeAndJD(BaseModel):
    resume: str
    jd: str
    role: str = "Generic"
    company: str = "Unknown"

class AnswerInput(BaseModel):
    answer: str
    jd: str

class ResumeInput(BaseModel):
    resume: str

# ======================
# 🎯 Individual Endpoints
# ======================

@app.post("/tailor/")
def tailor(data: ResumeAndJD):
    result = tailor_resume(data.resume, data.jd)
    pdf_bytes = text_to_pdf_bytes(result)
    save_temp_file(pdf_bytes, role=data.role, company=data.company, file_type="resume")
    return result

@app.post("/match/")
def match(data: ResumeAndJD):
    return match_resume_to_jd(data.resume, data.jd)

@app.post("/generate-questions/")
def generate_questions(data: ResumeAndJD):
    return generate_interview_questions(data.resume, data.jd)

@app.post("/evaluate/")
def evaluate(data: AnswerInput):
    return evaluate_answer(data.answer, data.jd)

@app.post("/parse/")
def parse(data: ResumeInput):
    return parse_resume(data.resume)

@app.post("/parse-pdf/")
def parse_pdf(file: UploadFile = File(...)):
    pdf = fitz.open(stream=file.file.read(), filetype="pdf")
    full_text = "".join(page.get_text() for page in pdf)
    return parse_resume(full_text)

# ======================
# 🚀 Advanced Endpoint
# ======================

@app.post("/optimize/")
def optimize_pipeline(data: ResumeAndJD):
    # 1. Tailor
    tailored = tailor_resume(data.resume, data.jd)
    tailored_pdf = text_to_pdf_bytes(tailored)
    save_temp_file(tailored_pdf, role=data.role, company=data.company, file_type="resume")

    # 2. Match
    match_report = match_resume_to_jd(tailored, data.jd)

    # 3. Questions
    questions = generate_interview_questions(tailored, data.jd)

    # 4. Cover Letter (could use similar prompt structure)
    cover_letter = f"Dear {data.company},\n\n{tailored.splitlines()[0]}\n\nBest,\n[Your Name]"
    cl_pdf = text_to_pdf_bytes(cover_letter)
    save_temp_file(cl_pdf, role=data.role, company=data.company, file_type="cover_letter")

    return {
        "tailored_resume": tailored,
        "match_report": match_report,
        "interview_questions": questions,
        "cover_letter": cover_letter
    }

@app.post("/cover_letter/")
def generate_cover_letter(data: ResumeAndJD):
    # For now, simulate a basic cover letter
    cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for the {data.role} role at {data.company}. 
With experience in areas like those outlined in your job description, I believe I can contribute immediately.

Highlights:
- {data.resume[:200]}...

I look forward to discussing how I can add value to your team!

Sincerely,  
[Your Name]
"""
    return cover_letter
