import openai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# === API Keys ===
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
D_ID_API_KEY = os.getenv("D_ID_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Default voice

# === Core Interview Generator ===
def generate_question_and_response(round_type="HR") -> dict:
    """
    Generate an interview question and model answer, then convert to voice + avatar.

    Args:
        round_type (str): HR or Technical

    Returns:
        dict: {question, answer, voice_url, video_url}
    """
    try:
        prompt = f"Generate a realistic {round_type} interview question and an ideal sample answer."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content

        # Split the GPT response into question/answer
        if "Answer:" in content:
            question, answer = content.split("Answer:", 1)
        else:
            question = "Generated question not formatted correctly."
            answer = content

        question = question.strip()
        answer = answer.strip()

        voice_url = generate_elevenlabs_audio(answer)
        video_url = generate_did_avatar_video(answer)

        return {
            "question": question,
            "answer": answer,
            "voice_url": voice_url,
            "video_url": video_url
        }

    except Exception as e:
        return {
            "error": f"❌ Failed to generate interview response: {str(e)}"
        }


# === ElevenLabs Text-to-Speech ===
def generate_elevenlabs_audio(text: str) -> str:
    """
    Convert answer text to audio using ElevenLabs.

    Returns:
        str: Local path to saved audio file (static)
    """
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        audio_path = "flask_app/static/audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)

        return "/static/audio.mp3"

    except Exception as e:
        print("❌ ElevenLabs error:", e)
        return ""


# === D-ID Avatar Video Generation ===
def generate_did_avatar_video(text: str) -> str:
    """
    Generate a video avatar using D-ID API.

    Returns:
        str: D-ID stream URL (playable video)
    """
    try:
        headers = {
            "Authorization": f"Bearer {D_ID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "script": {
                "type": "text",
                "provider": {
                    "type": "elevenlabs",
                    "voice_id": ELEVENLABS_VOICE_ID
                },
                "input": text
            },
            "source_url": "https://create.d-id.com/avatars/amy",  # Replace with your avatar if needed
            "config": {
                "fluent": True,
                "pad_audio": 0.3
            }
        }

        response = requests.post("https://api.d-id.com/talks", headers=headers, json=payload)
        response.raise_for_status()
        talk_id = response.json().get("id")

        return f"https://api.d-id.com/talks/{talk_id}/stream"

    except Exception as e:
        print("❌ D-ID avatar error:", e)
        return ""
