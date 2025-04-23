from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.q_generator.tool import generate_interview_questions
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume

import fitz  # PyMuPDF for PDF reading

app = FastAPI(title="Career AI Agent API", version="1.0")


class ResumeAndJD(BaseModel):
    resume: str
    jd: str

class AnswerInput(BaseModel):
    answer: str
    jd: str

class ResumeInput(BaseModel):
    resume: str


@app.post("/tailor/")
def tailor(data: ResumeAndJD):
    return tailor_resume(data.resume, data.jd)


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
    full_text = ""
    for page in pdf:
        full_text += page.get_text()
    return parse_resume(full_text)
