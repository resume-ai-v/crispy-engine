# flask_app/db_check.py

from app import app, db, User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"📧 Email: {user.email}")
