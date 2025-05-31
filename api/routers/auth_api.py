from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.extensions.db import get_db
from api.models.user import User
from api.extensions.hashing import Hasher
from pydantic import BaseModel

router = APIRouter()

class SignupModel(BaseModel):
    full_name: str
    email: str
    password: str

@router.post("/signup")
def signup(user: SignupModel, db: Session = Depends(get_db)):
    # 🔐 CHECK IF EMAIL ALREADY EXISTS
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="⚠️ Email is already registered")

    hashed_password = Hasher.get_password_hash(user.password)
    db_user = User(full_name=user.full_name, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "✅ Signup successful"}
