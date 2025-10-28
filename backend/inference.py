# inference.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

# load a sentence-transformers model for embeddings
# Option: allow using a PhoBERT-based sentence embedding you created. We'll default to a multilingual model.
DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class SkillMatcher:
    def __init__(self, embed_model_name=None):
        model_name = embed_model_name or DEFAULT_EMBED_MODEL
        self.embedder = SentenceTransformer(model_name)

    def extract_skills_from_text(self, job_text):
        """
        Simple skill extraction strategy:
         - Use heuristics to split 'requirements' into bullet points / lines
         - Alternatively you can plug in a trained NER extractor for 'SKILL' if available.
        """
        # split by lines and common separators
        lines = re.split(r'\n|•|-|–|;', job_text)
        # filter short lines
        cleaned = [l.strip() for l in lines if len(l.strip()) > 3]
        # Optionally deduplicate and normalize
        seen = set()
        skills = []
        for s in cleaned:
            s_norm = s.lower()
            if s_norm not in seen:
                skills.append(s.strip())
                seen.add(s_norm)
        return skills

    def compute_missing_skills(self, resume_text, required_skills, threshold=0.65):
        """
        For each required_skill, compute similarity between resume and the skill sentence.
        if similarity < threshold -> flagged as missing/weak.
        Returns: missing_skills list and scores list
        """
        if not required_skills:
            return [], 1.0

        # Embed resume as a single vector and each skill separately
        resume_embedding = self.embedder.encode(resume_text, convert_to_tensor=True)
        skill_embeddings = self.embedder.encode(required_skills, convert_to_tensor=True)

        # cosine similarities
        sims = util.cos_sim(resume_embedding, skill_embeddings)[0].cpu().numpy()
        missing = []
        scores = []
        for skill, score in zip(required_skills, sims):
            scores.append(float(score))
            if float(score) < threshold:
                missing.append(skill)
        # overall match score as mean similarity (clipped 0..1)
        match_score = float(np.clip(np.mean(sims), 0.0, 1.0))
        return missing, match_score, scores
