from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine
from app.database.models import Base
from app.routes import upload, candidates

# ─────────────────────────────────────────
# CREATE ALL DATABASE TABLES
# ─────────────────────────────────────────

Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────
# CREATE FASTAPI APP
# ─────────────────────────────────────────

app = FastAPI(
    title       = "RecruitFlow Intelligence Engine",
    description = "AI Powered Resume Parsing and Candidate Analysis System",
    version     = "1.0.0"
)

# ─────────────────────────────────────────
# CORS MIDDLEWARE
# ─────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

# ─────────────────────────────────────────
# INCLUDE ROUTES
# ─────────────────────────────────────────

app.include_router(upload.router,     tags=["Resume Upload"])
app.include_router(candidates.router, tags=["Candidates"])


# ─────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to RecruitFlow Intelligence Engine",
        "version": "1.0.0",
        "status" : "running",
        "docs"   : "Go to /docs to test all API endpoints"
    }


# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status" : "healthy",
        "message": "All systems are running"
    }