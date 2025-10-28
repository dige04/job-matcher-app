# backend/pipeline.py
"""
End-to-end PhoBERT inference pipeline:
- Cleans and parses resume + job posting
- Predicts salary using PhoBERT fine-tuned model
- Computes skill similarity and missing skills
"""

import os
import requests
import tempfile
import zipfile
from pathlib import Path
import numpy as np
import torch
from transformers import PhobertTokenizer, RobertaModel

# Internal imports
from src.data_preprocessing import normalize_text
from src.feature_engineering import build_input_text
from src.phobert_finetune_utils import PhoBERTRegressor
from src.parsing_layer import ParsingLayer
from src.resume_parser import ResumeParser

# --- Configuration ---
ARTIFACT_DIR = Path(os.environ.get("ARTIFACT_DIR", Path(__file__).parent / "artifacts"))
MODEL_WEIGHTS = ARTIFACT_DIR / "model" / "phobert_best.pt"
TOKENIZER_DIR = ARTIFACT_DIR / "tokenizer"
BASE_MODEL_DIR = Path(os.environ.get("PHOBERT_BASE_DIR", ""))  # base PhoBERT (VinAI)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cloud storage URLs (environment variables)
MODEL_URL = os.environ.get("MODEL_URL", "")
TOKENIZER_URL = os.environ.get("TOKENIZER_URL", "")
BASE_MODEL_URL = os.environ.get("BASE_MODEL_URL", "")


def download_and_extract(url: str, extract_to: Path) -> bool:
    """
    Download and extract a zip file from a URL to a directory.
    Returns True if successful, False otherwise.
    """
    if not url:
        return False
        
    try:
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create a temporary file for the download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Extract the zip file
        extract_to.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Clean up the temporary file
        os.unlink(tmp_file_path)
        print(f"Successfully extracted to {extract_to}")
        return True
        
    except Exception as e:
        print(f"Error downloading from {url}: {e}")
        return False


def download_file(url: str, file_path: Path) -> bool:
    """
    Download a single file from a URL.
    Returns True if successful, False otherwise.
    """
    if not url:
        return False
        
    try:
        print(f"Downloading file from {url}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded to {file_path}")
        return True
        
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
        return False


