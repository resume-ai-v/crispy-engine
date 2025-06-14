import os
import requests
import time
import logging
import base64

from fastapi import APIRouter, HTTPException, Body, Depends
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
    resume: str = ""
    jd: str = ""
    round: str = "hr"  # 'coding', 'system-design', 'hr'

# --- Generate Custom GPT-powered Interview Question ---
def generate_gpt_question(resume, jd, round_type):
    """Generate an interview question using GPT, tailored to the resume, JD, and round."""
    try:
        openai.api_key = OPENAI_API_KEY
        system = "You are a world-class interviewer. Your job is to ask ONE tough and relevant interview question for the specified round. Only output the question, not the answer."
        role_hint = {
            "coding": "coding round (data structures/algorithms)",
            "system-design": "system design round (architecture, scalability, tradeoffs)",
            "hr": "behavioral round (culture fit, teamwork, values, leadership)",
        }
        user = (
            f"Resume:\n{resume}\n\nJob Description:\n{jd}\n\n"
            f"Interview Round: {round_type} ({role_hint.get(round_type, 'general')})\n"
            f"Ask a single relevant interview question for this candidate."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=80,
            temperature=0.6,
        )
        question = response.choices[0].message.content.strip().replace("\n", " ")
        # Avoid trailing "Answer:" etc.
        question = question.split("Answer:")[0].strip()
        return question
    except Exception as e:
        logging.error(f"GPT interview question error: {e}")
        return {
            "coding": "Can you walk me through how you would solve a classic array or string problem in code?",
            "system-design": "How would you design a scalable URL shortening service like bit.ly?",
            "hr": "Tell me about a challenging project you've worked on and what you learned.",
        }.get(round_type, "Tell me about yourself.")

# --- ElevenLabs Audio Generation ---
def generate_elevenlabs_audio(text: str) -> str:
    """
    Generates TTS audio using ElevenLabs and returns the audio file as a data URL (base64-encoded MP3).
    """
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        raise HTTPException(status_code=500, detail="Missing ElevenLabs credentials.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
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
    try:
        audio_resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if audio_resp.status_code != 200:
            logging.error(f"ElevenLabs audio error: {audio_resp.text}")
            raise Exception(audio_resp.text)
        # Save as base64 data URL for direct use in <audio>
        audio_b64 = base64.b64encode(audio_resp.content).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_b64}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ElevenLabs audio: {str(e)}")

# --- D-ID Video Generation with ElevenLabs Audio ---
def generate_did_video(text: str) -> str:
    """
    Generates a video using D-ID's API and ElevenLabs, with logging for debugging.
    Returns the video URL, or raises HTTPException on error.
    """
    if not D_ID_API_KEY or not D_ID_AVATAR_ID or not ELEVENLABS_VOICE_ID:
        logging.error("❌ D-ID or ElevenLabs credentials missing. Set all API keys and avatar/voice IDs.")
        raise HTTPException(status_code=500, detail="D-ID or ElevenLabs credentials missing on server.")

    encoded_api_key = base64.b64encode(D_ID_API_KEY.encode("utf-8")).decode("utf-8")
    create_url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Basic {encoded_api_key}",
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
        "avatar_id": D_ID_AVATAR_ID,
        "config": {"fluent": "false", "pad_audio": "0.0"}
    }

    try:
        logging.info(f"[D-ID] Sending video generation request (Avatar: {D_ID_AVATAR_ID}, Voice: {ELEVENLABS_VOICE_ID})")
        create_response = requests.post(create_url, headers=headers, json=payload, timeout=30)
        logging.info(f"[D-ID] Status: {create_response.status_code}, Response: {create_response.text}")
        create_response.raise_for_status()
        talk_id = create_response.json().get("id")
        if not talk_id:
            raise HTTPException(status_code=500, detail="No talk_id returned from D-ID API.")
    except Exception as e:
        error_details = create_response.text if 'create_response' in locals() else str(e)
        logging.error(f"❌ [D-ID video creation failed] {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to create D-ID video: {error_details}")

    # --- Poll for the video result ---
    get_url = f"https://api.d-id.com/talks/{talk_id}"
    for _ in range(30):  # Poll up to 5 minutes (30 * 10s)
        try:
            get_response = requests.get(get_url, headers=headers, timeout=30)
            logging.info(f"[D-ID Poll] Status: {get_response.status_code}, Response: {get_response.text}")
            get_response.raise_for_status()
            result = get_response.json()
            if result.get("status") == "done":
                video_url = result.get("result_url")
                if video_url:
                    logging.info(f"[D-ID] Video generation complete: {video_url}")
                    return video_url
                else:
                    raise HTTPException(status_code=500, detail="No result_url in D-ID response.")
            elif result.get("status") == "error":
                error_details = result.get('error', 'Unknown D-ID error')
                logging.error(f"[D-ID] Video generation error: {error_details}")
                raise HTTPException(status_code=500, detail=f"D-ID error: {error_details}")
            time.sleep(10)
        except Exception as e:
            error_details = get_response.text if 'get_response' in locals() else str(e)
            logging.error(f"❌ [D-ID Polling error] {error_details}")
            raise HTTPException(status_code=500, detail=f"Error polling D-ID: {error_details}")

    logging.error("[D-ID] Video generation timed out.")
    raise HTTPException(status_code=504, detail="D-ID video generation timed out.")

# ========== Main Interview Start Endpoint ==========

@router.post("/start-interview")
def start_interview(
    data: InterviewInput,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
):
    """
    Starts an AI avatar interview and returns GPT-generated question, video_url, and audio_url.
    """
    try:
        round_type = data.round if data.round in {"coding", "system-design", "hr"} else "hr"
        question = generate_gpt_question(data.resume, data.jd, round_type)
        script_for_avatar = f"Let me ask you an interview question. {question}"

        # Generate audio (for instant playback)
        audio_url = generate_elevenlabs_audio(script_for_avatar)
        # Generate video (async for user experience: play audio, show "Video generating...", then show video)
        video_url = generate_did_video(script_for_avatar)

        return {
            "question": question,
            "video_url": video_url,
            "audio_url": audio_url,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in start_interview: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
