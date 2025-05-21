# api/feedback_api.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ai_agents.feedback_agent.tool import evaluate_answer
from utils.feedback_exporter import generate_feedback_pdf
from pydantic import BaseModel
import io

router = APIRouter()

class FeedbackRequest(BaseModel):
    answer: str
    jd: str
    user_name: str = "Candidate"

@router.post("/feedback-report")
def generate_feedback_report(data: FeedbackRequest):
    feedback = evaluate_answer(data.answer, data.jd)
    pdf_bytes = generate_feedback_pdf(feedback, user_name=data.user_name)

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                              headers={"Content-Disposition": f"attachment; filename=feedback_report.pdf"})
