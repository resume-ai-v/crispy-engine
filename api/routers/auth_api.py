from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.extensions.db import get_async_db
from api.models.user import User
from api.extensions.hashing import Hasher

router = APIRouter()

class SignupData(BaseModel):
    first_name: str = Field("", example="Vijay")
    last_name: str = Field("", example="Sheru")
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup", status_code=201)
async def signup(data: SignupData, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    # Combine first/last for full name fallback, or use as is
    full_name = f"{data.first_name} {data.last_name}".strip() if data.first_name or data.last_name else ""
    user = User(
        full_name=full_name,
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # TODO: Add JWT/session auth for production
    return {"message": "Login successful", "token": f"session-{user.email}"}

# Utility to get user from fake session-token (MVP only!)
async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = "",
):
    if not token or not token.startswith("session-"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    email = token.replace("session-", "")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
