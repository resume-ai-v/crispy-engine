from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="Career AI Dev API")

# --- CORS FIX ---
# Explicitly listing your frontend's exact URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://launchhire.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

# Static file mounting (if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Import routers
from api.routers.auth_api import router as auth_router
from api.routers.resume_api import router as resume_router
from api.routers.feedback_api import router as feedback_router
from api.routers.jobs_api import router as jobs_router
from api.routers.interview_api import router as interview_router
from api.routers.apply_api import router as apply_router
from api.routers.onboarding_api import router as onboarding_router
from api.routers.match_api import router as match_router

# ✅ Create a main API router and include other routers with the /api prefix
api_router = APIRouter(prefix="/api")

# --- THIS SECTION IS NOW CORRECTED ---
# The variables for each router are now correctly referenced.
api_router.include_router(auth_router)
api_router.include_router(resume_router)
api_router.include_router(feedback_router)
api_router.include_router(jobs_router)
api_router.include_router(interview_router)
api_router.include_router(apply_router)
api_router.include_router(onboarding_router)
api_router.include_router(match_router)

app.include_router(api_router)

# ✅ Health check route
@app.get("/")
def root():
    return {"message": "Career AI backend is live!"}

# ✅ Async DB initialization
from api.extensions.db import engine
from api.models.user import Base

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await init_models()