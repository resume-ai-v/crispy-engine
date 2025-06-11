from fastapi import APIRouter, HTTPException, Depends, status, Header
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
    full_name = f"{data.first_name} {data.last_name}".strip()
    user = User(
        full_name=full_name,
        email=data.email,
        password_hash=Hasher.get_password_hash(data.password)
    )
    db.add(user)
    await db.commit()
    # Return session token for MVP
    return {"message": "Signup successful", "token": f"session-{user.email}"}

@router.post("/login")
async def login(data: LoginData, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if not user or not Hasher.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful", "token": f"session-{user.email}"}

# Utility for current user (from MVP session-token in Authorization header)
async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    Authorization: str = Header(None),
):
    if not Authorization or not Authorization.startswith("session-"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    email = Authorization.replace("session-", "")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
