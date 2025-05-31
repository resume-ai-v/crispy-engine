from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
import os
import base64
import requests

# ✅ Load .env from root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# ✅ Retrieve environment variables
D_ID_API_KEY = os.getenv("D_ID_API_KEY")  # Format: username:password
D_ID_AVATAR_ID = os.getenv("D_ID_AVATAR_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# ✅ Environment Debug Check
print("\n🔍 ENV CHECK")
print(f"D_ID_API_KEY: {'✅ Loaded' if D_ID_API_KEY else '❌ Missing'}")
print(f"D_ID_AVATAR_ID: {D_ID_AVATAR_ID}")
print(f"ELEVENLABS_API_KEY: {'✅ Loaded' if ELEVENLABS_API_KEY else '❌ Missing'}")
print(f"ELEVENLABS_VOICE_ID: {ELEVENLABS_VOICE_ID}")
print("-" * 40)

# ✅ FastAPI router
router = APIRouter()

# ✅ Request schema
class InterviewInput(BaseModel):
    resume: str
    jd: str
    round: str = "HR"

# ✅ Main interview route
@router.post("/api/start-interview")
def start_interview(data: InterviewInput):
    try:
        question = "Tell me about yourself."
        answer = "Sure! I'm a passionate AI developer with experience in Python, LLMs, and building full-stack AI tools..."

        audio_url = generate_elevenlabs_audio(answer)
        video_url = generate_did_video(answer)

        return {
            "question": question,
            "answer": answer,
            "audio_url": audio_url,
            "video_url": video_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ ElevenLabs Audio TTS
def generate_elevenlabs_audio(text: str) -> str:
    try:
        if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
            raise Exception("❌ ElevenLabs: Missing API key or voice ID")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        Path("static").mkdir(parents=True, exist_ok=True)
        filename = f"audio_{uuid4().hex}.mp3"
        filepath = f"static/{filename}"

        with open(filepath, "wb") as f:
            f.write(response.content)

        return f"/static/{filename}"
    except Exception as e:
        print("❌ ElevenLabs Audio Error:", e)
        return None


# ✅ D-ID Video Generation with Basic Auth & Avatar ID
def generate_did_video(text: str) -> str:
    try:
        if not D_ID_API_KEY or not D_ID_AVATAR_ID:
            raise Exception("❌ D-ID: Missing API key or avatar ID")

        encoded_key = base64.b64encode(D_ID_API_KEY.encode()).decode()

        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "script": {
                "type": "text",
                "input": text
            },
            "avatar_id": D_ID_AVATAR_ID,  # ✅ Use avatar_id not source_url
            "config": {
                "fluent": True,
                "pad_audio": 0.2
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        talk_id = response.json().get("id")
        if not talk_id:
            raise Exception("❌ D-ID API: No talk ID returned")

        return f"https://api.d-id.com/talks/{talk_id}/stream"
    except Exception as e:
        print("❌ D-ID Video Error:", e)
        return None
