# Job Matcher App - Deployment Makefile
# This Makefile provides common commands for deploying the application

.PHONY: help check-deployment deploy-frontend deploy-backend deploy-all clean build-frontend build-backend test-frontend test-backend

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# Default values
PLATFORM ?= ecs
TAG ?= latest

help: ## Show this help message
	@echo "$(BLUE)Job Matcher App - Deployment Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make check-deployment          Run pre-deployment checks"
	@echo "  make deploy-frontend            Deploy frontend to Vercel"
	@echo "  make deploy-backend PLATFORM=gcp Deploy backend to Google Cloud Run"
	@echo "  make deploy-all PLATFORM=ecs   Deploy both services to AWS ECS"
	@echo "  make clean                      Clean up build artifacts"

check-deployment: ## Run pre-deployment checks for both services
	@echo "$(BLUE)Running pre-deployment checks...$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend checks:$(NC)"
	@if [ ! -d "frontend" ]; then \
		echo "$(RED)✗ Frontend directory not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Frontend directory found$(NC)"; \
	fi
	@if [ ! -f "frontend/package.json" ]; then \
		echo "$(RED)✗ Frontend package.json not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Frontend package.json found$(NC)"; \
	fi
	@if [ ! -f "frontend/.env.local.example" ]; then \
		echo "$(YELLOW)⚠ Frontend .env.local.example not found$(NC)"; \
	else \
		echo "$(GREEN)✓ Frontend .env.local.example found$(NC)"; \
	fi
	@if [ ! -f "frontend/.env.local" ]; then \
		echo "$(YELLOW)⚠ Frontend .env.local not found$(NC)"; \
		echo "$(BLUE)  Run: cp frontend/.env.local.example frontend/.env.local$(NC)"; \
	else \
		echo "$(GREEN)✓ Frontend .env.local found$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Backend checks:$(NC)"
	@if [ ! -d "backend" ]; then \
		echo "$(RED)✗ Backend directory not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Backend directory found$(NC)"; \
	fi
	@if [ ! -f "backend/app.py" ]; then \
		echo "$(RED)✗ Backend app.py not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Backend app.py found$(NC)"; \
	fi
	@if [ ! -f "backend/requirements.txt" ]; then \
		echo "$(RED)✗ Backend requirements.txt not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Backend requirements.txt found$(NC)"; \
	fi
	@if [ ! -f "backend/Dockerfile" ]; then \
		echo "$(RED)✗ Backend Dockerfile not found$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Backend Dockerfile found$(NC)"; \
	fi
	@if [ ! -f "backend/.env.example" ]; then \
		echo "$(YELLOW)⚠ Backend .env.example not found$(NC)"; \
	else \
		echo "$(GREEN)✓ Backend .env.example found$(NC)"; \
	fi
	@if [ ! -f "backend/.env" ]; then \
		echo "$(YELLOW)⚠ Backend .env not found$(NC)"; \
		echo "$(BLUE)  Run: cp backend/.env.example backend/.env$(NC)"; \
	else \
		echo "$(GREEN)✓ Backend .env found$(NC)"; \
	fi
	@if [ ! -d "backend/artifacts" ]; then \
		echo "$(YELLOW)⚠ Backend artifacts directory not found$(NC)"; \
		echo "$(BLUE)  Make sure model artifacts are available or set cloud storage URLs$(NC)"; \
	else \
		echo "$(GREEN)✓ Backend artifacts directory found$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)✓ Pre-deployment checks completed$(NC)"

build-frontend: ## Build the frontend application
	@echo "$(BLUE)Building frontend application...$(NC)"
	@cd frontend && npm install
	@cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend build completed$(NC)"

build-backend: ## Build the backend Docker image
	@echo "$(BLUE)Building backend Docker image...$(NC)"
	@cd backend && docker build -t job-matcher-backend:$(TAG) .
	@echo "$(GREEN)✓ Backend Docker image built$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	@cd frontend && npm test
	@echo "$(GREEN)✓ Frontend tests completed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	@cd backend && python -m pytest
	@echo "$(GREEN)✓ Backend tests completed$(NC)"

deploy-frontend: ## Deploy frontend to Vercel
	@echo "$(BLUE)Deploying frontend to Vercel...$(NC)"
	@chmod +x deploy-frontend.sh
	@./deploy-frontend.sh --prod
	@echo "$(GREEN)✓ Frontend deployment completed$(NC)"

deploy-backend: ## Deploy backend to container service (PLATFORM=ecs|gcp|railway)
	@echo "$(BLUE)Deploying backend to $(PLATFORM)...$(NC)"
	@chmod +x deploy-backend.sh
	@./deploy-backend.sh $(PLATFORM) --tag $(TAG)
	@echo "$(GREEN)✓ Backend deployment completed$(NC)"

