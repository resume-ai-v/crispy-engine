from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()

app = FastAPI(title="Career AI Dev API")

# --- CORS Middleware (for production and dev) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://launchhire.vercel.app",
        "https://launchhire-vijays-projects-10840c84.vercel.app",
        "http://localhost:3000",
        # Add more preview or custom domains here as needed!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Session Middleware ---
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

# --- Static Files (serves /static if folder exists) ---
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Import Routers (each should use router = APIRouter() with NO prefix in their own file) ---
from api.routers.auth_api import router as auth_router
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router
from api.routers.onboarding_api import router as onboarding_router
from api.routers.match_api import router as match_router

# --- Master API Router (prefixes all API endpoints under /api) ---
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

# --- Health Check Root Route ---
@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

# --- Database: Auto-create tables on startup ---
from api.extensions.db import engine
from api.models.user import Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await init_models()
