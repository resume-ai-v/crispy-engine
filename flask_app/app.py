import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests

# Path fix for utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.temp_storage_manager import save_temp_file, clean_old_files, get_temp_files, delete_temp_file
from utils.scrape_job import scrape_job_posting
from utils.extract_text import extract_text_from_file
from utils.job_fetcher import get_jobs_from_jsearch
from utils.pdf_exporter import text_to_pdf_bytes
from models.user import db, User
from utils.news_fetcher import get_newsletter_info

# Flask setup
app = Flask(__name__)
app.secret_key = "career_ai_secret"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance/users.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ensure instance folder exists
if not os.path.exists("instance"):
    os.makedirs("instance")

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

API_URL = "http://localhost:8000"

# === Auth Routes ===
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")

        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect("/register")

        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Logged out successfully.")
    return redirect("/login")

# === Main Home Route ===
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    resume_text = jd_text = result = resume = jd = role = company = ""

    if request.method == "POST":
        action = request.form.get("action")
        role = request.form.get("role") or "Generic"
        company = request.form.get("company") or "Unknown"

        resume_file = request.files.get("resume_file")
        if resume_file and resume_file.filename:
            content = resume_file.read()
            resume_text = extract_text_from_file(resume_file)
            save_temp_file(content, role, company, "resume")

        jd_file = request.files.get("jd_file")
        jd_url = request.form.get("jd_url")
        if jd_file and jd_file.filename:
            content = jd_file.read()
            jd_text = extract_text_from_file(jd_file)
        elif jd_url:
            jd_text, scraped_role, scraped_company = scrape_job_posting(jd_url)
            role = scraped_role or role
            company = scraped_company or company

        resume = request.form.get("resume") or resume_text
        jd = request.form.get("jd") or jd_text
        payload = {"resume": resume, "jd": jd, "role": role, "company": company}

        try:
            if action == "tailor":
                res = requests.post(f"{API_URL}/tailor/", json=payload)
                result = res.text
                save_temp_file(text_to_pdf_bytes(res.text), role, company, "tailored_resume")
            elif action == "cover_letter":
                res = requests.post(f"{API_URL}/cover_letter/", json=payload)
                result = res.text
                save_temp_file(text_to_pdf_bytes(res.text), role, company, "cover_letter")
            elif action == "match":
                res = requests.post(f"{API_URL}/match/", json={"resume": resume, "jd": jd})
                result = res.text
            elif action == "questions":
                res = requests.post(f"{API_URL}/generate-questions/", json={"resume": resume, "jd": jd})
                result = res.text
        except Exception as e:
            result = f"❌ API Error: {e}"

    return render_template("index.html", result=result, resume=resume, jd=jd, role=role, company=company)

# === Preferences ===
@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    if request.method == "POST":
        current_user.role_preference = request.form.get("role")
        current_user.location_preference = request.form.get("location")
        current_user.work_mode = request.form.get("work_mode")
        current_user.salary_expectation = request.form.get("salary")
        db.session.commit()
        flash("✅ Preferences updated.")
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
        flash(f"⚠️ Job fetch failed: {e}")
    return render_template("jobs.html", jobs=jobs)

@app.route("/vault")
@login_required
def vault():
    files = get_temp_files()
    return render_template("vault.html", files=files)

@app.route("/download/<filename>")
@login_required
def download(filename):
    return send_from_directory("/tmp/career_ai_vault", filename, as_attachment=True)

@app.route("/delete/<filename>")
@login_required
def delete(filename):
    delete_temp_file(filename)
    return redirect("/vault")

@app.route("/cleanup")
@login_required
def cleanup():
    clean_old_files()
    flash("🧹 Vault cleaned.")
    return redirect("/vault")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/resume-editor", methods=["GET", "POST"])
@login_required
def resume_editor():
    if request.method == "POST":
        current_user.base_resume = request.form["resume"]
        db.session.commit()
        flash("✅ Resume saved successfully.")
        return redirect("/resume-editor")
    return render_template("resume_editor.html", resume_text=current_user.base_resume or "")

@app.route("/newsletter")
@login_required
def newsletter():
    news = get_newsletter_info()
    return render_template("newsletter.html", news=news)

# === AI Interview Simulation ===
@app.route("/interview")
@login_required
def interview():
    return render_template("interview.html")  # Add template with avatar interaction UI

# ============ Run App ============
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
