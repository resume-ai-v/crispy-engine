# flask_app/models/user.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role_preference = db.Column(db.String(100))
    location_preference = db.Column(db.String(100))
    work_mode = db.Column(db.String(50))
    salary_expectation = db.Column(db.String(50))
    base_resume = db.Column(db.Text)  # Store raw resume text

# === Job Application Tracking Table ===
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    status = db.Column(db.String(50))  # Applied / Interviewing / Offer / Rejected
    note = db.Column(db.Text)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)

# === Optional Admin Model (for future RBAC) ===
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False)
