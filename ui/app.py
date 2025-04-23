import streamlit as st
import requests
import os
import sys
from PyPDF2 import PdfReader
import docx

# Fix path for jobs module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from jobs.job_fetcher import get_jobs_from_jsearch

st.set_page_config(page_title="🎯 Career AI Agent", layout="wide")
st.title("🎯 Career AI Agent – Pro Tester")

# ========== FILE UPLOAD & TEXT EXTRACTION ==========

st.sidebar.title("📎 Upload Resume & JD (Optional)")

def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

uploaded_resume = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx"], key="resume_file")
uploaded_jd = st.sidebar.file_uploader("Upload Job Description", type=["pdf", "docx"], key="jd_file")

uploaded_resume_text = extract_text(uploaded_resume) if uploaded_resume else ""
uploaded_jd_text = extract_text(uploaded_jd) if uploaded_jd else ""

# ========== TEXT INPUTS ==========

st.subheader("📄 Resume & Job Description")
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste your Resume", uploaded_resume_text, height=250, key="resume_text")
with col2:
    jd = st.text_area("Paste Job Description", uploaded_jd_text, height=250, key="jd_text")

# ========== AGENT ACTIONS ==========

if resume and jd:
    col1, col2, col3 = st.columns(3)

    if col1.button("🔁 Tailor Resume", key="tailor_button"):
        try:
            res = requests.post("http://localhost:8000/tailor/", json={"resume": resume, "jd": jd})
            st.subheader("🎯 Tailored Resume")
            st.code(res.text.strip(), language="markdown")
        except Exception as e:
            st.error(f"❌ Tailor Agent Failed: {e}")

    if col2.button("📊 Match Resume", key="match_button"):
        try:
            res = requests.post("http://localhost:8000/match/", json={"resume": resume, "jd": jd})
            st.subheader("📍 JD Match Report")
            st.code(res.text.strip())
        except Exception as e:
            st.error(f"❌ Match Agent Failed: {e}")

    if col3.button("🧠 Generate Interview Questions", key="question_button"):
        try:
            res = requests.post("http://localhost:8000/generate-questions/", json={"resume": resume, "jd": jd})
            st.subheader("🎤 Interview Questions")
            st.code(res.text.strip())
        except Exception as e:
            st.error(f"❌ Question Agent Failed: {e}")

# ========== JOB SEARCH ==========
st.divider()
st.subheader("🌍 Explore Jobs (via JSearch + Local Fallback)")
keyword = st.text_input("Search jobs by title", "data analyst", key="job_search_input")

if st.button("🔍 Get Jobs", key="get_jobs_button"):
    try:
        jobs = get_jobs_from_jsearch(keyword)
        if not jobs:
            st.warning("⚠️ No jobs found.")
        else:
            for job in jobs:
                st.markdown(f"""
**{job.get('job_title')}**  
🏢 {job.get('employer_name')}  
📍 {job.get('job_city', 'N/A')}  
🔗 [Apply here]({job.get('job_apply_link')})  
---
""")
    except Exception as e:
        st.error(f"❌ Failed to fetch jobs: {e}")
