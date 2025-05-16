import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# For future OpenAI use:
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def parse_resume(resume_text: str) -> str:
    """
    Uses Together API (Mistral-7B) to extract structured information from resume text.
    Replace with OpenAI GPT-4 when moving to production.
    """
    try:
        # Load prompt template
        with open("prompts/parser_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{{resume_text}}", resume_text)

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
        # =======================================================

        # ======= OPENAI FALLBACK (Uncomment When Ready) =======
        # import openai
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.3,
        #     max_tokens=800
        # )
        # result = response.choices[0].message.content
        # =======================================================

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Resume Parser Error:", e)
        return "Something went wrong while parsing the resume."
