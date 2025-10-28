# backend/src/job_matching.py
from backend.pipeline import JobMatcherPipeline
from inference import SkillMatcher

class ResumeJobMatcher:
    """
    Combines PhoBERT salary prediction with semantic job–resume matching.
    """

    def __init__(self, threshold=0.65):
        self.pipeline = JobMatcherPipeline()
        self.matcher = SkillMatcher()
        self.threshold = threshold

    def analyze(self, resume_text, job_title, job_description, requirements, benefits):
        """
        Unified inference: salary + skill match analysis.
        """
        # 1️⃣ Salary prediction
        salary_result = self.pipeline.predict_salary(
            resume_text, job_title, job_description, requirements, benefits
        )

        # 2️⃣ Skill similarity
        required_skills = self.matcher.extract_skills_from_text(requirements or job_description or "")
        missing_skills, match_score, _ = self.matcher.compute_missing_skills(
            resume_text, required_skills, threshold=self.threshold
        )

        return {
            "predicted_salary": salary_result["predicted_salary_vnd"],
            "match_score": match_score,
            "missing_skills": missing_skills,
            "input_text": salary_result["input_text"]
        }
