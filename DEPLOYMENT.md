# Container Deployment Guide

This guide explains how to deploy the Job Matcher application using containers to services like AWS ECS, Google Cloud Run, or Railway.

## Prerequisites

- Docker and Docker Compose installed
- Model artifacts (PhoBERT model and tokenizer) uploaded to cloud storage or available locally

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the backend directory based on `backend/.env.example`:

```bash
# Model Configuration
ARTIFACT_DIR=/app/backend/artifacts

# Cloud storage URLs for models (optional)
MODEL_URL=https://your-storage.com/models/phobert_best.pt
TOKENIZER_URL=https://your-storage.com/tokenizer.zip
BASE_MODEL_URL=https://your-storage.com/base_model.zip

# Local path to base PhoBERT model (if not using cloud storage)
PHOBERT_BASE_DIR=

# API Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create a `.env.local` file in the frontend directory based on `frontend/.env.local.example`:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Local Development with Docker Compose

1. Clone the repository and navigate to the project root
2. Create the necessary environment files as described above
3. Run the application:

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

### AWS ECS

1. Build and push the Docker images to Amazon ECR:

```bash
# Backend
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker build -t job-matcher-backend ./backend
docker tag job-matcher-backend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-backend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-backend:latest

# Frontend
docker build -t job-matcher-frontend ./frontend
docker tag job-matcher-frontend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-frontend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-frontend:latest
```

2. Create an ECS task definition with the appropriate environment variables
3. Set up an Application Load Balancer with proper health checks
4. Configure the health check endpoint: `/health`

### Google Cloud Run

1. Build and push the Docker images to Google Container Registry:

```bash
# Backend
gcloud builds submit --tag gcr.io/PROJECT-ID/job-matcher-backend ./backend

# Frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/job-matcher-frontend ./frontend
```

2. Deploy to Cloud Run:

```bash
# Backend
gcloud run deploy job-matcher-backend \
  --image gcr.io/PROJECT-ID/job-matcher-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "MODEL_URL=https://your-storage.com/models/phobert_best.pt,TOKENIZER_URL=https://your-storage.com/tokenizer.zip"

# Frontend
gcloud run deploy job-matcher-frontend \
  --image gcr.io/PROJECT-ID/job-matcher-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://job-matcher-backend-abcdef1234-uc.a.run.app"
```

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile and build the application
3. Set environment variables in the Railway dashboard
4. Railway will automatically handle health checks using the `/health` endpoint

## Model Storage

### Option 1: Bundle Models with Container

Include model artifacts in the container image by placing them in `backend/artifacts/` before building.

### Option 2: Cloud Storage (Recommended)

1. Upload model artifacts to cloud storage (AWS S3, Google Cloud Storage, etc.)
2. Set the appropriate environment variables:
   - `MODEL_URL`: URL to the fine-tuned model weights
   - `TOKENIZER_URL`: URL to the tokenizer zip file
   - `BASE_MODEL_URL`: URL to the base PhoBERT model zip file

The application will automatically download the models on startup if the URLs are provided.

## Health Checks

The backend service includes several health check endpoints:

- `/health`: Returns service health status (used by container orchestration)
- `/ready`: Returns whether the service is ready to accept requests
- `/ping`: Simple ping endpoint

## Monitoring and Logging

- Application logs are output to stdout/stderr and can be collected by your container platform
- The health check endpoint includes service status and timestamp information
- Set `LOG_LEVEL` environment variable to control logging verbosity

## Security Considerations

1. Configure appropriate CORS origins for production
2. Use HTTPS in production environments
3. Consider implementing API authentication if needed
4. Regularly update base Docker images for security patches
5. Use non-root users in containers (already configured in the Dockerfiles)