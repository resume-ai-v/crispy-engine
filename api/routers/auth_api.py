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

class LoginModel(BaseModel):
    email: str
    password: str

@router.post("/api/signup")
def signup(user: SignupModel, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="⚠️ Email is already registered")
    hashed_password = Hasher.get_password_hash(user.password)
    db_user = User(full_name=user.full_name, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "✅ Signup successful"}

@router.post("/api/login")
def login(login: LoginModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    if not user or not Hasher.verify_password(login.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "✅ Login successful", "full_name": user.full_name}
