from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.extensions.db import get_async_db
from api.models.user import User
from api.extensions.hashing import Hasher

router = APIRouter()

class SignupData(BaseModel):
    full_name: str = ""
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(data: SignupData, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=Hasher.get_password_hash(data.password)
    )
    db.add(user)
    await db.commit()
    return {"message": "Signup successful"}

@router.post("/login")
async def login(data: LoginData, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if not user or not Hasher.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # For MVP, return fake token. Add JWT for production.
    return {"message": "Login successful", "token": "session-" + user.email}

# --- For Onboarding: Dependency to get current user ---
async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = "",
):
    # For demo: token is "session-{email}".
    # In production, parse JWT or use session.
    if not token or not token.startswith("session-"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    email = token.replace("session-", "")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
