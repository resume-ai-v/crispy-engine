import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def match_resume_to_jd(resume_text: str, jd_text: str) -> str:
    try:
        with open("prompts/jd_match_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{{resume_text}}", resume_text).replace("{{jd_text}}", jd_text)

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/Mistral-7B-Instruct-v0.2",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 800
            }
        )

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ JD Match Agent Error:", e)
        return "Something went wrong with JD Matcher."
