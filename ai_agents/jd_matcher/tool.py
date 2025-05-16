import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# For production OpenAI fallback (optional):
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def match_resume_to_jd(resume_text: str, jd_text: str) -> str:
    """
    Uses Together API (Mistral) to analyze the match between resume and job description.
    Replace with OpenAI GPT-4 for enhanced reasoning when moving to production.
    """
    try:
        with open("prompts/jd_match_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template \
            .replace("{{resume_text}}", resume_text) \
            .replace("{{jd_text}}", jd_text)

        # ======= TOGETHER API CALL (Current - Free Tier) =======
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
        # =======================================================

        # ======= OPENAI FALLBACK (Optional for Later) =======
        # import openai
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.3,
        #     max_tokens=800
        # )
        # return response.choices[0].message.content
        # =====================================================

    except Exception as e:
        print("❌ JD Match Agent Error:", e)
        return "Something went wrong while matching resume to JD."
