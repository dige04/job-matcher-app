#!/bin/bash

# Job Matcher Backend Deployment Script
# This script automates the deployment of the backend to various container services

set -e  # Exit on any error

# Default values
PLATFORM=""
TAG="latest"
PROJECT_DIR="backend"
IMAGE_NAME="job-matcher-backend"
REGISTRY=""
PROJECT_ID=""
REGION="us-central1"
AWS_ACCOUNT_ID=""
AWS_REGION="us-west-2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        ecs|gcp|railway)
            PLATFORM="$1"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --aws-account-id)
            AWS_ACCOUNT_ID="$2"
            shift 2
            ;;
        --aws-region)
            AWS_REGION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [platform] [options]"
            echo ""
            echo "Platforms:"
            echo "  ecs      Deploy to Amazon ECS"
            echo "  gcp      Deploy to Google Cloud Run"
            echo "  railway  Deploy to Railway"
            echo ""
            echo "Options:"
            echo "  --tag TAG              Docker image tag (default: latest)"
            echo "  --registry REGISTRY    Container registry URL"
            echo "  --project-id ID        Google Cloud project ID (for GCP)"
            echo "  --region REGION        Deployment region (default: us-central1)"
            echo "  --aws-account-id ID    AWS account ID (for ECS)"
            echo "  --aws-region REGION    AWS region (default: us-west-2)"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate platform
if [ -z "$PLATFORM" ]; then
    print_error "Platform is required"
    echo "Supported platforms: ecs, gcp, railway"
    echo "Use --help for usage information"
    exit 1
fi

# Pre-deployment checks
pre_deployment_checks() {
    print_header "Running Pre-Deployment Checks"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check if we're in the right directory
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Project directory '$PROJECT_DIR' not found"
        print_info "Please run this script from the root of the repository"
        exit 1
    fi
    print_success "Project directory found"
    
    # Navigate to the backend directory
    cd $PROJECT_DIR
    
    # Check if Dockerfile exists
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found in $PROJECT_DIR"
        exit 1
    fi
    print_success "Dockerfile found"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found in $PROJECT_DIR"
        exit 1
    fi
    print_success "requirements.txt found"
    
    # Check if .env.example exists
    if [ ! -f ".env.example" ]; then
        print_warning ".env.example not found"
    else
        print_success ".env.example found"
        
        # Check if .env exists
        if [ ! -f ".env" ]; then
            print_warning ".env not found, creating from example"
            cp .env.example .env
            print_warning "Please update .env with your production values"
        else
            print_success ".env found"
        fi
    fi
    
    # Check if artifacts directory exists
    if [ ! -d "artifacts" ]; then
        print_warning "Artifacts directory not found"
        print_info "Make sure model artifacts are available or set cloud storage URLs"
    else
        print_success "Artifacts directory found"
    fi
    
    # Check if app.py exists
    if [ ! -f "app.py" ]; then
        print_error "app.py not found in $PROJECT_DIR"
        exit 1
    fi
    print_success "app.py found"
    
    cd ..
}

# Build Docker image
build_image() {
    print_header "Building Docker Image"
    
    cd $PROJECT_DIR
    
    # Build the Docker image
    print_info "Building Docker image: $IMAGE_NAME:$TAG"
    if docker build -t $IMAGE_NAME:$TAG .; then
        print_success "Docker image built successfully"
    else
        print_error "Docker image build failed"
        exit 1
    fi
    
    cd ..
}

# Deploy to AWS ECS
deploy_to_ecs() {
    print_header "Deploying to AWS ECS"
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        print_info "Install it with: pip install awscli"
        exit 1
    fi
    
    # Set default AWS account ID if not provided
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        if [ -z "$AWS_ACCOUNT_ID" ]; then
            print_error "Could not determine AWS account ID"
            print_info "Please provide it with --aws-account-id"
            exit 1
        fi
    fi
    
    # Set default registry if not provided
    if [ -z "$REGISTRY" ]; then
        REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    fi
    
    # Login to ECR
    print_info "Logging in to Amazon ECR..."
    if aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REGISTRY; then
        print_success "Successfully logged in to ECR"
    else
        print_error "Failed to log in to ECR"
        exit 1
    fi
    
    # Tag the image for ECR
    print_info "Tagging image for ECR..."
    if docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:$TAG; then
        print_success "Image tagged successfully"
    else
        print_error "Failed to tag image"
        exit 1
    fi
    
    # Push the image to ECR
    print_info "Pushing image to ECR..."
    if docker push $REGISTRY/$IMAGE_NAME:$TAG; then
        print_success "Image pushed successfully to ECR"
    else
        print_error "Failed to push image to ECR"
        exit 1
    fi
    
    print_header "ECS Deployment Instructions"
    print_info "Manual steps required:"
    print_info "1. Create or update ECS task definition with image: $REGISTRY/$IMAGE_NAME:$TAG"
    print_info "2. Update the ECS service with the new task definition"
    print_info "3. Configure environment variables in the task definition"
    print_info "4. Set up Application Load Balancer with health checks"
    print_info "5. Configure health check endpoint: /health"
}

