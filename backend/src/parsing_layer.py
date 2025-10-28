# backend/src/parsing_layer.py
import re
import torch
import numpy as np
from typing import List, Dict
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from src.resume_parser import ResumeParser

class ParsingLayer:
    """
    Cleans, tokenizes, and compares resume vs job posting text using PhoBERT embeddings.
    Also identifies missing or weak skills.
    """

    def __init__(self, model_path: str, tokenizer_path: str, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
        self.model.eval()
        self.resume_parser = ResumeParser()

    # --- TEXT CLEANING ---
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^A-Za-zÀ-ỹ0-9.,;:!?()\-/ ]+', '', text)
        return text.lower()

    # --- TOKENIZATION & EMBEDDING ---
    def get_sentence_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=256, padding=True
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        return embeddings

    # --- SIMILARITY SCORE ---
    def compute_match_score(self, resume_text: str, job_text: str) -> float:
        resume_emb = self.get_sentence_embedding(resume_text)
        job_emb = self.get_sentence_embedding(job_text)
        score = cosine_similarity(resume_emb, job_emb)[0][0]
        return float(score * 100)  # scale to 0–100

    # --- SKILL EXTRACTION ---
    def extract_keywords(self, text: str) -> List[str]:
        """Extracts noun-like keywords (simplified rule-based)."""
        tokens = re.findall(r'\b[a-zA-ZÀ-ỹ]{3,}\b', text.lower())
        common_stopwords = set([
            "and", "or", "with", "for", "the", "in", "of", "to", "a", "an", "on", "at", "by", 
            "is", "are", "as", "from", "this", "that", "your", "our", "their", "etc"
        ])
        keywords = [t for t in tokens if t not in common_stopwords]
        return sorted(list(set(keywords)))

    def find_missing_skills(self, resume_text: str, job_text: str) -> List[str]:
        resume_keywords = set(self.extract_keywords(resume_text))
        job_keywords = set(self.extract_keywords(job_text))
        missing = [kw for kw in job_keywords if kw not in resume_keywords]
        return missing[:15]  # limit output length

    # --- MAIN ENTRYPOINT ---
    def parse_and_compare(self, resume_text: str, job_posting: Dict[str, str]) -> Dict:
        # --- Step 1. Parse resume ---
        parsed_resume = self.resume_parser.parse(resume_text)
        resume_flat = parsed_resume["flattened"]

        # --- Step 2. Prepare job posting text ---
        description = job_posting.get("description", "")
        requirements = job_posting.get("requirements", "")
        benefits = job_posting.get("benefits", "")
        job_text = self.clean_text(" ".join([description, requirements, benefits]))

        # --- Step 3. Compute similarity ---
        match_score = self.compute_match_score(resume_flat, job_text)
        missing_skills = self.find_missing_skills(resume_flat, job_text)

        return {
            "structured_resume": parsed_resume["structured"],
            "match_score": match_score,
            "missing_skills": missing_skills,
        }

