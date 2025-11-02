# ============================================================================
# HyFuzz MCP Server - Makefile
# ============================================================================
# Common development and deployment commands
# Usage: make <target>
# ============================================================================

.PHONY: help install install-dev clean test lint format type-check run debug docs

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Variables
# ============================================================================

PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
SPHINX := sphinx-build

# Directories
SRC_DIR := src
TESTS_DIR := client_tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist

# ============================================================================
# Help Target
# ============================================================================

help:
	@echo "HyFuzz MCP Server - Makefile Targets"
	@echo "===================================="
	@echo ""
	@echo "Installation & Setup:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make clean            - Clean project directories"
	@echo ""
	@echo "Development:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run linter (flake8)"
	@echo "  make format           - Format code with black"
	@echo "  make format-check     - Check code formatting"
	@echo "  make type-check       - Run type checker (mypy)"
	@echo "  make quality          - Run all quality checks"
	@echo ""
	@echo "Running:"
	@echo "  make run              - Run server in production mode"
	@echo "  make debug            - Run server in debug mode"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             - Build documentation"
	@echo "  make docs-serve       - Build and serve documentation"
	@echo ""
	@echo "Utilities:"
	@echo "  make health-check     - Run health check script"
	@echo "  make build            - Build distribution packages"
	@echo "  make venv             - Create virtual environment"
	@echo ""

# ============================================================================
# Installation Targets
# ============================================================================

install:
	$(PIP) install -r requirements.txt
	@echo "✓ Production dependencies installed"

install-dev:
	$(PIP) install -r requirements-dev.txt
	@echo "✓ Development dependencies installed"

venv:
	$(PYTHON) -m venv venv
	@echo "✓ Virtual environment created"
	@echo "Activate with: .\venv\Scripts\activate"

# ============================================================================
# Cleaning Targets
# ============================================================================

clean:
	@echo "Cleaning project directories..."
	rm -rf build/ dist/ *.egg-info .eggs/
	rm -rf .pytest_cache .coverage .mypy_cache .tox
	rm -rf htmlcov .hypothesis
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	@echo "✓ Directories cleaned"

clean-logs:
	rm -f logs/*.log
	@echo "✓ Log files removed"

# ============================================================================
# Testing Targets
# ============================================================================

test:
	$(PYTEST) $(TESTS_DIR) -v
	@echo "✓ All tests passed"

test-unit:
	$(PYTEST) $(TESTS_DIR)/unit -v
	@echo "✓ Unit tests passed"

test-integration:
	$(PYTEST) $(TESTS_DIR)/integration -v
	@echo "✓ Integration tests passed"

test-coverage:
	$(PYTEST) $(TESTS_DIR) -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated (htmlcov/index.html)"

test-watch:
	pytest-watch $(TESTS_DIR) -v
	@echo "✓ Tests running in watch mode"

# ============================================================================
# Code Quality Targets
# ============================================================================

lint:
	$(FLAKE8) $(SRC_DIR) $(TESTS_DIR) --max-line-length=100
	@echo "✓ Linting passed"

format:
	$(BLACK) $(SRC_DIR) $(TESTS_DIR) --line-length=100
	@echo "✓ Code formatted"

format-check:
	$(BLACK) $(SRC_DIR) $(TESTS_DIR) --line-length=100 --check
	@echo "✓ Code formatting is valid"

type-check:
	$(MYPY) $(SRC_DIR) --ignore-missing-imports
	@echo "✓ Type checking passed"

quality: format lint type-check test
	@echo "✓ All quality checks passed"

# ============================================================================
# Running Targets
# ============================================================================

run:
	$(PYTHON) -m $(SRC_DIR)
	@echo "✓ Server stopped"

debug:
	DEBUG=true LOG_LEVEL=DEBUG $(PYTHON) -m $(SRC_DIR)
	@echo "✓ Server stopped"

run-port:
	$(PYTHON) -m $(SRC_DIR) --port 8000
	@echo "✓ Server stopped"

# ============================================================================
# Documentation Targets
# ============================================================================

docs:
	cd $(DOCS_DIR) && $(SPHINX) -b html . _build/html
	@echo "✓ Documentation built ($(DOCS_DIR)/_build/html/index.html)"

docs-clean:
	rm -rf $(DOCS_DIR)/_build
	@echo "✓ Documentation cleaned"

docs-serve:
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000
	@echo "Documentation server running on http://localhost:8000"

# ============================================================================
# Build & Distribution Targets
# ============================================================================

build:
	$(PYTHON) -m build
	@echo "✓ Distribution packages built"

dist-upload:
	python -m twine upload dist/*
	@echo "✓ Packages uploaded"

# ============================================================================
# Utility Targets
# ============================================================================

health-check:
	$(PYTHON) scripts/health_check.py
	@echo "✓ Health check completed"

setup-env:
	$(PYTHON) scripts/setup_env.py
	@echo "✓ Environment setup completed"

setup-ollama:
	$(PYTHON) scripts/setup_ollama.py
	@echo "✓ Ollama setup completed"

benchmark:
	$(PYTHON) scripts/benchmark.py
	@echo "✓ Benchmark completed"

requirements-update:
	$(PIP) list --outdated
	@echo "Run: pip install -U -r requirements.txt"

requirements-lock:
	$(PIP) freeze > requirements.lock
	@echo "✓ Requirements locked"

# ============================================================================
# Development Workflow Targets
# ============================================================================

dev-setup: venv install-dev
	@echo "✓ Development environment ready"
	@echo "Activate with: .\venv\Scripts\activate"

dev-check: lint type-check
	@echo "✓ Development checks passed"

pre-commit: format lint
	@echo "✓ Pre-commit checks passed"

# ============================================================================
# CI/CD Targets
# ============================================================================

ci: lint type-check test
	@echo "✓ CI pipeline passed"

release: clean build
	@echo "✓ Release packages ready"

# ============================================================================
# Notes
# ============================================================================

# Note 1: Windows Compatibility
# On Windows, some commands may need modification:
# - Use 'del' instead of 'rm' for file deletion
# - Use 'rmdir /s /q' instead of 'rm -rf' for directory deletion
# - Path separators: use '\\' or '/'
#
# Note 2: Make Installation
# Windows users can install GNU Make via:
# - Chocolatey: choco install make
# - MinGW: Download from mingw-w64.org
# - Or use nmake with appropriate modifications
#
# Note 3: Python Version
# Ensure Python 3.9+ is installed and in PATH
# Check with: python --version
#
# Note 4: Virtual Environment
# Always activate venv before running make commands:
# .\venv\Scripts\activate  (Windows)
# source venv/bin/activate (Linux/Mac)

# ============================================================================
# End of Makefile
# ============================================================================