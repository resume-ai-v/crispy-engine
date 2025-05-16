import os
from dotenv import load_dotenv
import requests

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# Optional OpenAI fallback:
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def tailor_resume(resume_text: str, jd_text: str) -> str:
    """
    Uses Together API to rewrite the resume so that it aligns better with the given job description.
    """
    try:
        # Load tailored prompt template
        with open("prompts/resume_tailor_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template \
            .replace("{{resume_text}}", resume_text) \
            .replace("{{jd_text}}", jd_text)

        # ======= TOGETHER API (Current - Free Tier) =======
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/Mistral-7B-Instruct-v0.2",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1024
            }
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
        # ===================================================

        # ======= OPENAI FALLBACK (Uncomment When Needed) =======
        # import openai
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.7,
        #     max_tokens=1024
        # )
        # return response.choices[0].message.content
        # ========================================================

    except Exception as e:
        print("❌ Resume Tailor Agent Error:", e)
        return "Something went wrong while tailoring the resume."