# Deploy to Google Cloud Run
deploy_to_gcp() {
    print_header "Deploying to Google Cloud Run"
    
    # Check if gcloud CLI is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed"
        print_info "Install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Set default project ID if not provided
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "Could not determine Google Cloud project ID"
            print_info "Please provide it with --project-id"
            exit 1
        fi
    fi
    
    # Set default registry if not provided
    if [ -z "$REGISTRY" ]; then
        REGISTRY="gcr.io/$PROJECT_ID"
    fi
    
    # Tag the image for GCR
    print_info "Tagging image for Google Container Registry..."
    if docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:$TAG; then
        print_success "Image tagged successfully"
    else
        print_error "Failed to tag image"
        exit 1
    fi
    
    # Push the image to GCR
    print_info "Pushing image to Google Container Registry..."
    if docker push $REGISTRY/$IMAGE_NAME:$TAG; then
        print_success "Image pushed successfully to GCR"
    else
        print_error "Failed to push image to GCR"
        exit 1
    fi
    
    # Deploy to Cloud Run
    print_info "Deploying to Cloud Run..."
    if gcloud run deploy $IMAGE_NAME \
        --image $REGISTRY/$IMAGE_NAME:$TAG \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated; then
        print_success "Deployment to Cloud Run successful"
    else
        print_error "Deployment to Cloud Run failed"
        exit 1
    fi
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $IMAGE_NAME --region $REGION --format 'value(status.url)')
    if [ -n "$SERVICE_URL" ]; then
        print_success "Service URL: $SERVICE_URL"
    fi
}

# Deploy to Railway
deploy_to_railway() {
    print_header "Deploying to Railway"
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed"
        print_info "Install it with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if logged in to Railway
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway"
        print_info "Login with: railway login"
        exit 1
    fi
    
    # Initialize Railway project if needed
    if [ ! -f "railway.json" ] && [ ! -f "railway.toml" ]; then
        print_info "Initializing Railway project..."
        if railway init; then
            print_success "Railway project initialized"
        else
            print_error "Failed to initialize Railway project"
            exit 1
        fi
    fi
    
    # Deploy to Railway
    print_info "Deploying to Railway..."
    if railway up; then
        print_success "Deployment to Railway successful"
    else
        print_error "Deployment to Railway failed"
        exit 1
    fi
    
    # Get the service URL
    SERVICE_URL=$(railway status 2>/dev/null | grep -E "(URL|Domain)" | head -n 1 | awk '{print $3}' || echo "")
    if [ -n "$SERVICE_URL" ]; then
        print_success "Service URL: $SERVICE_URL"
    fi
}

# Main deployment function
deploy_backend() {
    print_header "Starting Backend Deployment to $PLATFORM"
    
    # Run pre-deployment checks
    pre_deployment_checks
    
    # Build Docker image
    build_image
    
    # Deploy to the specified platform
    case $PLATFORM in
        ecs)
            deploy_to_ecs
            ;;
        gcp)
            deploy_to_gcp
            ;;
        railway)
            deploy_to_railway
            ;;
        *)
            print_error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
    
    print_header "Backend Deployment Complete"
    print_info "Next steps:"
    print_info "1. Update your frontend environment variable NEXT_PUBLIC_API_URL"
    print_info "2. Test the API endpoints to ensure everything works correctly"
    print_info "3. Set up monitoring and alerting"
    print_info "4. Configure backup and disaster recovery"
}

# Run the deployment
deploy_backend