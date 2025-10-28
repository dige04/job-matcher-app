# Job Matcher App - Comprehensive Deployment Guide

This guide provides complete instructions for deploying both the frontend and backend components of the Job Matcher application.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Variables](#environment-variables)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Backend Deployment (Container Services)](#backend-deployment-container-services)
7. [Deployment Automation](#deployment-automation)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

## Architecture Overview

The Job Matcher application consists of:

- **Frontend**: Next.js application deployed to Vercel
- **Backend**: FastAPI Python application with PhoBERT model, deployed as a container
- **Model Storage**: PhoBERT model and tokenizer artifacts (can be bundled with container or stored in cloud storage)

## Prerequisites

### Required Tools
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- Docker and Docker Compose (for local testing)
- Vercel CLI (for frontend deployment)
- Cloud provider CLI (AWS, Google Cloud, or Railway access)

### Required Accounts
- Vercel account (connected to Git provider)
- Cloud provider account (AWS, Google Cloud, or Railway)
- (Optional) Cloud storage account for model artifacts

## Environment Variables

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# API URL for the backend service
# Replace with your deployed backend URL when deploying to production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Model Configuration
# Directory where model artifacts are stored
ARTIFACT_DIR=/app/backend/artifacts

# Cloud storage URLs for models (optional)
# If provided, models will be downloaded from these URLs if not present locally
MODEL_URL=
TOKENIZER_URL=
BASE_MODEL_URL=

# Local path to base PhoBERT model (if not using cloud storage)
PHOBERT_BASE_DIR=

# API Configuration
# Comma-separated list of allowed origins for CORS
# For production: https://yourdomain.com,https://www.yourdomain.com
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Allowed HTTP methods for CORS
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Allowed headers for CORS
ALLOWED_HEADERS=*

# Logging
LOG_LEVEL=INFO
```

## Pre-Deployment Checklist

Before deploying, ensure you have completed the following:

### Frontend Checklist
- [ ] All dependencies are installed (`npm install`)
- [ ] Environment variables are configured in `.env.local`
- [ ] Application builds successfully (`npm run build`)
- [ ] API endpoints are correctly configured
- [ ] Static assets are optimized
- [ ] Error handling is implemented

### Backend Checklist
- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] Environment variables are configured in `.env`
- [ ] Model artifacts are available in `backend/artifacts/` or cloud storage URLs are set
- [ ] Application starts successfully (`python app.py`)
- [ ] Health check endpoints are accessible (`/health`, `/ready`, `/ping`)
- [ ] CORS is properly configured for production domains
- [ ] Logging is configured appropriately

### Security Checklist
- [ ] Environment variables don't contain sensitive values in code
- [ ] CORS is restricted to production domains
- [ ] HTTPS will be used in production
- [ ] API rate limiting is considered (if needed)
- [ ] Input validation is implemented
- [ ] Error messages don't expose sensitive information

## Frontend Deployment (Vercel)

### Option 1: Through Vercel Dashboard (Recommended)

1. Log in to your Vercel dashboard
2. Click **Add New...** > **Project**
3. Import your Git repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (if deploying from monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL
6. Click **Deploy**

### Option 2: Using Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Run the deployment command:
   ```bash
   vercel --prod
   ```

4. Follow the prompts to configure your project

### Option 3: Using the Deployment Script

Use the provided deployment script:
```bash
./deploy-frontend.sh
```

## Backend Deployment (Container Services)

The backend can be deployed to any container service. Below are instructions for common platforms:

### AWS ECS

1. Build and push the Docker images to Amazon ECR:
   ```bash
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
   docker build -t job-matcher-backend ./backend
   docker tag job-matcher-backend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-backend:latest
   docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/job-matcher-backend:latest
   ```

2. Create an ECS task definition with the appropriate environment variables
3. Set up an Application Load Balancer with proper health checks
4. Configure the health check endpoint: `/health`

### Google Cloud Run

1. Build and push the Docker images to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/job-matcher-backend ./backend
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy job-matcher-backend \
     --image gcr.io/PROJECT-ID/job-matcher-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "MODEL_URL=https://your-storage.com/models/phobert_best.pt,TOKENIZER_URL=https://your-storage.com/tokenizer.zip"
   ```

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile and build the application
3. Set environment variables in the Railway dashboard
4. Railway will automatically handle health checks using the `/health` endpoint

### Option 4: Using the Deployment Script

Use the provided deployment script:
```bash
./deploy-backend.sh [platform]
```
Where `platform` is one of: `ecs`, `gcp`, `railway`

## Deployment Automation

### Using the Makefile

The provided Makefile includes common deployment commands:

```bash
# Deploy frontend to Vercel
make deploy-frontend

# Deploy backend to specified platform
make deploy-backend PLATFORM=ecs

# Deploy both services
make deploy-all PLATFORM=ecs

# Run pre-deployment checks
make check-deployment

# View all available commands
make help
```

### Using the Deployment Scripts

#### Frontend Deployment Script

The `deploy-frontend.sh` script automates the Vercel deployment process:

```bash
./deploy-frontend.sh [--prod] [--preview]
```

Options:
- `--prod`: Deploy to production (default)
- `--preview`: Deploy to preview environment

#### Backend Deployment Script

The `deploy-backend.sh` script automates the container deployment process:

```bash
./deploy-backend.sh [platform] [--tag TAG]
```

Arguments:
- `platform`: Target platform (ecs, gcp, railway)
- `--tag`: Docker image tag (default: latest)

## Monitoring and Maintenance

### Health Checks

The backend service includes several health check endpoints:

- `/health`: Returns service health status (used by container orchestration)
- `/ready`: Returns whether the service is ready to accept requests
- `/ping`: Simple ping endpoint

### Logging

- Application logs are output to stdout/stderr
- Set `LOG_LEVEL` environment variable to control verbosity
- Configure log collection in your container platform

### Performance Monitoring

- Frontend: Use Vercel Analytics for performance insights
- Backend: Configure monitoring in your container platform
- Consider implementing APM tools like New Relic or DataDog

## Troubleshooting

### Common Frontend Issues

#### Build Errors
1. Check that all dependencies are in `package.json`
2. Verify environment variables are correctly set
3. Review build logs in the Vercel dashboard
4. Ensure TypeScript compilation succeeds

#### Runtime Errors
1. Check that `NEXT_PUBLIC_API_URL` is accessible
2. Verify the backend API is deployed and accessible
3. Check browser console for client-side errors
4. Verify CORS configuration on the backend

#### Performance Issues
1. Enable Vercel Analytics for performance insights
2. Check Core Web Vitals in the Vercel dashboard
3. Optimize images and large assets
4. Implement code splitting for large components

### Common Backend Issues

#### Container Startup Issues
1. Check that all model artifacts are available
2. Verify environment variables are correctly set
3. Check container logs for error messages
4. Ensure the application binds to the correct port (8000)

#### Model Loading Issues
1. Verify model URLs are accessible (if using cloud storage)
2. Check that model artifacts have correct permissions
3. Ensure sufficient memory is allocated to the container
4. Verify model compatibility with the PyTorch version

#### API Issues
1. Check CORS configuration for your frontend domain
2. Verify API endpoints are correctly configured
3. Check that the health check endpoints return 200 OK
4. Ensure proper error handling is implemented

### Debugging Steps

1. Check logs in your deployment platform
2. Test locally with the same environment variables
3. Use network tools to verify API connectivity
4. Check environment variable values in the deployed environment
5. Verify health check endpoints are accessible

### Getting Help

1. Check this guide for common solutions
2. Review platform-specific documentation
3. Check the application logs for detailed error messages
4. Test with a minimal reproduction case
5. Contact support for your deployment platform if needed

## Next Steps

After successful deployment:

1. Set up custom domains
2. Configure SSL certificates (usually automatic)
3. Set up monitoring and alerting
4. Configure backup and disaster recovery
5. Implement CI/CD pipelines for automated deployments
6. Set up analytics and performance monitoring
7. Configure team access and permissions