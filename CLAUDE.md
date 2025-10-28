# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Job Matcher Application that uses PhoBERT (Vietnamese language model) for matching resumes with job postings. The application provides salary predictions and skill gap analysis for Vietnamese job seekers and employers.

## Architecture

- **Frontend**: Next.js 14.2.5 with TypeScript, Tailwind CSS, and Radix UI components
- **Backend**: Python FastAPI with PyTorch, transformers, and sentence-transformers
- **AI Models**: PhoBERT for Vietnamese language processing
- **Deployment**: Docker containerization with support for AWS ECS, Google Cloud Run, and Railway

## Common Development Commands

### Local Development

```bash
# Backend (Terminal 1)
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
./run.sh

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### Docker Development

```bash
# Start both services with Docker Compose
docker-compose up --build

# Or use the Makefile
make local-docker
```

### Testing and Building

```bash
# Frontend
cd frontend
npm run build          # Build for production
npm run start          # Start production server

# Backend
cd backend
python -m pytest       # Run tests (if test files exist)
```

### Deployment

```bash
# Using Makefile (recommended)
make check-deployment                    # Run pre-deployment checks
make deploy-frontend                     # Deploy to Vercel
make deploy-backend PLATFORM=gcp         # Deploy to Google Cloud Run
make deploy-all PLATFORM=ecs             # Deploy both to AWS ECS

# Manual deployment
./deploy-frontend.sh --prod              # Frontend to Vercel
./deploy-backend.sh gcp --tag latest     # Backend to chosen platform
```

## Key Architecture Points

### Backend AI Pipeline

1. **JobMatcherPipeline** (`pipeline.py`): Main inference pipeline that orchestrates the entire process
2. **PhoBERT Model**: Fine-tuned Vietnamese language model for salary prediction
3. **SkillMatcher** (`inference.py`): Handles skill extraction and similarity matching
4. **Model Loading**: Supports both local artifacts and cloud storage downloads

### Model Artifacts

- Models are stored in `backend/artifacts/` with three subdirectories:
  - `model/`: Fine-tuned PhoBERT weights (`phobert_best.pt`)
  - `tokenizer/`: PhoBERT tokenizer files
  - `data/`: Training/testing data (if present)

### Frontend Structure

- **App Router**: Uses Next.js 13+ app directory structure
- **Components**: Main components in `components/` directory
- **API Integration**: Uses axios for backend communication
- **UI Framework**: Tailwind CSS with Radix UI primitives

### Environment Configuration

Backend (`.env`):
- `ARTIFACT_DIR`: Path to model artifacts
- `MODEL_URL`, `TOKENIZER_URL`: Cloud storage URLs for models
- `ALLOWED_ORIGINS`: CORS configuration
- `LOG_LEVEL`: Logging level

Frontend (`.env.local`):
- `NEXT_PUBLIC_API_URL`: Backend API endpoint

## Important Development Notes

### Model Requirements

1. PhoBERT model artifacts must be present in `backend/artifacts/` before running
2. If artifacts are missing, the application will attempt to download from cloud URLs if provided
3. The fine-tuned model should be named `phobert_best.pt` and placed in `artifacts/model/`

### Skill Matching Configuration

- Edit `inference.DEFAULT_EMBED_MODEL` to change the sentence embedding model
- Adjust `inference.SkillMatcher.compute_missing_skills` threshold for skill similarity tuning

### API Endpoints

- `POST /predict`: Main prediction endpoint (resume + job posting → salary/match analysis)
- `GET /health`, `/ready`, `/ping`: Health check endpoints
- CORS is configured based on `ALLOWED_ORIGINS` environment variable

### Docker Development

- Backend runs on port 8000, frontend on port 3000
- Health checks are configured for the backend container
- Artifacts directory is mounted read-only in development

### Deployment Considerations

- Frontend is deployed to Vercel automatically via `deploy-frontend.sh`
- Backend supports multiple cloud platforms (choose via PLATFORM parameter)
- Pre-deployment checks validate environment files and dependencies
- Makefile provides comprehensive deployment automation with colored output

## Development Workflow

1. **Setup**: Run `make setup-env` to create environment files from examples
2. **Local Development**: Use `make local-dev` or `make local-docker` for development
3. **Testing**: Run `make check-deployment` before any deployment
4. **Deployment**: Use `make deploy-all PLATFORM=<platform>` for full deployment

## File Structure Notes

- Backend uses global pipeline instance for efficiency (loaded once at startup)
- Frontend uses absolute imports with path mapping (`@/` prefix)
- Both services include comprehensive Docker configurations
- Deployment scripts handle platform-specific configurations automatically