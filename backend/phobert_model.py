# phobert_model.py
import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

class PhoBERTSalaryModel:
    def __init__(self, model_dir=None, device=None):
        self.model_dir = model_dir or os.path.join(ARTIFACT_DIR, "model")
        self.tokenizer_dir = os.path.join(ARTIFACT_DIR, "tokenizer")
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self._load()

    def _load(self):
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_dir, local_files_only=True)
        # Load model -- user might have a sequence-regressor or classifier head saved
        # Here we assume a single-output regression head (transformers still uses AutoModelForSequenceClassification).
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir, local_files_only=True)
        self.model.to(self.device)
        self.model.eval()

    def predict_salary(self, text):
        # Adjust max_length or truncation strategy to your needs
        inputs = self.tokenizer(text, truncation=True, padding="longest", return_tensors="pt", max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model(**inputs)
        # If regression: logits is shape (1,1) or (1,) depending on config. Convert to float
        logits = out.logits.cpu().numpy()
        # Heuristic: if single-dim prediction
        if logits.ndim == 2 and logits.shape[1] == 1:
            return float(logits[0,0])
        # if multi-dim, maybe trained to predict buckets -> we assume a float is in first position
        return float(logits[0].mean())
