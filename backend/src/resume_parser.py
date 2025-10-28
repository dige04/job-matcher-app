import re
from typing import Dict, List
from collections import defaultdict

class ResumeParser:
    """
    Lightweight rule-based resume parser.
    Detects sections like Education, Experience, Skills, etc.
    Converts raw text into a normalized structured dict.
    """

    SECTION_HEADERS = {
        "education": ["education", "academic background", "study"],
        "experience": ["experience", "employment", "work history", "career"],
        "skills": ["skills", "technical skills", "tools", "technologies"],
        "projects": ["projects", "portfolio"],
        "languages": ["languages", "communication languages"],
        "summary": ["summary", "objective", "profile"],
    }

    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        text = re.sub(r"\r|\t", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def parse_sections(self, text: str) -> Dict[str, str]:
        """
        Simple regex-based segmentation by section headers.
        Works well for English/Vietnamese mixed resumes.
        """
        text = self.normalize_text(text)
        sections = defaultdict(str)
        current_section = "summary"
        for line in re.split(r"\n|(?<=\.)(?=\s[A-Z])", text):
            line_lower = line.lower().strip()
            # Detect section headers
            for section, keywords in self.SECTION_HEADERS.items():
                if any(kw in line_lower for kw in keywords):
                    current_section = section
                    break
            sections[current_section] += " " + line
        return {k: v.strip() for k, v in sections.items() if v.strip()}

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract comma- or newline-separated skills, e.g. "Python, SQL, Deep Learning".
        """
        skills = re.findall(r"[A-Za-zÀ-ỹ\-+/]+", text)
        skills = [s.lower() for s in skills if len(s) > 2]
        return sorted(list(set(skills)))

    def parse(self, resume_text: str) -> Dict:
        """
        Returns both structured resume fields and a flattened version.
        """
        sections = self.parse_sections(resume_text)
        structured_resume = {
            "summary": sections.get("summary", ""),
            "education": [sections.get("education", "")],
            "experience": [sections.get("experience", "")],
            "projects": [sections.get("projects", "")],
            "languages": self.extract_skills(sections.get("languages", "")),
            "skills": self.extract_skills(sections.get("skills", "")),
        }

        # Flatten text for model embedding
        flattened_text = " ".join(
            [structured_resume["summary"]]
            + structured_resume["education"]
            + structured_resume["experience"]
            + structured_resume["projects"]
            + structured_resume["skills"]
        )

        return {
            "structured": structured_resume,
            "flattened": self.normalize_text(flattened_text)
        }
