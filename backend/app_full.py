# backend/app.py
"""
FastAPI entrypoint for PhoBERT Job Matcher.
Handles requests from frontend, loads pipeline once, and returns structured predictions.
"""

import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import JobMatcherPipeline

# -------------------------------
# Logging & App Setup
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job-matcher")

app = FastAPI(
    title="PhoBERT Job Matcher API",
    version="1.0",
    description="API for matching resumes with job postings using PhoBERT model"
)

# CORS configuration for production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
allowed_methods = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
allowed_headers = os.getenv("ALLOWED_HEADERS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# -------------------------------
# Request / Response Schemas
# -------------------------------
class PredictRequest(BaseModel):
    resume_text: str
    job_title: str = ""
    description: str = ""
    requirements: str = ""
    benefits: str = ""

# No need for a strict response model — we return dict/json directly.


# -------------------------------
# Pipeline Initialization
# -------------------------------
PIPELINE = None

@app.on_event("startup")
def load_pipeline():
    global PIPELINE
    try:
        logger.info("🚀 Loading PhoBERT pipeline and model artifacts...")
        PIPELINE = JobMatcherPipeline()
        logger.info("✅ PhoBERT pipeline loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load pipeline: {e}")
        PIPELINE = None


# -------------------------------
# Endpoints
# -------------------------------
@app.get("/ping")
def ping():
    return {"ok": True, "status": "ready" if PIPELINE else "loading"}


@app.get("/health")
def health_check():
    """
    Health check endpoint for container orchestration.
    Returns service status and basic system information.
    """
    if PIPELINE is None:
        return {
            "status": "unhealthy",
            "error": "Pipeline not loaded",
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "health_check", logging.INFO, "", 0, "", (), None
            )) if logger.handlers else None
        }
    
    return {
        "status": "healthy",
        "service": "job-matcher-api",
        "version": "1.0",
        "model_loaded": True,
        "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
            "health_check", logging.INFO, "", 0, "", (), None
        )) if logger.handlers else None
    }


@app.get("/ready")
def readiness_check():
    """
    Readiness check endpoint for container orchestration.
    Returns whether the service is ready to accept requests.
    """
    return {
        "ready": PIPELINE is not None,
        "status": "ready" if PIPELINE else "initializing"
    }


@app.get("/")
def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "PhoBERT Job Matcher API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "ping": "/ping",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.post("/predict")
def predict(req: PredictRequest):
    if PIPELINE is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready. Please try again later.")
    try:
        result = PIPELINE.predict(
            resume_text=req.resume_text,
            job_title=req.job_title,
            description=req.description,
            requirements=req.requirements,
            benefits=req.benefits,
        )
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
