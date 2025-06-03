from fastapi import APIRouter, HTTPException, Body
from ai_agents.feedback_agent.tool import evaluate_answer

router = APIRouter()

@router.post("/api/evaluate")
def evaluate_answer_route(data: dict = Body(...)):
    try:
        if not data.get('answer') or not data.get('jd'):
            raise HTTPException(status_code=422, detail="Missing answer or JD in request body.")
        feedback = evaluate_answer(data['answer'], data['jd'])
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
