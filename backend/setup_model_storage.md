# Setting up PhoBERT Model on Google Cloud Storage

## Steps to Upload Model:

1. **Create a GCS Bucket**:
```bash
gsutil mb gs://your-job-matcher-models
```

2. **Upload the model artifacts**:
```bash
# Upload the fine-tuned model
gsutil cp backend/artifacts/model/phobert_best.pt gs://your-job-matcher-models/

# Upload the tokenizer
gsutil -m cp -r backend/artifacts/tokenizer/* gs://your-job-matcher-models/tokenizer/

# Make files public readable
gsutil -m acl ch -u AllUsers:R gs://your-job-matcher-models/**
```

3. **Get the URLs**:
- Model: https://storage.googleapis.com/your-job-matcher-models/phobert_best.pt
- Tokenizer: https://storage.googleapis.com/your-job-matcher-models/tokenizer/

4. **Set environment variables in Railway**:
```
MODEL_URL=https://storage.googleapis.com/your-job-matcher-models/phobert_best.pt
TOKENIZER_URL=https://storage.googleapis.com/your-job-matcher-models/tokenizer.zip
ARTIFACT_DIR=/app/backend/artifacts
```

## Alternative: Use Vite Backend for Model Download
The pipeline.py already supports downloading models from URLs on startup!