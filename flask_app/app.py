import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from utils.temp_storage_manager import save_temp_file, clean_old_files, get_temp_files, delete_temp_file
from utils.scrape_job import scrape_job_posting
from utils.extract_text import extract_text_from_file

import requests
from dotenv import load_dotenv
load_dotenv()

# === App Setup ===
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "career_ai_secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "google.login"

# === OAuth Setup ===
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === FastAPI Endpoint ===
API_URL = "http://localhost:8000"

# === Routes ===

# 🏠 Home Page
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
            save_temp_file(content, role=role, company=company, file_type="base_resume")
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
                flash("🎯 Tailored Resume Generated Successfully!")
            elif action == "cover_letter":
                res = requests.post(f"{API_URL}/cover_letter/", json=payload)
                result = res.text
                flash("✉️ Cover Letter Generated Successfully!")
            elif action == "match":
                res = requests.post(f"{API_URL}/match/", json={"resume": resume, "jd": jd})
                result = res.text
                flash("📊 JD Match Score Computed!")
            elif action == "questions":
                res = requests.post(f"{API_URL}/generate-questions/", json={"resume": resume, "jd": jd})
                result = res.text
                flash("🧠 Interview Questions Generated!")
        except Exception as e:
            result = f"❌ API Error: {e}"

    return render_template("index.html", result=result, resume=resume, jd=jd, role=role, company=company)


# 📁 Resume Vault Page
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
    flash("🧹 Cleanup completed.")
    return redirect("/vault")

# 🚪 Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Logged out!")
    return redirect("/")

# === Run App ===
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
