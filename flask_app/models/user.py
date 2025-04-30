# flask_app/models/user.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask import current_app

# Use global DB instance from app
db = SQLAlchemy()

# === User Table ===
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Preferences
    role_preference = db.Column(db.String(100))
    location_preference = db.Column(db.String(100))
    work_mode = db.Column(db.String(50))  # e.g., remote, hybrid, on-site
    salary_expectation = db.Column(db.String(50))  # Optional: "80k-100k"

    # Relationship
    applications = db.relationship("Application", backref="user", lazy=True)

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
