"""
Simple FastAPI app for testing deployment
"""
import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job-matcher-simple")

# Create FastAPI app
app = FastAPI(
    title="Job Matcher API (Simple)",
    version="1.0.0",
    description="Simple API for testing deployment"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request model
class PredictRequest(BaseModel):
    resume_text: str
    job_title: str = ""
    description: str = ""
    requirements: str = ""
    benefits: str = ""

# Health check endpoint
@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Simple health check that doesn't require models"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "Job Matcher API (Simple)",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
    }

# Root endpoint
@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Job Matcher API is running",
        "docs": "/docs",
        "health": "/health"
    }

# Simple predict endpoint (mock response)
@app.post("/predict")
def predict(request: PredictRequest) -> Dict[str, Any]:
    """Mock prediction endpoint for testing"""
    logger.info(f"Prediction request received for job: {request.job_title}")

    # Return a mock response
    return {
        "predicted_salary": "15-20 million VND",
        "match_score": 0.75,
        "missing_skills": ["Python", "Machine Learning"],
        "parsed_resume": {
            "experience_years": 2,
            "education": "Bachelor's Degree",
            "skills": ["JavaScript", "React", "Node.js"]
        },
        "note": "This is a mock response. The full model will be loaded soon."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)