# utils.py
from pydantic import BaseModel, Field
from typing import List, Optional

class PredictRequest(BaseModel):
    resume_text: str = Field(..., description="Candidate resume text")
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None

class PredictResponse(BaseModel):
    predicted_salary: float
    missing_skills: List[str]
    match_score: float
    skill_scores: Optional[List[float]] = None
