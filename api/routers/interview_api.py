import os
import requests
import time
import logging
import base64

from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Start of Changes ---
# Use the synchronous Session for this router, as all helper functions are synchronous
from sqlalchemy.orm import Session
from api.extensions.db import get_db
# --- End of Changes ---

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

# --- Start of Changes ---
# Removed 'resume' from the input model. We will get it from the logged-in user.
class InterviewInput(BaseModel):
    jd: str
    round: str = "hr"
# --- End of Changes ---

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
        raise HTTPException(status_code=500, detail="Missing ElevenLabs credentials.")

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
        raise HTTPException(status_code=500, detail=f"Failed to generate ElevenLabs audio: {error_detail}")


def generate_did_video(text: str) -> str:
    if not D_ID_API_KEY or not D_ID_AVATAR_ID or not ELEVENLABS_VOICE_ID:
        logging.error("❌ D-ID or ElevenLabs credentials missing. Set all API keys and avatar/voice IDs.")
        raise HTTPException(status_code=500, detail="D-ID or ElevenLabs credentials missing on server.")

    # D-ID now uses "Bearer <API_KEY>" for authorization
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
                "voice_id": ELEVENLABS_VOICE_ID,
                "voice_config": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
        },
        "source_url": D_ID_AVATAR_ID, # Assuming D_ID_AVATAR_ID is a URL to a still image
        "config": {"fluent": "false", "pad_audio": "0.0"}
    }

    try:
        logging.info(f"[D-ID] Sending video generation request (Source: {D_ID_AVATAR_ID}, Voice: {ELEVENLABS_VOICE_ID})")
        create_response = requests.post(create_url, headers=headers, json=payload, timeout=30)
        create_response.raise_for_status()
        talk_id = create_response.json().get("id")
        if not talk_id:
            raise HTTPException(status_code=500, detail="No talk_id returned from D-ID API.")
    except requests.exceptions.RequestException as e:
        error_details = e.response.text if e.response else str(e)
        logging.error(f"❌ [D-ID video creation failed] {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to create D-ID video: {error_details}")

    get_url = f"https://api.d-id.com/talks/{talk_id}"
    get_headers = {"Authorization": f"Bearer {D_ID_API_KEY}"}

    for _ in range(30): # Poll for 5 minutes (30 * 10s)
        try:
            get_response = requests.get(get_url, headers=get_headers, timeout=30)
            get_response.raise_for_status()
            result = get_response.json()
            if result.get("status") == "done":
                video_url = result.get("result_url")
                if video_url:
                    logging.info(f"[D-ID] Video generation complete: {video_url}")
                    return video_url
                else:
                    raise HTTPException(status_code=500, detail="No result_url in D-ID response.")
            elif result.get("status") in ["error", "rejected"]:
                error_details = result.get('result', 'Unknown D-ID error')
                logging.error(f"[D-ID] Video generation error: {error_details}")
                raise HTTPException(status_code=500, detail=f"D-ID error: {error_details}")
            time.sleep(10)
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else str(e)
            logging.error(f"❌ [D-ID Polling error] {error_details}")
            raise HTTPException(status_code=500, detail=f"Error polling D-ID: {error_details}")

    logging.error("[D-ID] Video generation timed out.")
    raise HTTPException(status_code=504, detail="D-ID video generation timed out.")


@router.post("/start-interview")
# --- Start of Changes ---
# Changed to async def to work with get_current_user and async db session if needed,
# but using a synchronous DB session as the helper functions are not async.
def start_interview(
    data: InterviewInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
# --- End of Changes ---
    try:
        if not user or not getattr(user, "id", None):
            logging.error("Unauthorized: No user/session found.")
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing user session.")

        # --- Start of Changes ---
        # Fetch resume securely from the database instead of the request body
        if not user.resume_text:
            raise HTTPException(status_code=400, detail="Resume not found for the user. Please upload a resume first.")
        resume_text = user.resume_text
        # --- End of Changes ---

        round_type = data.round if data.round in {"coding", "system-design", "hr"} else "hr"

        # --- Start of Changes ---
        # Pass the resume from the database to the question generator
        question = generate_gpt_question(resume_text, data.jd, round_type)
        # --- End of Changes ---

        script_for_avatar = f"Let me ask you an interview question. {question}"

        # Note: D-ID video generation can be very slow. Consider running this as a background task.
        audio_url = generate_elevenlabs_audio(script_for_avatar)
        video_url = generate_did_video(script_for_avatar)

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
