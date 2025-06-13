from api.extensions.db import Base
from sqlalchemy import Column, Integer, String, JSON, Text

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    onboarding_data = Column(JSON, default={})
    resume_text = Column(String, nullable=True)  # <-- Make sure this is present!
    #tailored_resume = Column(Text, nullable=True)
    tailored_resume = Column(String, nullable=True)
