import os
import requests
import time
import logging
import base64

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from api.extensions.db import get_async_db
from api.routers.auth_api import get_current_user
from api.models.user import User
import openai

load_dotenv()
router = APIRouter()

D_ID_API_KEY = os.getenv("D_ID_API_KEY")
D_ID_AVATAR_ID = os.getenv("D_ID_AVATAR_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

class InterviewInput(BaseModel):
    jd: str
    round: str = "hr"

def generate_gpt_question(resume, jd, round_type):
    try:
        if not OPENAI_API_KEY:
            logging.error("Missing OpenAI API Key.")
            raise Exception("Missing OpenAI API Key")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        system = "You are a world-class interviewer. Your job is to ask ONE tough and relevant interview question for the specified round. Only output the question, not the answer."
        role_hint = {
            "coding": "coding round (data structures/algorithms)",
            "system-design": "system design round (architecture, scalability, tradeoffs)",
            "hr": "behavioral round (culture fit, teamwork, values, leadership)",
        }
        user_prompt = (
            f"Resume:\n{resume}\n\nJob Description:\n{jd}\n\n"
            f"Interview Round: {round_type} ({role_hint.get(round_type, 'general')})\n"
            f"Ask a single relevant interview question for this candidate."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=80,
            temperature=0.6,
        )
        question = response.choices[0].message.content.strip().replace("\n", " ")
        question = question.split("Answer:")[0].strip()
        return question
    except openai.RateLimitError as e:
        logging.error(f"OpenAI Rate Limit Error (Quota Exceeded) during question generation: {e}")
        raise HTTPException(status_code=429,
                            detail="AI interview question service is temporarily unavailable (OpenAI quota exceeded or too many requests). Please try again later.")
    except Exception as e:
        logging.error(f"GPT interview question error: {e}")
        return {
            "coding": "Can you walk me through how you would solve a classic array or string problem in code?",
            "system-design": "How would you design a scalable URL shortening service like bit.ly?",
            "hr": "Tell me about a challenging project you've worked on and what you learned.",
        }.get(round_type, "Tell me about yourself.")

def generate_elevenlabs_audio(text: str) -> str:
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        logging.error("Missing ElevenLabs credentials.")
        raise HTTPException(status_code=500, detail="Missing ElevenLabs credentials on the server.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    try:
        audio_resp = requests.post(url, headers=headers, json=payload, timeout=30)
        audio_resp.raise_for_status()
        audio_b64 = base64.b64encode(audio_resp.content).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_b64}"
    except requests.exceptions.RequestException as e:
        error_detail = e.response.text if e.response else str(e)
        logging.error(f"ElevenLabs audio error: {error_detail}")
        if "detected_unusual_activity" in error_detail:
            raise HTTPException(status_code=403,
                                detail="Your ElevenLabs account has been flagged for unusual activity. Please check your account status.")
        # --- NEW: Handle 429 or service unavailable
        if "429" in error_detail or "quota" in error_detail.lower():
            raise HTTPException(
                status_code=429,
                detail="AI voice service is temporarily unavailable (ElevenLabs quota exceeded or too many requests). Please try again later."
            )
        raise HTTPException(status_code=500, detail=f"Failed to generate ElevenLabs audio: {error_detail}")

def generate_did_video(text: str) -> str:
    if not D_ID_API_KEY or not D_ID_AVATAR_ID or not ELEVENLABS_VOICE_ID:
        logging.error("❌ D-ID or ElevenLabs credentials missing.")
        raise HTTPException(status_code=500, detail="D-ID or ElevenLabs credentials missing on server.")

    create_url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Bearer {D_ID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "elevenlabs",
                "voice_id": ELEVENLABS_VOICE_ID
            }
        },
        "source_url": D_ID_AVATAR_ID,
        "config": {"fluent": "false", "pad_audio": "0.0"}
    }

    try:
        create_response = requests.post(create_url, headers=headers, json=payload, timeout=30)
        create_response.raise_for_status()
        talk_id = create_response.json().get("id")
        if not talk_id:
            raise HTTPException(status_code=500, detail="No talk_id returned from D-ID API.")
    except requests.exceptions.RequestException as e:
        error_details = e.response.text if e.response else str(e)
        logging.error(f"❌ [D-ID video creation failed] {error_details}")
        # --- NEW: Handle 429 or quota errors for D-ID as well
        if "429" in error_details or "quota" in error_details.lower():
            raise HTTPException(
                status_code=429,
                detail="AI avatar video service is temporarily unavailable (D-ID quota exceeded or too many requests). Please try again later."
            )
        raise HTTPException(status_code=500, detail=f"Failed to create D-ID video: {error_details}")

    get_url = f"https://api.d-id.com/talks/{talk_id}"
    get_headers = {"Authorization": f"Bearer {D_ID_API_KEY}"}

    for _ in range(30):
        try:
            get_response = requests.get(get_url, headers=get_headers, timeout=30)
            get_response.raise_for_status()
            result = get_response.json()
            if result.get("status") == "done":
                video_url = result.get("result_url")
                if video_url:
                    return video_url
                else:
                    raise HTTPException(status_code=500, detail="No result_url in D-ID response.")
            elif result.get("status") in ["error", "rejected"]:
                error_details = result.get('result', 'Unknown D-ID error')
                raise HTTPException(status_code=500, detail=f"D-ID error: {error_details}")
            time.sleep(10)
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            raise HTTPException(status_code=500, detail=f"Error polling D-ID: {error_details}")

    raise HTTPException(status_code=504, detail="D-ID video generation timed out.")

@router.post("/start-interview")
async def start_interview(
        data: InterviewInput,
        db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
):
    try:
        if not user or not getattr(user, "id", None):
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing user session.")

        if not user.resume_text:
            raise HTTPException(status_code=400, detail="Resume not found for the user. Please upload a resume first.")
        resume_text = user.resume_text

        round_type = data.round if data.round in {"coding", "system-design", "hr"} else "hr"

        question = generate_gpt_question(resume_text, data.jd, round_type)
        script_for_avatar = f"Let me ask you an interview question. {question}"

        # --- Key Change: wrap all downstream AI calls with specific error handling!
        try:
            audio_url = generate_elevenlabs_audio(script_for_avatar)
        except HTTPException as e:
            if e.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="AI voice service is temporarily unavailable (ElevenLabs quota exceeded or too many requests). Please try again later."
                )
            raise

        try:
            video_url = generate_did_video(script_for_avatar)
        except HTTPException as e:
            if e.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="AI avatar video service is temporarily unavailable (D-ID quota exceeded or too many requests). Please try again later."
                )
            raise

        return {
            "question": question,
            "video_url": video_url,
            "audio_url": audio_url,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in start_interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred.")