class JobMatcherPipeline:
    """
    Unified pipeline for PhoBERT salary prediction + resume-job matching.
    """

    def __init__(self, device=None):
        self.device = device or DEVICE

        # --- Download models if URLs are provided ---
        self._download_models_if_needed()

        # --- Load tokenizer ---
        if TOKENIZER_DIR.exists():
            self.tokenizer = PhobertTokenizer.from_pretrained(str(TOKENIZER_DIR))
        elif BASE_MODEL_DIR.exists():
            self.tokenizer = PhobertTokenizer.from_pretrained(str(BASE_MODEL_DIR))
        else:
            raise FileNotFoundError(
                "Tokenizer not found. Please place tokenizer files in backend/artifacts/tokenizer or set TOKENIZER_URL"
            )

        # --- Load base PhoBERT model ---
        if BASE_MODEL_DIR.exists():
            self.base_roberta = RobertaModel.from_pretrained(str(BASE_MODEL_DIR))
        else:
            raise FileNotFoundError(
                "Base PhoBERT model not found. Set PHOBERT_BASE_DIR or BASE_MODEL_URL or place model in artifacts/model"
            )

        # --- Load fine-tuned regressor ---
        self.model = PhoBERTRegressor(self.base_roberta)
        if MODEL_WEIGHTS.exists():
            state = torch.load(str(MODEL_WEIGHTS), map_location=self.device)
            self.model.load_state_dict(state)
        else:
            print(f"[WARN] Model weights not found at {MODEL_WEIGHTS}. Using uninitialized weights.")
        self.model.to(self.device)
        self.model.eval()

        # --- Load parsing utilities ---
        self.parsing_layer = ParsingLayer(
            model_path=str(BASE_MODEL_DIR),
            tokenizer_path=str(TOKENIZER_DIR),
            device=self.device
        )
        self.resume_parser = ResumeParser()

    def _download_models_if_needed(self):
        """Download models from cloud storage if URLs are provided and local files don't exist."""
        
        # Download tokenizer if URL is provided and local tokenizer doesn't exist
        if TOKENIZER_URL and not TOKENIZER_DIR.exists():
            if not download_and_extract(TOKENIZER_URL, TOKENIZER_DIR):
                print(f"[WARN] Failed to download tokenizer from {TOKENIZER_URL}")
        
        # Download base model if URL is provided and local model doesn't exist
        if BASE_MODEL_URL and not BASE_MODEL_DIR.exists():
            if not download_and_extract(BASE_MODEL_URL, BASE_MODEL_DIR):
                print(f"[WARN] Failed to download base model from {BASE_MODEL_URL}")
        
        # Download fine-tuned model weights if URL is provided and local weights don't exist
        if MODEL_URL and not MODEL_WEIGHTS.exists():
            if not download_file(MODEL_URL, MODEL_WEIGHTS):
                print(f"[WARN] Failed to download model weights from {MODEL_URL}")

    # -----------------------------------------------------
    # 1️⃣ Preprocessing
    # -----------------------------------------------------
    def preprocess_input(self, resume_text: str, job_title: str = "", job_description: str = "", requirements: str = "", benefits: str = ""):
        resume_clean = normalize_text(resume_text)
        job_parts = [job_title, job_description, requirements, benefits]
        job_clean = normalize_text(" ".join([p for p in job_parts if p]))

        tmp_row = {
            "job_title": job_title,
            "description": job_description,
            "requirement": requirements,
            "benefit": benefits,
            "industry": "",
            "position_level": "",
        }
        input_text = build_input_text(tmp_row)
        return resume_clean, job_clean, input_text

    # -----------------------------------------------------
    # 2️⃣ Salary Prediction
    # -----------------------------------------------------
    def predict_salary(self, resume_text: str, job_title: str, job_description: str, requirements: str, benefits: str):
        _, _, input_text = self.preprocess_input(
            resume_text, job_title, job_description, requirements, benefits
        )

        enc = self.tokenizer(
            str(input_text),
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            out = self.model(input_ids=input_ids, attention_mask=attention_mask)
            preds = out["preds"].cpu().numpy()

        pred_log1p = float(preds[0]) if preds.shape[0] > 0 else float(preds)
        try:
            pred_vnd = float(np.expm1(pred_log1p))
        except Exception:
            pred_vnd = None

        return pred_vnd

    # -----------------------------------------------------
    # 3️⃣ Resume–Job Matching + Skill Analysis
    # -----------------------------------------------------
    def analyze_resume_and_job(self, resume_text: str, description: str, requirements: str, benefits: str):
        job_posting = {
            "description": description,
            "requirements": requirements,
            "benefits": benefits,
        }
        return self.parsing_layer.parse_and_compare(resume_text, job_posting)

    # -----------------------------------------------------
    # 4️⃣ Unified Predict Method
    # -----------------------------------------------------
    def predict(self, resume_text: str, job_title: str = "", description: str = "", requirements: str = "", benefits: str = ""):
        """
        Runs full PhoBERT inference + text matching and returns a unified response.
        """
        try:
            # Parse resume structure
            parsed_resume = self.resume_parser.parse(resume_text)
            structured_resume = parsed_resume["structured"]

            # Predict salary
            salary_pred = self.predict_salary(resume_text, job_title, description, requirements, benefits)

            # Compute match metrics
            match_result = self.analyze_resume_and_job(resume_text, description, requirements, benefits)

            return {
                "predicted_salary": salary_pred,
                "match_score": match_result["match_score"],
                "missing_skills": match_result["missing_skills"],
                "structured_resume": structured_resume
            }

        except Exception as e:
            print(f"[ERROR] Pipeline prediction failed: {e}")
            raise
