import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.temp_storage_manager import clean_old_files, get_temp_files, delete_temp_file, load_temp_file

import os
import requests
import streamlit as st
from PyPDF2 import PdfReader
import docx
from datetime import datetime
from utils.temp_storage_manager import clean_old_files, get_temp_files, delete_temp_file, load_temp_file
from jobs.job_fetcher import get_jobs_from_jsearch

st.set_page_config(page_title="🎯 Career AI Agent", layout="wide")
st.title("🎯 Career AI Agent – Pro Platform")

# ========== File Text Extractor ==========
def extract_text(file):
    if file.name.endswith(".pdf"):
        return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif file.name.endswith(".docx"):
        return "\n".join([para.text for para in docx.Document(file).paragraphs])
    return ""

# ========== Uploads ==========
st.sidebar.title("📎 Upload Resume & JD")
uploaded_resume = st.sidebar.file_uploader("Resume (.pdf or .docx)", type=["pdf", "docx"])
uploaded_jd = st.sidebar.file_uploader("Job Description (.pdf or .docx)", type=["pdf", "docx"])

resume_text = extract_text(uploaded_resume) if uploaded_resume else ""
jd_text = extract_text(uploaded_jd) if uploaded_jd else ""

# ========== Resume & JD Input ==========
st.subheader("📄 Resume & Job Description")
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste your Resume", resume_text, height=250)
with col2:
    jd = st.text_area("Paste Job Description", jd_text, height=250)

role = st.text_input("🎯 Role", value="Data Analyst")
company = st.text_input("🏢 Company", value="Google")

# ========== Action Buttons ==========
if resume and jd:
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🔁 Tailor Resume"):
        res = requests.post("http://localhost:8000/tailor/", json={
            "resume": resume, "jd": jd, "role": role, "company": company
        })
        st.success("✅ Tailored Resume Generated")
        st.code(res.text)

    if c2.button("📄 Generate Cover Letter"):
        res = requests.post("http://localhost:8000/cover_letter/", json={
            "resume": resume, "jd": jd, "role": role, "company": company
        })
        st.success("✅ Cover Letter Generated")
        st.code(res.text)

    if c3.button("📊 Match Resume"):
        res = requests.post("http://localhost:8000/match/", json={"resume": resume, "jd": jd})
        st.success("📍 JD Match Score")
        st.code(res.text)

    if c4.button("🧠 Generate Questions"):
        res = requests.post("http://localhost:8000/generate-questions/", json={"resume": resume, "jd": jd})
        st.success("🎤 Interview Questions")
        st.code(res.text)

# ========== Resume Vault ==========
st.divider()
st.subheader("📁 Resume Vault (Temporary)")

files = get_temp_files()
if files:
    for file in files:
        name = file["name"]
        mod = file["modified"]
        st.markdown(f"📄 **{name}** — _Last Modified_: {mod}")
        with open(file["path"], "rb") as f:
            st.download_button("⬇️ Download", data=f, file_name=name)
        st.button(f"🗑️ Delete {name}", key=name, on_click=delete_temp_file, args=(name,))
else:
    st.info("No resumes saved yet.")

st.button("🧹 Cleanup Old Files", on_click=clean_old_files)

# ========== Job Search ==========
st.divider()
st.subheader("🌍 Explore Jobs (via JSearch + Match Score)")

keyword = st.text_input("Search job title", value="Data Analyst")
if st.button("🔍 Search Jobs"):
    jobs = get_jobs_from_jsearch(keyword)
    if jobs:
        for job in jobs:
            st.markdown(f"""
**{job['job_title']}**  
🏢 {job['employer_name']} | 📍 {job.get('job_city', 'Remote')}  
🔗 [Apply Now]({job['job_apply_link']})  
🧮 Match %: _Run via JD Matcher if resume provided_  
---
""")
    else:
        st.warning("No jobs found or API error.")
