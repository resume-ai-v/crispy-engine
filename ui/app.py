# ----------------------------------
# ✅ FILE: ui/app.py (Streamlit Dev UI)
# ----------------------------------

import os
import sys

from utils.resume.pdf_exporter import text_to_pdf_bytes

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
from PyPDF2 import PdfReader
import docx
from utils.system.temp_storage_manager import clean_old_files, get_temp_files, delete_temp_file
from jobs.job_fetcher import fetch_jobs_from_api

st.set_page_config(page_title="🎯 Career AI Agent", layout="wide")
st.title("🎯 Career AI Agent – Dev Panel")

# ========== Text Extraction ==========
def extract_text(file):
    if file.name.endswith(".pdf"):
        return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif file.name.endswith(".docx"):
        return "\n".join([para.text for para in docx.Document(file).paragraphs])
    return ""

# ========== Upload Resume and JD ==========
st.sidebar.title("📎 Upload Resume & JD")
uploaded_resume = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx"])
uploaded_jd = st.sidebar.file_uploader("Upload JD", type=["pdf", "docx"])

resume_text = extract_text(uploaded_resume) if uploaded_resume else ""
jd_text = extract_text(uploaded_jd) if uploaded_jd else ""

# ========== Input Panels ==========
st.subheader("📄 Resume & Job Description")
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste Resume", resume_text, height=250)
with col2:
    jd = st.text_area("Paste JD", jd_text, height=250)

role = st.text_input("🎯 Role", value="Data Scientist")
company = st.text_input("🏢 Company", value="OpenAI")

# ========== AI Actions ==========
if resume and jd:
    c1, c2, c3, c4, c5 = st.columns(5)

    if c1.button("🔁 Tailor Resume"):
        with st.spinner("Tailoring resume..."):
            try:
                res = requests.post("http://localhost:8000/tailor/", json={"resume": resume, "jd": jd, "role": role, "company": company})
                st.success("✅ Tailored Resume")
                st.code(res.text)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if c2.button("📄 Cover Letter"):
        with st.spinner("Generating cover letter..."):
            res = requests.post("http://localhost:8000/cover_letter/", json={"resume": resume, "jd": jd, "role": role, "company": company})
            st.success("📬 Cover Letter")
            st.code(res.text)

    if c3.button("📊 JD Match"):
        with st.spinner("Scoring resume..."):
            res = requests.post("http://localhost:8000/match/", json={"resume": resume, "jd": jd})
            st.success("📌 Match Score")
            st.code(res.text)

    if c4.button("🎤 Interview Questions"):
        with st.spinner("Generating interview questions..."):
            res = requests.post("http://localhost:8000/generate-questions/", json={"resume": resume, "jd": jd})
            st.success("💬 Interview Questions")
            st.code(res.text)

    if c5.button("🚀 Apply to Job"):
        with st.spinner("Tailoring + Autofill in progress..."):
            res = requests.post("http://localhost:8000/apply-to-job", json={
                "resume_text": resume,
                "jd_text": jd,
                "job_url": "https://example.com/jobform",
                "job_title": role,
                "user_info": {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "phone": "+1234567890"
                }
            })
            st.success("📤 Applied or User Notified")
            st.json(res.json())

# ========== Resume Vault ==========
st.divider()
st.subheader("📁 Resume Vault")
files = get_temp_files()
for file in files:
    st.markdown(f"📄 **{file['name']}** — _Last Modified_: {file['modified']}")
    with open(file["path"], "rb") as f:
        st.download_button("⬇️ Download", f, file_name=file['name'])
    st.button(f"🗑️ Delete {file['name']}", key=file['name'], on_click=delete_temp_file, args=(file['name'],))
st.button("🧹 Cleanup Old Files", on_click=clean_old_files)

# ========== Job Browser ==========
st.divider()
st.subheader("🌍 Explore Jobs (from Remotive API)")

if st.button("📡 Fetch Jobs"):
    jobs = fetch_jobs_from_api()
    if resume:
        for job in jobs[:5]:
            try:
                match = requests.post("http://localhost:8000/match/", json={"resume": resume, "jd": job["jd_text"]})
                score = match.text
            except:
                score = "error"
            st.markdown(f"""
**{job['title']}** at *{job['company']}*  
📍 {job['location']} | 🕒 {job['type']} | H1B: {job['h1b_sponsor']}  
🧮 Match Score: {score}  
---
""")

# Inside st.download_button() usage area:
st.info("⚠️ Files downloaded from this app will expire from your system in 48 hours. They are also backed up for 60 days on our secure server.")

# Example usage:
file_bytes = text_to_pdf_bytes(resume)
st.download_button("⬇️ Download Resume", data=file_bytes, file_name="resume_ai.pdf")

# View My Vault tab:
if st.sidebar.button("📁 View My Vault"):
    from utils.system.temp_storage_manager import get_temp_files, load_temp_file, delete_temp_file
    st.subheader("📁 Your Resume Vault (48hr storage)")
    files = get_temp_files()
    if files:
        for file in files:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{file['name']}** — _Last Modified_: {file['modified']}")
                st.download_button("⬇️ Download", load_temp_file(file['name']), file_name=file['name'])
            with col2:
                st.button("🗑️", key=file['name'], on_click=delete_temp_file, args=(file['name'],))
    else:
        st.info("No resumes saved yet.")

