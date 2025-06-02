# ai_agents/job_explainer/tool.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# ─── Load environment and initialize OpenAI client ──────────────────────────────
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment.")
client = OpenAI(api_key=api_key)


def explain_job_match(resume: str, jd_text: str) -> str:
    """
    Returns a 1–2 sentence explanation plus a match percentage
    for why the candidate’s résumé fits (or does not fit) the JD.
    Format: "<X>% Match – <brief explanation>"
    """
    prompt = f"""
You are a senior recruiter. Evaluate this résumé against the job description 
and return exactly:

  "<X>% Match – <brief explanation>"

Résumé:
{resume}

Job Description:
{jd_text}

Return only the single line match string.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "0% Match – Unable to generate explanation."
