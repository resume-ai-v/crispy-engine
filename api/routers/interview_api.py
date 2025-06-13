import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
import time

load_dotenv()

router = APIRouter()

D_ID_API_KEY = os.getenv("D_ID_API_KEY")
D_ID_AVATAR_ID = os.getenv("D_ID_AVATAR_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

import logging

def generate_did_video(text: str) -> str:
    """
    Generates a video from text using D-ID's API and ElevenLabs voice, with full logging for debugging.
    """
    if not D_ID_API_KEY or not D_ID_AVATAR_ID or not ELEVENLABS_VOICE_ID:
        logging.error("❌ D-ID or ElevenLabs credentials missing. Check your .env file.")
        return None

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

    # --- LOG the outgoing request (hide API key) ---
    logging.info(f"[D-ID] Sending video generation request. Avatar: {D_ID_AVATAR_ID}, Voice: {ELEVENLABS_VOICE_ID}, Text: {text}")

    try:
        create_response = requests.post(create_url, headers=headers, json=payload, timeout=30)
        logging.info(f"[D-ID] Status: {create_response.status_code}, Response: {create_response.text}")

        create_response.raise_for_status()
        talk_id = create_response.json().get("id")
    except Exception as e:
        error_details = create_response.text if 'create_response' in locals() else str(e)
        logging.error(f"❌ [D-ID video creation failed] {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to create D-ID video: {error_details}")

    # Poll for result
    get_url = f"https://api.d-id.com/talks/{talk_id}"

    for _ in range(30):
        try:
            get_response = requests.get(get_url, headers=headers, timeout=30)
            logging.info(f"[D-ID Poll] Status: {get_response.status_code}, Response: {get_response.text}")

            get_response.raise_for_status()
            result = get_response.json()

            if result.get("status") == "done":
                video_url = result.get("result_url")
                logging.info(f"[D-ID] Video generation complete: {video_url}")
                return video_url
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
    raise HTTPException(status_code=504, detail="Video generation timed out.")


class InterviewInput(BaseModel):
    resume: str
    jd: str
    round: str = "hr"

QUESTION_MAP = {
    "coding": "Can you walk me through how you would solve a classic array or string problem in code?",
    "system-design": "How would you design a scalable URL shortening service like bit.ly?",
    "hr": "Tell me about a challenging project you've worked on and what you learned.",
}

@router.post("/start-interview")
def start_interview(data: InterviewInput):
    try:
        question = QUESTION_MAP.get(data.round, QUESTION_MAP["hr"])
        script_for_avatar = f"Let me ask you an interview question. {question}"
        video_url = generate_did_video(script_for_avatar)
        return {
            "question": question,
            "video_url": video_url,
            "audio_url": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in start_interview: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
