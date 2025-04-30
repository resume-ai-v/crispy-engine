# flask_app/models/user.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    google_id = db.Column(db.String(200))

    # NEW FIELDS
    role_preference = db.Column(db.String(100))
    location_preference = db.Column(db.String(100))
    work_mode = db.Column(db.String(50))  # Remote / Onsite / Hybrid
    salary_expectation = db.Column(db.String(50))
