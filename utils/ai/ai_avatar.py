import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

# === Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DID_API_KEY = os.getenv("D_ID_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
MODEL_ID = "eleven_monolingual_v1"

openai.api_key = OPENAI_API_KEY

# === Global memory context ===
conversation_history = [
    {"role": "system",
     "content": "You are a friendly AI interviewer. Ask questions naturally and follow up based on user replies."}
]


# === Generate Follow-up Question ===
def ask_follow_up(user_response=None):
    if user_response:
        conversation_history.append({"role": "user", "content": user_response})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=150
        )
        reply = response["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Error generating follow-up: {str(e)}"


# === Transcribe Audio with Deepgram ===
def transcribe_audio(audio_file):
    try:
        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            files={"file": audio_file}
        )
        return response.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get(
            "transcript", "")
    except Exception as e:
        return f"Transcription error: {str(e)}"


# === Convert Text to Speech ===
def text_to_speech(text, voice_id=ELEVEN_VOICE_ID, stability=0.5, similarity_boost=0.75, save_as=None):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        audio = response.content

        if save_as:
            with open(save_as, "wb") as f:
                f.write(audio)

        return audio

    except requests.exceptions.RequestException as e:
        print("❌ ElevenLabs Error:", e)
        return None


# === Generate AI Avatar Video with D-ID ===
def generate_avatar_video(audio_bytes, script_text):
    try:
        response = requests.post(
            "https://api.d-id.com/talks",
            headers={
                "Authorization": f"Bearer {DID_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "script": {
                    "type": "text",
                    "provider": {"type": "elevenlabs", "voice_id": ELEVEN_VOICE_ID},
                    "input": script_text
                },
                "source_url": "https://models.d-id.com/amy",
                "config": {"fluent": True, "pad_audio": 0.3}
            }
        )
        return response.json().get("result_url")
    except Exception as e:
        return f"D-ID generation error: {str(e)}"
