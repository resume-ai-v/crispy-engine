# ai_agents/resume_tailor/tool.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def tailor_resume(resume_text: str, jd_text: str) -> str:
    try:
        with open("prompts/resume_tailor_prompt.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template \
            .replace("{{resume_text}}", resume_text) \
            .replace("{{jd_text}}", jd_text)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ Resume Tailor Agent Error:", e)
        return "Something went wrong while tailoring the resume."
