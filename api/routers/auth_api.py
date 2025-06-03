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

@router.post("/api/signup")
def signup(user: SignupModel, db: Session = Depends(get_db)):
    # 🔐 Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="⚠️ Email is already registered")

    hashed_password = Hasher.get_password_hash(user.password)
    db_user = User(full_name=user.full_name, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "✅ Signup successful"}

class LoginModel(BaseModel):
    email: str
    password: str

@router.post("/api/login")
def login(user: LoginModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="❌ Invalid credentials")

    if not Hasher.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="❌ Invalid credentials")

    # Return full_name so frontend can store it, etc.
    return {"full_name": db_user.full_name}
