import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
import base64  # Ensure base64 is imported
import time

# Load .env from the project's root directory
load_dotenv()

router = APIRouter()

# --- Environment Variable Checks ---
D_ID_API_KEY = os.getenv("D_ID_API_KEY")
D_ID_AVATAR_ID = os.getenv("D_ID_AVATAR_ID")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")


def generate_did_video(text: str) -> str:
    """
    Generates a video from text using D-ID's API, correctly encoding the API key
    and waiting for the video generation to complete.
    """
    if not D_ID_API_KEY or not D_ID_AVATAR_ID:
        print("⚠️ D-ID credentials not found or incomplete in .env file. Skipping video generation.")
        return None

    # --- Correctly encode the 'email:password' style key to Base64 ---
    encoded_api_key = base64.b64encode(D_ID_API_KEY.encode("utf-8")).decode("utf-8")

    # --- Step 1: Create the video generation talk ---
    create_url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Basic {encoded_api_key}",  # Use the Base64 encoded key
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
        print("🚀 Starting D-ID video generation...")
        create_response = requests.post(create_url, headers=headers, json=payload, timeout=30)
        create_response.raise_for_status()
        talk_id = create_response.json().get("id")
        print(f"✅ D-ID talk created with ID: {talk_id}")
    except Exception as e:
        error_details = create_response.text if 'create_response' in locals() else str(e)
        print(f"❌ D-ID Video Creation Error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to create D-ID video: {error_details}")

    # --- Step 2: Poll for the result ---
    get_url = f"https://api.d-id.com/talks/{talk_id}"

    for i in range(30):  # Poll for up to 5 minutes
        try:
            print(f" polling for talk {talk_id} (Attempt {i + 1}/30)")
            get_response = requests.get(get_url, headers=headers, timeout=30)
            get_response.raise_for_status()
            result = get_response.json()

            if result.get("status") == "done":
                video_url = result.get("result_url")
                print(f"✅ D-ID video is ready: {video_url}")
                return video_url
            elif result.get("status") == "error":
                error_details = result.get('error', 'Unknown D-ID error')
                print(f"❌ D-ID video generation failed with error: {error_details}")
                raise HTTPException(status_code=500, detail=f"D-ID video generation failed: {error_details}")

            time.sleep(10)
        except Exception as e:
            error_details = get_response.text if 'get_response' in locals() else str(e)
            print(f"❌ D-ID polling error: {error_details}")
            raise HTTPException(status_code=500, detail=f"Error while checking video status: {error_details}")

    print("❌ D-ID video generation timed out after 5 minutes.")
    raise HTTPException(status_code=504, detail="Video generation timed out.")


class InterviewInput(BaseModel):
    resume: str
    jd: str
    round: str = "hr"


@router.post("/start-interview")
def start_interview(data: InterviewInput):
    try:
        question = "Tell me about a challenging project you've worked on."
        script_for_avatar = "Of course. Let me tell you about a challenging project I worked on recently."

        video_url = generate_did_video(script_for_avatar)

        return {
            "question": question,
            "video_url": video_url,
            "audio_url": None
        }
    except HTTPException as e:
        # Re-raise HTTPException to propagate the specific error and status code
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred in start_interview: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")