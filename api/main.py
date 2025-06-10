from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Career AI Dev API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://launchhire.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# FIXED imports: No "api." prefix if main.py is inside api/!
from routers.auth_api import router as auth_router
from routers.resume_api import router as resume_router
from routers.feedback_api import router as feedback_router
from routers.jobs_api import router as jobs_router
from routers.interview_api import router as interview_router
from routers.apply_api import router as apply_router
from routers.onboarding_api import router as onboarding_router
from routers.match_api import router as match_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(resume_router)
api_router.include_router(feedback_router)
api_router.include_router(jobs_router)
api_router.include_router(interview_router)
api_router.include_router(apply_router)
api_router.include_router(onboarding_router)
api_router.include_router(match_router)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

from extensions.db import engine
from models.user import Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await init_models()
