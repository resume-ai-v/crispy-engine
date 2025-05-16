from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai, os, requests, random
from ai_agents.q_generator.tool import generate_interview_questions
from data.interview_questions import preset_rounds

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
D_ID_API_KEY = os.getenv("D_ID_API_KEY")

router = APIRouter()

class InterviewInput(BaseModel):
    resume: str
    jd: str
    round: str = "HR"

@router.post("/start-interview")
def start_interview(data: InterviewInput):
    try:
        # 🎯 Try to generate dynamic AI-based questions
        try:
            questions = generate_interview_questions(data.resume, data.jd, data.round)
        except:
            questions = random.choice(preset_rounds.get(data.round, []))

        # 🧠 Follow-up Q&A prompt
        q_prompt = f"As an interviewer, here's the question: {questions}. Now provide the best model answer."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": q_prompt}]
        )
        answer = response.choices[0].message.content

        audio_url = generate_elevenlabs_audio(answer.strip())
        video_url = generate_did_video(answer.strip())

        return {
            "question": questions.strip(),
            "answer": answer.strip(),
            "audio_url": audio_url,
            "video_url": video_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_elevenlabs_audio(text):
    try:
        voice_id = "YOUR_VOICE_ID"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, headers=headers, json=payload)
        with open("static/audio.mp3", "wb") as f:
            f.write(response.content)
        return "/static/audio.mp3"
    except Exception as e:
        print("❌ ElevenLabs Error:", e)
        return None


def generate_did_video(text):
    try:
        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Bearer {D_ID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "script": {"type": "text", "input": text},
            "source_url": "https://create.d-id.com/avatars/YOUR_AVATAR_ID"
        }
        response = requests.post(url, headers=headers, json=payload)
        talk_id = response.json().get("id", "")
        return f"https://api.d-id.com/talks/{talk_id}/stream"
    except Exception as e:
        print("❌ D-ID Error:", e)
        return None
