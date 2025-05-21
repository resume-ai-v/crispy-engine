# ✅ ai_agents/job_explainer/tool.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_job_match(resume: str, jd: str) -> str:
    prompt = f"""
    You're an AI career coach. Here's a candidate's resume:
    {resume}

    And here's a job description:
    {jd}

    Explain why this job is a good match for the candidate, including skill alignment, role relevance, and improvement tips.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ Job match explanation failed:", e)
        return "AI could not generate a match explanation."
