# ----------------------------------
# ✅ FILE: api/apply_api.py
# ----------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai_agents.resume_tailor.tool import tailor_resume
from utils.resume.pdf_exporter import text_to_pdf_bytes
from utils.system.temp_storage_manager import save_temp_file
from jobs.form_autofiller import autofill_application_form
from utils.system.notify_user import notify_missing_fields

router = APIRouter()

class ApplyJobRequest(BaseModel):
    resume_text: str
    jd_text: str
    job_url: str
    job_title: str
    user_info: dict  # expects {"name": str, "email": str, "phone": str}

@router.post("/api/apply-to-job")
def apply_to_job(data: ApplyJobRequest):
    try:
        # Step 1: Tailor resume using JD
        tailored_resume = tailor_resume(data.resume_text, data.jd_text)

        # Step 2: Export to PDF in memory
        pdf_bytes = text_to_pdf_bytes(tailored_resume)
        temp_url = save_temp_file(pdf_bytes, file_type="resume")  # path or URL to temp PDF

        # Step 3: Launch autofill browser agent
        missing_fields = autofill_application_form(data.job_url, tailored_resume, data.user_info)

        # Step 4: If any fields missing, notify user (via WhatsApp/SMS)
        if missing_fields:
            notify_missing_fields(
                phone_number=data.user_info.get("phone"),
                job_title=data.job_title,
                missing_fields=missing_fields
            )

        return {
            "status": "applied" if not missing_fields else "pending_user_input",
            "resume_download_url": temp_url,
            "missing_fields": missing_fields
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

