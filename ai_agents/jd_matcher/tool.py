import os
import openai
import re
from dotenv import load_dotenv

load_dotenv()

# --- Start of Changes ---

# Initialize the client with the API key
# This is the new required way for openai > 1.0.0
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment.")
client = openai.OpenAI(api_key=API_KEY)

# --- End of Changes ---

def clean_match_summary(summary: str) -> str:
    """
    Ensures the returned string is in format 'XX% Match – <explanation>',
    and removes any stray trailing percent signs (from GPT hallucinations).
    """
    summary = summary.strip()
    # Remove any trailing % not part of the XX% Match pattern
    summary = re.sub(r'(%\s*)+$', '', summary)
    # Remove double percent if exists
    summary = re.sub(r'(%+)(\s*Match)', r'%\2', summary)
    return summary

def match_resume_to_jd(resume: str, jd_text: str) -> str:
    prompt = f"""
You are a seasoned hiring manager with expertise in software engineering roles.
Compare the candidate’s résumé below against the job description.

Return your evaluation in this EXACT format (no extra text):
"<X>% Match – <brief explanation>"

Where:
  • <X> is an integer from 0 to 100, followed by the percent sign.
  • <brief explanation> is one or two sentences calling out specific keywords or skill gaps.

Candidate Résumé:
{resume}

Job Description:
{jd_text}

Return only the one‐line match string.
"""
    try:
        # --- Start of Changes ---
        # Use the client to create the chat completion
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        result = response.choices[0].message.content.strip()
        # --- End of Changes ---
        return clean_match_summary(result)
    except Exception as e:
        # It's good practice to log the actual error
        print(f"An error occurred while matching resume to JD: {e}")
        return "0% Match – Unable to compute match at this time."