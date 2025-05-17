import streamlit as st
import requests

st.set_page_config(page_title="Career AI Assistant", layout="wide")

API_BASE = "http://localhost:8000"

st.title("🎯 Career AI Assistant")

# -------------------------------------------
# 🧠 STEP 1: Onboarding Preferences
# -------------------------------------------
st.header("1️⃣ Job Preferences")

col1, col2, col3 = st.columns(3)
with col1:
    role = st.text_input("Target Role", value="Data Analyst")
with col2:
    location = st.text_input("Preferred Location", value="Remote")
with col3:
    visa = st.selectbox("H1B Sponsorship Needed?", options=["Yes", "No"])

keyword = st.text_input("Search Jobs With Keyword", value="Data Analyst")

if st.button("🔍 Fetch Jobs"):
    with st.spinner("Fetching jobs..."):
        try:
            res = requests.get(f"{API_BASE}/jobs", params={"keyword": keyword})
            jobs = res.json()
            if jobs:
                st.success("✅ Jobs fetched")
                for i, job in enumerate(jobs[:10]):
                    with st.expander(f"{job['title']} at {job['company']}"):
                        st.markdown(f"📍 {job['location']} | 🕒 {job['type']} | 🏢 H1B: {job.get('h1b_sponsor', 'Unknown')}")
                        st.markdown(job["jd_text"][:400] + "...")
                        if st.button("🎯 Apply With AI", key=f"apply_{i}"):
                            st.session_state["selected_job"] = job
                            st.session_state["step"] = "resume_upload"

        except Exception as e:
            st.error(f"Failed to fetch jobs: {e}")

# -------------------------------------------
# 📄 STEP 2: Resume Upload + Tailoring
# -------------------------------------------
if st.session_state.get("step") == "resume_upload":
    st.header("2️⃣ Resume Upload")

    resume_text = st.text_area("Paste your Resume", height=300)
    job = st.session_state["selected_job"]

    if resume_text:
        if st.button("🔧 Tailor Resume"):
            with st.spinner("Tailoring resume..."):
                try:
                    res = requests.post(f"{API_BASE}/tailor/", json={
                        "resume": resume_text,
                        "jd": job["jd_text"],
                        "role": job["title"],
                        "company": job["company"]
                    })
                    tailored_resume = res.text
                    st.session_state["tailored_resume"] = tailored_resume
                    st.session_state["step"] = "confirm_apply"
                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------------------------
# ✅ STEP 3: Confirm + Apply
# -------------------------------------------
if st.session_state.get("step") == "confirm_apply":
    st.header("3️⃣ Confirm + Apply")

    st.subheader("🎯 Tailored Resume")
    st.code(st.session_state["tailored_resume"], language="text")

    user_info = {
        "name": st.text_input("Your Full Name", value="Jane Doe"),
        "email": st.text_input("Email", value="jane@example.com"),
        "phone": st.text_input("Phone", value="+1234567890")
    }

    if st.button("🚀 Apply Now"):
        try:
            res = requests.post(f"{API_BASE}/apply-to-job", json={
                "resume_text": st.session_state["tailored_resume"],
                "jd_text": st.session_state["selected_job"]["jd_text"],
                "job_url": st.session_state["selected_job"]["apply_url"],
                "job_title": st.session_state["selected_job"]["title"],
                "user_info": user_info
            })
            response = res.json()
            st.success("✅ Application Submitted or User Notified")
            st.json(response)
        except Exception as e:
            st.error(f"Error: {e}")
