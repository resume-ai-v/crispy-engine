# flask_app/app.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from utils.temp_storage_manager import save_temp_file, clean_old_files, get_temp_files, delete_temp_file
from utils.scrape_job import scrape_job_posting
from utils.extract_text import extract_text_from_file
from utils.job_fetcher import get_jobs_from_jsearch
from utils.pdf_exporter import text_to_pdf_bytes
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

# === Flask Setup ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "career_ai_secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# === Auth Setup ===
login_manager = LoginManager(app)
login_manager.login_view = "google.login"

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="home",
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# === User Model ===
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role_preference = db.Column(db.String(100))
    location_preference = db.Column(db.String(100))
    work_mode = db.Column(db.String(50))
    salary_expectation = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

API_URL = "http://localhost:8000"

# === ROUTES ===

@app.route("/", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("google.login"))

    resume_text = ""
    jd_text = ""
    result = ""
    resume = ""
    jd = ""
    role = ""
    company = ""

    if request.method == "POST":
        action = request.form.get("action")
        role = request.form.get("role") or "Generic"
        company = request.form.get("company") or "Unknown"

        resume_file = request.files.get("resume_file")
        if resume_file and resume_file.filename:
            content = resume_file.read()
            resume_text = extract_text_from_file(resume_file)
            save_temp_file(content, role, company, "resume")
            flash(f"✅ Uploaded Resume: {resume_file.filename}")

        jd_file = request.files.get("jd_file")
        jd_url = request.form.get("jd_url")
        if jd_file and jd_file.filename:
            content = jd_file.read()
            jd_text = extract_text_from_file(jd_file)
            flash(f"✅ Uploaded JD: {jd_file.filename}")
        elif jd_url:
            jd_text, scraped_role, scraped_company = scrape_job_posting(jd_url)
            role = scraped_role or role
            company = scraped_company or company
            flash(f"✅ Scraped JD from URL")

        resume = request.form.get("resume") or resume_text
        jd = request.form.get("jd") or jd_text
        payload = {"resume": resume, "jd": jd, "role": role, "company": company}

        try:
            if action == "tailor":
                res = requests.post(f"{API_URL}/tailor/", json=payload)
                result = res.text
                filename = f"tailored_resume_{role}_{company}_{datetime.now().strftime('%Y-%m-%dT%H-%M')}.pdf"
                save_temp_file(text_to_pdf_bytes(res.text), role, company, "tailored_resume")
                flash("🎯 Tailored Resume Created")
            elif action == "cover_letter":
                res = requests.post(f"{API_URL}/cover_letter/", json=payload)
                result = res.text
                save_temp_file(text_to_pdf_bytes(res.text), role, company, "cover_letter")
                flash("✉️ Cover Letter Generated")
            elif action == "match":
                res = requests.post(f"{API_URL}/match/", json={"resume": resume, "jd": jd})
                result = res.text
                flash("📊 JD Match Score Computed")
            elif action == "questions":
                res = requests.post(f"{API_URL}/generate-questions/", json={"resume": resume, "jd": jd})
                result = res.text
                flash("🧠 Interview Questions Ready")
        except Exception as e:
            result = f"❌ API Error: {e}"

    return render_template("index.html", result=result, resume=resume, jd=jd, role=role, company=company)


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    if request.method == "POST":
        current_user.role_preference = request.form.get("role")
        current_user.location_preference = request.form.get("location")
        current_user.work_mode = request.form.get("work_mode")
        current_user.salary_expectation = request.form.get("salary")
        db.session.commit()
        flash("✅ Preferences Updated")
        return redirect("/jobs")

    return render_template("preferences.html")


@app.route("/jobs")
@login_required
def jobs():
    role = current_user.role_preference or "Data Scientist"
    location = current_user.location_preference or "Remote"
    try:
        jobs = get_jobs_from_jsearch(role, location)
    except Exception as e:
        jobs = []
        flash(f"⚠️ Failed to fetch jobs: {e}")
    return render_template("jobs.html", jobs=jobs)


@app.route("/vault")
@login_required
def vault():
    files = get_temp_files()
    return render_template("vault.html", files=files)

@app.route("/download/<filename>")
@login_required
def download(filename):
    return send_from_directory('/tmp/career_ai_vault', filename, as_attachment=True)

@app.route("/delete/<filename>")
@login_required
def delete(filename):
    delete_temp_file(filename)
    return redirect("/vault")

@app.route("/cleanup")
@login_required
def cleanup():
    clean_old_files()
    flash("🧹 Cleanup complete.")
    return redirect("/vault")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Logged out!")
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
