from fastapi import APIRouter, HTTPException, Body
from api.playwright.auto_apply import apply_to_job_site

router = APIRouter()

@router.post("/auto-apply")
def auto_apply_route(data: dict = Body(...)):
    try:
        result = apply_to_job_site(
            data['resume'],
            data['job_url'],
            data['job_title'],
            data['company']
        )
        return {"status": "Auto-apply triggered", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
