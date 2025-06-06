from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Career AI Dev API")

# -- CORS FIX: Allow all Vercel subdomains, production safe --
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

from api.routers.auth_api import router as auth_router
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router
from api.routers.onboarding_api import router as onboarding_router

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(feedback_router)
app.include_router(jobs_router)
app.include_router(interview_router)
app.include_router(apply_router)
app.include_router(onboarding_router)

from api.routers.match_api import router as match_router
app.include_router(match_router)

@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

app.mount("/static", StaticFiles(directory="static"), name="static")

from api.extensions.db import Base, engine
from api.models.user import User
Base.metadata.create_all(bind=engine)
