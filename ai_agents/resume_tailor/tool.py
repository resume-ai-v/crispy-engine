import os
import openai
import re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment.")
client = openai.OpenAI(api_key=API_KEY)

def clean_match_summary(summary: str) -> str:
    summary = summary.strip()
    summary = re.sub(r'(%\s*)+$', '', summary)
    summary = re.sub(r'(%+)(\s*Match)', r'%\2', summary)
    return summary

def tailor_resume(resume_text: str, jd_text: str) -> dict:
    # Step 1: Original Match
    match_prompt = f"""
You are an expert hiring manager.
Given a candidate’s résumé and a job description, evaluate how well the résumé fits the job.
Return your answer in this EXACT format (no extra text):

  "<X>% Match – <brief explanation>"

Where:
  • <X> is an integer from 0 to 100 (no decimals), followed by the percent sign.
  • <brief explanation> is 1–2 sentences referencing specific keywords from the résumé or JD.

Candidate Résumé:
{resume_text}

Job Description:
{jd_text}

Return exactly one line (no extra commentary).
"""
    try:
        resp_orig = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": match_prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        original_match = clean_match_summary(resp_orig.choices[0].message.content.strip())
    except Exception:
        original_match = "0% Match – Unable to compute original match."

    # Step 2: Tailor Resume
    tailor_prompt = f"""
You are a professional résumé writer and hiring expert. Given the candidate’s résumé
and the job description below, rewrite (tailor) the résumé so that it highlights only
the information most relevant to this specific job. Be sure to:

  • Emphasize the candidate’s skills, keywords, and accomplishments that match or
    exceed the JD requirements.
  • Keep formatting simple—just plain text, bullet points, headings, etc.
  • Do not invent new jobs or dates; only reframe and reorder existing experience
    and skills. If something is not relevant, omit or downplay it.

Candidate’s Original Résumé:
{resume_text}

Job Description:
{jd_text}

Return only the **tailored résumé text** (no extra commentary).
"""
    try:
        resp_tailor = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": tailor_prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        tailored_resume = resp_tailor.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(
            "❌ Something went wrong while tailoring the résumé. "
            "Please check your API key, prompt template, or token limits."
        )

    # Step 3: After Tailoring Match
    match_again_prompt = f"""
You are an expert hiring manager. Given this **tailored résumé** and the same job description,
evaluate how well the résumé now fits the job. Return exactly:

  "<X>% Match – <brief explanation>"

Résumé:
{tailored_resume}

Job Description:
{jd_text}

Return only one line.
"""
    try:
        resp_tailored_match = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": match_again_prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        tailored_match = clean_match_summary(resp_tailored_match.choices[0].message.content.strip())
    except Exception:
        tailored_match = "0% Match – Unable to compute tailored match."

    return {
        "tailored_resume": tailored_resume,
        "original_match": original_match,
        "tailored_match": tailored_match,
    }
