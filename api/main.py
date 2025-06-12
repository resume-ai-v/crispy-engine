from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# --- Load environment variables (from .env) ---
load_dotenv()

app = FastAPI(title="Career AI Dev API")

# --- CORS Middleware (IMPORTANT: Domains must match browser exactly, no trailing slash) ---
PROD_ORIGINS = [
    "https://launchhire.vercel.app",
    "https://launchhire-vijays-projects-10840c84.vercel.app",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=PROD_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Session Middleware (for login/session handling) ---
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

# --- Static files (if needed for user uploads, resumes, etc) ---
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Import and mount all API routers ---
from api.routers.auth_api import router as auth_router
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router
from api.routers.onboarding_api import router as onboarding_router
from api.routers.match_api import router as match_router

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

# --- Health Check (always available) ---
@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

# --- Database: Auto-create tables on startup (if using SQLAlchemy/async) ---
from api.extensions.db import engine
from api.models.user import Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await init_models()

# --- Extra Debug Route for CORS (optional, for debugging only) ---
@app.get("/api/debug/origins")
def debug_origins():
    return {"allowed_origins": PROD_ORIGINS}
