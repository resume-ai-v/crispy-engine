from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.extensions.db import get_async_db
from api.models.user import User
from api.extensions.hashing import Hasher
from pydantic import BaseModel, EmailStr
import jwt
import os
from datetime import datetime, timedelta
import re

router = APIRouter()
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-prod")
JWT_ALGORITHM = "HS256"

# Password strength checker (no external dependencies)
def check_password_strength(password: str) -> bool:
    # At least 8 characters, 1 uppercase, 1 number
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

class SignupModel(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=4)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# --- JWT Auth Helper (for other APIs) ---
async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid JWT")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid JWT payload")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

@router.post("/api/signup")
async def signup(user: SignupModel, db: AsyncSession = Depends(get_async_db)):
    # Check if password is strong
    if not check_password_strength(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 chars, incl. uppercase and number.",
        )
    async with db.begin():
        result = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="⚠️ Email is already registered")
        hashed_password = Hasher.get_password_hash(user.password)
        db_user = User(full_name=user.full_name, email=user.email, password_hash=hashed_password)
        db.add(db_user)
    await db.commit()
    # JWT for instant login
    access_token = create_access_token({"sub": user.email})
    return {"message": "✅ Signup successful", "access_token": access_token, "full_name": user.full_name}

@router.post("/api/login")
async def login(login: LoginModel, db: AsyncSession = Depends(get_async_db)):
    async with db.begin():
        result = await db.execute(select(User).where(User.email == login.email))
        user = result.scalars().first()
        if not user or not Hasher.verify_password(login.password, user.password_hash):
            # Generic error: never leak which was wrong!
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    access_token = create_access_token({"sub": user.email})
    return {"message": "✅ Login successful", "access_token": access_token, "full_name": user.full_name}

# --- (Optional) SlowAPI Rate Limiting Example ---
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# limiter = Limiter(key_func=get_remote_address)
# router.route_class = limiter.limit("5/minute")(APIRouter)
