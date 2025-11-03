# ============================================================================
# HyFuzz Makefile
# ============================================================================
# Simplifies common development and operational tasks
#
# Usage:
#   make help           Show this help message
#   make install        Install all dependencies
#   make test           Run all tests
#   make lint           Run code quality checks
#   make format         Format code with black and isort
#   make docker-build   Build Docker images
#   make docker-up      Start services with Docker Compose
# ============================================================================

.PHONY: help install install-dev test test-unit test-integration lint format clean docker-build docker-up docker-down health-check init-db run-server run-client run-dashboard run-workers run-campaign

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================
help:
	@echo "HyFuzz Development Tasks"
	@echo "========================"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make init-db          Initialize database"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-cov         Run tests with coverage"
	@echo "  make health-check     Run platform health check"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linters (ruff, mypy)"
	@echo "  make format           Format code (black, isort)"
	@echo "  make format-check     Check code formatting"
	@echo "  make security         Run security checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start all services"
	@echo "  make docker-down      Stop all services"
	@echo "  make docker-logs      View service logs"
	@echo ""
	@echo "Running Services:"
	@echo "  make run-server       Start Windows Server"
	@echo "  make run-client       Start Ubuntu Client"
	@echo "  make run-workers      Start task workers"
	@echo "  make run-dashboard    Start monitoring dashboard"
	@echo "  make run-campaign     Run demo campaign"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache and temp files"
	@echo "  make clean-all        Deep clean (including data)"

# ============================================================================
# Setup & Installation
# ============================================================================
install:
	@echo "Installing production dependencies..."
	pip install -r HyFuzz-Windows-Server/requirements.txt
	pip install -r HyFuzz-Ubuntu-Client/requirements.txt
	@echo "✓ Installation complete"

install-dev: install
	@echo "Installing development dependencies..."
	pip install -r HyFuzz-Windows-Server/requirements-dev.txt
	pip install -r HyFuzz-Ubuntu-Client/requirements-dev.txt
	@echo "✓ Development dependencies installed"

init-db:
	@echo "Initializing database..."
	python scripts/init_database.py --demo-data
	@echo "✓ Database initialized"

# ============================================================================
# Testing
# ============================================================================
test:
	@echo "Running all tests..."
	pytest tests/ -v
	@echo "✓ All tests passed"

test-unit:
	@echo "Running unit tests..."
	pytest tests/ -v -m unit
	@echo "✓ Unit tests passed"

test-integration:
	@echo "Running integration tests..."
	pytest tests/ -v -m integration
	@echo "✓ Integration tests passed"

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=HyFuzz-Windows-Server/src --cov=HyFuzz-Ubuntu-Client/src --cov=coordinator --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated in htmlcov/"

health-check:
	@echo "Running platform health check..."
	python scripts/health_check.py --verbose

# ============================================================================
# Code Quality
# ============================================================================
lint:
	@echo "Running linters..."
	ruff check HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator tests
	mypy HyFuzz-Windows-Server/src coordinator --ignore-missing-imports
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	black HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator tests scripts
	isort HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator tests scripts
	@echo "✓ Code formatted"

format-check:
	@echo "Checking code formatting..."
	black --check HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator tests scripts
	isort --check-only HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator tests scripts
	@echo "✓ Format check passed"

security:
	@echo "Running security checks..."
	bandit -r HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src coordinator -f screen
	safety check
	@echo "✓ Security check complete"

# ============================================================================
# Docker
# ============================================================================
docker-build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✓ Docker images built"

docker-up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo ""
	@echo "Services running at:"
	@echo "  Server:    http://localhost:8080"
	@echo "  Dashboard: http://localhost:8888"
	@echo "  Ollama:    http://localhost:11434"

docker-down:
	@echo "Stopping services..."
	docker-compose down
	@echo "✓ Services stopped"

docker-logs:
	docker-compose logs -f

docker-clean:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	@echo "✓ Docker resources cleaned"

# ============================================================================
# Running Services (Development)
# ============================================================================
run-server:
	@echo "Starting HyFuzz Windows Server..."
	cd HyFuzz-Windows-Server && python scripts/start_server.py

run-client:
	@echo "Starting HyFuzz Ubuntu Client..."
	cd HyFuzz-Ubuntu-Client && python scripts/start_client.py

run-workers:
	@echo "Starting task workers..."
	cd HyFuzz-Windows-Server && python scripts/start_workers.py --concurrency 4

run-dashboard:
	@echo "Starting monitoring dashboard..."
	cd HyFuzz-Windows-Server && python scripts/start_dashboard.py
	@echo "Dashboard available at: http://localhost:8888"

run-campaign:
	@echo "Running demo campaign..."
	cd HyFuzz-Windows-Server && python scripts/run_fuzzing_campaign.py \
		--name demo-campaign \
		--protocol coap \
		--target coap://localhost:5683 \
		--payloads 10

run-coordinator:
	@echo "Running campaign coordinator..."
	python -m coordinator.coordinator --protocol coap --plan configs/campaign_demo.yaml

# ============================================================================
# Cleanup
# ============================================================================
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✓ Cleanup complete"

clean-all: clean
	@echo "Deep cleaning (including logs and results)..."
	rm -rf HyFuzz-Windows-Server/logs/*
	rm -rf HyFuzz-Ubuntu-Client/logs/*
	rm -rf HyFuzz-Windows-Server/results/*
	rm -rf HyFuzz-Ubuntu-Client/results/*
	@echo "✓ Deep clean complete"

# ============================================================================
# Development Helpers
# ============================================================================
shell-server:
	@echo "Opening Python shell with server context..."
	cd HyFuzz-Windows-Server && python -i -c "import sys; sys.path.insert(0, 'src'); from src import *"

shell-client:
	@echo "Opening Python shell with client context..."
	cd HyFuzz-Ubuntu-Client && python -i -c "import sys; sys.path.insert(0, 'src'); from src import *"

docs-serve:
	@echo "Starting documentation server..."
	mkdocs serve

# ============================================================================
# Quick Start
# ============================================================================
quickstart: install init-db health-check
	@echo ""
	@echo "✅ HyFuzz Quick Start Complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Start services:    make run-server (in one terminal)"
	@echo "  2. Start client:      make run-client (in another terminal)"
	@echo "  3. Run campaign:      make run-campaign"
	@echo "  4. View dashboard:    make run-dashboard"
	@echo ""
	@echo "Or use Docker:         make docker-up"

# ============================================================================
# CI/CD Helpers
# ============================================================================
ci: install-dev lint format-check test security
	@echo "✓ All CI checks passed"

pre-commit: format lint test-unit
	@echo "✓ Pre-commit checks passed"
