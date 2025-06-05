from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.resume.extract_text import extract_text_from_file
from ai_agents.resume_parser.tool import parse_resume

router = APIRouter()

@router.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save file to temp location
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        # Extract text from PDF/DOCX
        text = extract_text_from_file(open(temp_path, "rb"), file.filename)
        parsed = parse_resume(text)
        return {"parsed": parsed, "raw": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
