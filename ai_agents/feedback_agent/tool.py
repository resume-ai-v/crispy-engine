import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# Optional OpenAI fallback:
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def evaluate_answer(user_answer: str, jd_text: str) -> str:
    """
    Uses Together API to provide feedback on a user's interview answer
    based on the job description.
    """
    try:
        with open("prompts/feedback_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template \
            .replace("{{user_answer}}", user_answer) \
            .replace("{{jd_text}}", jd_text)

        # ======= TOGETHER API (Free Tier - Current) =======
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/Mistral-7B-Instruct-v0.2",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6,
                "max_tokens": 800
            }
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
        # ===================================================

        # ======= OPENAI Fallback (GPT-4 - Optional) =======
        # import openai
        # openai.api_key = OPENAI_API_KEY
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.6,
        #     max_tokens=800
        # )
        # return response.choices[0].message.content
        # ==================================================

    except Exception as e:
        print("❌ Feedback Agent Error:", e)
        return "Something went wrong while evaluating the answer."