deploy-all: ## Deploy both frontend and backend (PLATFORM=ecs|gcp|railway)
	@echo "$(BLUE)Deploying both frontend and backend...$(NC)"
	@make check-deployment
	@make deploy-backend PLATFORM=$(PLATFORM) TAG=$(TAG)
	@make deploy-frontend
	@echo "$(GREEN)✓ Full deployment completed$(NC)"

deploy-preview: ## Deploy frontend to preview environment
	@echo "$(BLUE)Deploying frontend to preview environment...$(NC)"
	@chmod +x deploy-frontend.sh
	@./deploy-frontend.sh --preview
	@echo "$(GREEN)✓ Frontend preview deployment completed$(NC)"

local-dev: ## Start local development environment
	@echo "$(BLUE)Starting local development environment...$(NC)"
	@echo "$(YELLOW)Starting backend...$(NC)"
	@cd backend && python app.py &
	@echo "$(YELLOW)Starting frontend...$(NC)"
	@cd frontend && npm run dev &
	@echo "$(GREEN)✓ Local development environment started$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8000$(NC)"

local-docker: ## Start local development with Docker Compose
	@echo "$(BLUE)Starting local development with Docker Compose...$(NC)"
	@docker-compose up --build
	@echo "$(GREEN)✓ Local Docker environment started$(NC)"

stop-local: ## Stop local development environment
	@echo "$(BLUE)Stopping local development environment...$(NC)"
	@pkill -f "python app.py" || true
	@pkill -f "npm run dev" || true
	@docker-compose down || true
	@echo "$(GREEN)✓ Local development environment stopped$(NC)"

clean: ## Clean up build artifacts and Docker images
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	@rm -rf frontend/.next
	@rm -rf frontend/node_modules/.cache
	@rm -rf backend/__pycache__
	@rm -rf backend/src/__pycache__
	@docker system prune -f
	@docker image prune -f
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

logs-frontend: ## Show Vercel deployment logs
	@echo "$(BLUE)Fetching Vercel logs...$(NC)"
	@vercel logs frontend

logs-backend: ## Show backend container logs (PLATFORM=ecs|gcp|railway)
	@echo "$(BLUE)Fetching backend logs from $(PLATFORM)...$(NC)"
	@if [ "$(PLATFORM)" = "gcp" ]; then \
		gcloud logs read "resource.type=cloud_run_revision" --limit=50 --format="table(timestamp,textPayload)" ; \
	elif [ "$(PLATFORM)" = "ecs" ]; then \
		aws logs tail /ecs/job-matcher-backend --follow ; \
	elif [ "$(PLATFORM)" = "railway" ]; then \
		railway logs ; \
	else \
		echo "$(RED)Unsupported platform: $(PLATFORM)$(NC)"; \
	fi

status-frontend: ## Check frontend deployment status
	@echo "$(BLUE)Checking frontend deployment status...$(NC)"
	@vercel ls frontend

status-backend: ## Check backend deployment status (PLATFORM=ecs|gcp|railway)
	@echo "$(BLUE)Checking backend deployment status on $(PLATFORM)...$(NC)"
	@if [ "$(PLATFORM)" = "gcp" ]; then \
		gcloud run services list --filter="metadata.name:job-matcher-backend" ; \
	elif [ "$(PLATFORM)" = "ecs" ]; then \
		aws ecs describe-services --cluster job-matcher --services job-matcher-backend ; \
	elif [ "$(PLATFORM)" = "railway" ]; then \
		railway status ; \
	else \
		echo "$(RED)Unsupported platform: $(PLATFORM)$(NC)"; \
	fi

setup-env: ## Set up environment files from examples
	@echo "$(BLUE)Setting up environment files...$(NC)"
	@if [ ! -f "frontend/.env.local" ]; then \
		cp frontend/.env.local.example frontend/.env.local ; \
		echo "$(GREEN)✓ Created frontend/.env.local$(NC)"; \
	else \
		echo "$(YELLOW)⚠ frontend/.env.local already exists$(NC)"; \
	fi
	@if [ ! -f "backend/.env" ]; then \
		cp backend/.env.example backend/.env ; \
		echo "$(GREEN)✓ Created backend/.env$(NC)"; \
	else \
		echo "$(YELLOW)⚠ backend/.env already exists$(NC)"; \
	fi
	@echo "$(GREEN)✓ Environment files setup completed$(NC)"
	@echo "$(YELLOW)Please update the environment files with your values$(NC)"