#!/bin/bash

# Job Matcher Frontend Deployment Script
# This script automates the deployment of the frontend to Vercel

set -e  # Exit on any error

# Default values
ENVIRONMENT="production"
PROJECT_DIR="frontend"
VERCEL_CLI="vercel"

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
        --prod)
            ENVIRONMENT="production"
            shift
            ;;
        --preview)
            ENVIRONMENT="preview"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--prod|--preview] [--help]"
            echo ""
            echo "Options:"
            echo "  --prod      Deploy to production (default)"
            echo "  --preview   Deploy to preview environment"
            echo "  --help, -h  Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main deployment function
deploy_frontend() {
    print_header "Starting Frontend Deployment to Vercel"
    
    # Check if Vercel CLI is installed
    if ! command -v $VERCEL_CLI &> /dev/null; then
        print_error "Vercel CLI is not installed"
        print_info "Install it with: npm i -g vercel"
        exit 1
    fi
    print_success "Vercel CLI is installed"
    
    # Check if we're in the right directory
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Project directory '$PROJECT_DIR' not found"
        print_info "Please run this script from the root of the repository"
        exit 1
    fi
    print_success "Project directory found"
    
    # Navigate to the frontend directory
    cd $PROJECT_DIR
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in $PROJECT_DIR"
        exit 1
    fi
    print_success "package.json found"
    
    # Check if .env.local.example exists
    if [ ! -f ".env.local.example" ]; then
        print_warning ".env.local.example not found"
    else
        print_success ".env.local.example found"
        
        # Check if .env.local exists
        if [ ! -f ".env.local" ]; then
            print_warning ".env.local not found, creating from example"
            cp .env.local.example .env.local
            print_warning "Please update .env.local with your backend API URL"
            print_info "Required variable: NEXT_PUBLIC_API_URL"
        else
            print_success ".env.local found"
            
            # Check if NEXT_PUBLIC_API_URL is set
            if ! grep -q "NEXT_PUBLIC_API_URL=" .env.local; then
                print_warning "NEXT_PUBLIC_API_URL not found in .env.local"
            elif grep -q "NEXT_PUBLIC_API_URL=http://localhost:8000" .env.local && [ "$ENVIRONMENT" = "production" ]; then
                print_warning "NEXT_PUBLIC_API_URL is set to localhost in production"
                print_info "Please update it with your production backend URL"
            fi
        fi
    fi
    
    # Install dependencies
    print_info "Installing dependencies..."
    if npm install; then
        print_success "Dependencies installed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
    
    # Run build to check for errors
    print_info "Running build check..."
    if npm run build; then
        print_success "Build successful"
    else
        print_error "Build failed"
        exit 1
    fi
    
    # Check if vercel.json exists
    if [ ! -f "vercel.json" ]; then
        print_warning "vercel.json not found, using default configuration"
    else
        print_success "vercel.json found"
    fi
    
    # Deploy to Vercel
    print_info "Deploying to Vercel ($ENVIRONMENT environment)..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        if vercel --prod; then
            print_success "Deployment to production successful"
        else
            print_error "Production deployment failed"
            exit 1
        fi
    else
        if vercel; then
            print_success "Deployment to preview successful"
        else
            print_error "Preview deployment failed"
            exit 1
        fi
    fi
    
    # Get the deployment URL
    DEPLOYMENT_URL=$(vercel ls $PROJECT_DIR 2>/dev/null | head -n 1 | awk '{print $2}' || echo "")
    if [ -n "$DEPLOYMENT_URL" ]; then
        print_success "Deployment URL: https://$DEPLOYMENT_URL"
    fi
    
    print_header "Frontend Deployment Complete"
    print_info "Next steps:"
    print_info "1. Update your backend CORS configuration to include the new frontend URL"
    print_info "2. Test the application to ensure everything works correctly"
    print_info "3. Set up a custom domain if needed"
}

# Run the deployment
deploy_frontend