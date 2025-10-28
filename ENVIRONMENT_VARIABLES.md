# Environment Variables Documentation

This document provides detailed information about all environment variables required for the Job Matcher application.

## Table of Contents

1. [Frontend Environment Variables](#frontend-environment-variables)
2. [Backend Environment Variables](#backend-environment-variables)
3. [Environment Setup](#environment-setup)
4. [Security Considerations](#security-considerations)
5. [Platform-Specific Configuration](#platform-specific-configuration)

## Frontend Environment Variables

The frontend application uses Next.js environment variables to configure its behavior. These variables are defined in the `.env.local` file in the `frontend/` directory.

### Required Variables

#### NEXT_PUBLIC_API_URL
- **Description**: The URL of the backend API service
- **Format**: `https://your-backend-domain.com` or `http://localhost:8000` for development
- **Example**: `NEXT_PUBLIC_API_URL=https://api.jobmatcher.com`
- **Notes**: 
  - Must include the protocol (http:// or https://)
  - The `NEXT_PUBLIC_` prefix is required for Next.js to expose the variable to the browser
  - Should be updated for each deployment environment

### Optional Variables

#### NEXT_PUBLIC_APP_NAME
- **Description**: The name of the application (used in meta tags and page titles)
- **Format**: String
- **Example**: `NEXT_PUBLIC_APP_NAME=Job Matcher`
- **Default**: `Job Matcher`

#### NEXT_PUBLIC_APP_VERSION
- **Description**: The version of the application (for debugging and caching)
- **Format**: Semantic version (e.g., `1.0.0`)
- **Example**: `NEXT_PUBLIC_APP_VERSION=1.0.0`
- **Default**: `1.0.0`

#### NEXT_PUBLIC_SENTRY_DSN
- **Description**: Sentry DSN for error tracking (optional)
- **Format**: Sentry DSN URL
- **Example**: `NEXT_PUBLIC_SENTRY_DSN=https://your-dsn@sentry.io/project-id`
- **Notes**: Only required if using Sentry for error tracking

#### NEXT_PUBLIC_GOOGLE_ANALYTICS_ID
- **Description**: Google Analytics tracking ID (optional)
- **Format**: `GA-XXXXXXXXX`
- **Example**: `NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-123456789`
- **Notes**: Only required if using Google Analytics

## Backend Environment Variables

The backend application uses environment variables to configure its behavior, including model paths, API settings, and logging. These variables are defined in the `.env` file in the `backend/` directory.

### Model Configuration

#### ARTIFACT_DIR
- **Description**: Directory where model artifacts are stored
- **Format**: Absolute path
- **Example**: `ARTIFACT_DIR=/app/backend/artifacts`
- **Default**: `/app/backend/artifacts`
- **Notes**: 
  - This is the base directory for all model files
  - In containerized environments, this should match the path in the Dockerfile

#### MODEL_URL
- **Description**: URL to download the fine-tuned PhoBERT model weights
- **Format**: HTTP/HTTPS URL
- **Example**: `MODEL_URL=https://storage.googleapis.com/models/phobert_best.pt`
- **Optional**: Yes
- **Notes**: 
  - If provided, the model will be downloaded from this URL if not present locally
  - Should be a direct download link to the model file
  - Supports cloud storage URLs (AWS S3, Google Cloud Storage, etc.)

#### TOKENIZER_URL
- **Description**: URL to download the tokenizer files
- **Format**: HTTP/HTTPS URL to a zip file
- **Example**: `TOKENIZER_URL=https://storage.googleapis.com/tokenizers/tokenizer.zip`
- **Optional**: Yes
- **Notes**: 
  - If provided, the tokenizer will be downloaded and extracted
  - Should point to a zip file containing all tokenizer files
  - The zip should contain the tokenizer directory structure

#### BASE_MODEL_URL
- **Description**: URL to download the base PhoBERT model
- **Format**: HTTP/HTTPS URL to a zip file
- **Example**: `BASE_MODEL_URL=https://storage.googleapis.com/models/base_model.zip`
- **Optional**: Yes
- **Notes**: 
  - Only needed if the base model is not included in the container
  - Should point to a zip file containing the base model files

#### PHOBERT_BASE_DIR
- **Description**: Local path to the base PhoBERT model
- **Format**: Absolute path
- **Example**: `PHOBERT_BASE_DIR=/models/phobert-base`
- **Optional**: Yes
- **Notes**: 
  - Used when the base model is stored locally
  - Alternative to using BASE_MODEL_URL
  - Should point to the directory containing the base model files

### API Configuration

#### ALLOWED_ORIGINS
- **Description**: Comma-separated list of allowed origins for CORS
- **Format**: Comma-separated URLs
- **Example**: `ALLOWED_ORIGINS=https://jobmatcher.com,https://www.jobmatcher.com`
- **Default**: `http://localhost:3000,http://127.0.0.1:3000`
- **Notes**: 
  - Include all domains that need to access the API
  - For production, include your frontend domain(s)
  - Don't include trailing slashes

#### ALLOWED_METHODS
- **Description**: Comma-separated list of allowed HTTP methods for CORS
- **Format**: Comma-separated HTTP methods
- **Example**: `ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS`
- **Default**: `GET,POST,PUT,DELETE,OPTIONS`
- **Notes**: 
  - Include all HTTP methods your API supports
  - OPTIONS is required for preflight requests

#### ALLOWED_HEADERS
- **Description**: Comma-separated list of allowed headers for CORS
- **Format**: Comma-separated header names or `*` for all
- **Example**: `ALLOWED_HEADERS=Content-Type,Authorization`
- **Default**: `*`
- **Notes**: 
  - Use `*` to allow all headers (less secure)
  - Specify exact headers for better security

#### API_HOST
- **Description**: Host address for the API server
- **Format**: IP address or hostname
- **Example**: `API_HOST=0.0.0.0`
- **Default**: `0.0.0.0`
- **Notes**: 
  - Use `0.0.0.0` to listen on all interfaces
  - Use `127.0.0.1` to listen only on localhost

#### API_PORT
- **Description**: Port number for the API server
- **Format**: Port number
- **Example**: `API_PORT=8000`
- **Default**: `8000`
- **Notes**: 
  - Must match the port exposed in the Dockerfile
  - Ensure the port is not blocked by firewalls

### Logging Configuration

#### LOG_LEVEL
- **Description**: Logging level for the application
- **Format**: Logging level name
- **Example**: `LOG_LEVEL=INFO`
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Notes**: 
  - Use `DEBUG` for detailed debugging information
  - Use `INFO` for normal operation
  - Use `WARNING` or higher for production

#### LOG_FORMAT
- **Description**: Log format for the application
- **Format**: Format string
- **Example**: `LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Notes**: 
  - Follows Python logging format conventions
  - Can be customized to match your logging system

### Database Configuration (Optional)

#### DATABASE_URL
- **Description**: Database connection URL
- **Format**: Database connection string
- **Example**: `DATABASE_URL=postgresql://user:password@localhost:5432/jobmatcher`
- **Optional**: Yes
- **Notes**: 
  - Only required if using a database
  - Supports PostgreSQL, MySQL, SQLite, etc.

#### REDIS_URL
- **Description**: Redis connection URL for caching
- **Format**: Redis connection string
- **Example**: `REDIS_URL=redis://localhost:6379/0`
- **Optional**: Yes
- **Notes**: 
  - Only required if using Redis for caching
  - Used for session storage and caching

### Security Configuration

#### SECRET_KEY
- **Description**: Secret key for cryptographic operations
- **Format**: Random string
- **Example**: `SECRET_KEY=your-secret-key-here`
- **Optional**: Yes
- **Notes**: 
  - Used for session management and token generation
  - Should be a long, random string
  - Keep this value secret and secure

#### JWT_SECRET_KEY
- **Description**: Secret key for JWT token signing
- **Format**: Random string
- **Example**: `JWT_SECRET_KEY=your-jwt-secret-key-here`
- **Optional**: Yes
- **Notes**: 
  - Only required if using JWT authentication
  - Should be different from SECRET_KEY
  - Keep this value secret and secure

#### JWT_ALGORITHM
- **Description**: Algorithm for JWT token signing
- **Format**: JWT algorithm name
- **Example**: `JWT_ALGORITHM=HS256`
- **Default**: `HS256`
- **Options**: `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`
- **Notes**: 
  - Use HS algorithms for symmetric key signing
  - Use RS algorithms for asymmetric key signing

#### JWT_EXPIRATION_MINUTES
- **Description**: JWT token expiration time in minutes
- **Format**: Integer
- **Example**: `JWT_EXPIRATION_MINUTES=30`
- **Default**: `30`
- **Notes**: 
  - Shorter expiration times are more secure
  - Consider refresh tokens for longer sessions

## Environment Setup

### Frontend Environment Setup

1. Create the environment file:
   ```bash
   cd frontend
   cp .env.local.example .env.local
   ```

2. Edit the `.env.local` file with your values:
   ```bash
   # Required
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   
   # Optional
   NEXT_PUBLIC_APP_NAME=Job Matcher
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```

3. Restart the development server after making changes.

### Backend Environment Setup

1. Create the environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit the `.env` file with your values:
   ```bash
   # Model Configuration
   ARTIFACT_DIR=/app/backend/artifacts
   MODEL_URL=https://your-storage.com/models/phobert_best.pt
   TOKENIZER_URL=https://your-storage.com/tokenizers/tokenizer.zip
   
   # API Configuration
   ALLOWED_ORIGINS=https://your-frontend-domain.com
   ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
   ALLOWED_HEADERS=Content-Type,Authorization
   
   # Logging
   LOG_LEVEL=INFO
   ```

3. Restart the application after making changes.

## Security Considerations

### Sensitive Data
- Never commit environment files to version control
- Use different values for development and production
- Rotate secret keys regularly
- Use strong, random values for secret keys

### Access Control
- Limit access to environment variables in production
- Use IAM roles to control access to cloud resources
- Implement least privilege access for API keys

### Validation
- Validate environment variables on application startup
- Provide clear error messages for missing or invalid variables
- Use default values where appropriate

## Platform-Specific Configuration

### Vercel (Frontend)

1. In the Vercel dashboard, go to **Settings** > **Environment Variables**
2. Add each variable with the appropriate environment (Production, Preview, Development)
3. Redeploy the application to apply changes

### AWS ECS (Backend)

1. In the ECS task definition, add environment variables to the container definition
2. Use AWS Secrets Manager for sensitive values
3. Update the task definition and redeploy the service

### Google Cloud Run (Backend)

1. Use the `--set-env-vars` flag when deploying:
   ```bash
   gcloud run deploy service-name \
     --set-env-vars "VAR1=value1,VAR2=value2"
   ```

2. Use Google Secret Manager for sensitive values

### Railway (Backend)

1. In the Railway dashboard, go to **Settings** > **Variables**
2. Add each variable with the appropriate value
3. Railway will automatically apply the changes on the next deployment

## Environment Variable Templates

### Development Environment

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Job Matcher (Dev)
NEXT_PUBLIC_APP_VERSION=1.0.0-dev
```

#### Backend (.env)
```bash
ARTIFACT_DIR=./artifacts
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*
LOG_LEVEL=DEBUG
```

### Production Environment

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://api.jobmatcher.com
NEXT_PUBLIC_APP_NAME=Job Matcher
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-123456789
```

#### Backend (.env)
```bash
ARTIFACT_DIR=/app/backend/artifacts
MODEL_URL=https://storage.googleapis.com/jobmatcher-models/phobert_best.pt
TOKENIZER_URL=https://storage.googleapis.com/jobmatcher-models/tokenizer.zip
ALLOWED_ORIGINS=https://jobmatcher.com,https://www.jobmatcher.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization
LOG_LEVEL=INFO
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret
```

## Troubleshooting

### Common Issues

1. **Environment variables not loading**
   - Check that the environment file exists
   - Verify the file name and location
   - Ensure the file format is correct

2. **CORS errors**
   - Verify ALLOWED_ORIGINS includes the frontend domain
   - Check for typos in domain names
   - Ensure the protocol (http/https) matches

3. **Model loading failures**
   - Verify MODEL_URL and TOKENIZER_URL are accessible
   - Check that ARTIFACT_DIR exists and is writable
   - Ensure sufficient disk space for model files

4. **Permission errors**
   - Check file permissions for ARTIFACT_DIR
   - Verify the application has read access to model files
   - Ensure the container user has appropriate permissions

### Debugging Environment Variables

#### Frontend
```bash
# Check if variables are loaded in the browser
console.log(process.env.NEXT_PUBLIC_API_URL);
```

#### Backend
```python
# Check if variables are loaded
import os
print(f"ARTIFACT_DIR: {os.getenv('ARTIFACT_DIR')}")
print(f"ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS')}")
```

For more troubleshooting information, refer to the [Deployment Guide](DEPLOYMENT_GUIDE.md).