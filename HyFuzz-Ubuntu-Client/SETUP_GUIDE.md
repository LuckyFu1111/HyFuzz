# HyFuzz MCP Server - Detailed Setup Guide

Complete step-by-step guide for setting up the HyFuzz MCP Server on Windows.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Preparation](#system-preparation)
3. [Python Installation](#python-installation)
4. [Project Setup](#project-setup)
5. [Ollama Installation & Configuration](#ollama-installation--configuration)
6. [Environment Configuration](#environment-configuration)
7. [Verification & Testing](#verification--testing)
8. [IDE Setup (PyCharm)](#ide-setup-pycharm)
9. [Running the Server](#running-the-server)
10. [Advanced Configuration](#advanced-configuration)

## Prerequisites

### Hardware Requirements

- **Processor**: Intel i5/i7 or AMD Ryzen 5/7 (4+ cores recommended)
- **RAM**: 
  - Minimum: 4GB
  - Recommended: 8GB+
  - With GPU: 16GB+
- **Storage**: 
  - Minimum: 2GB free space
  - Recommended: 10GB+ (for models and data)
- **GPU** (Optional): 
  - NVIDIA with CUDA support for faster inference
  - 4GB+ VRAM

### Software Requirements

- **OS**: Windows 10 (Build 19041+) or Windows 11/Server 2019+
- **Python**: 3.9 or later (3.11+ recommended)
- **Git**: For version control (optional)

### Network Requirements

- Stable internet connection (for downloading dependencies and models)
- TCP port 5000 (or configured port) available
- Port 11434 available (for Ollama, if running locally)

## System Preparation

### Step 1: Update Windows
```powershell
# Check Windows Update
Settings → Update & Security → Check for updates

# Update all critical patches
```

### Step 2: Install Prerequisites

#### Option A: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey (if not already installed)
# Run as Administrator in PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

iwr -useb community.chocolatey.org/install.ps1 | iex

# Install Python and Git
choco install python git -y

# Verify installation
python --version
git --version
```

#### Option B: Manual Installation

1. **Python**:
   - Download from https://www.python.org/downloads/
   - Run installer
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"

2. **Git** (optional):
   - Download from https://git-scm.com/download/win
   - Run installer with default options

### Step 3: Verify Python Installation
```powershell
# Check Python version
python --version
# Expected: Python 3.9 or later

# Check pip
pip --version
# Expected: pip 21.0 or later

# Check pip cache location
pip cache dir
```

## Python Installation

### Create Virtual Environment
```powershell
# Open PowerShell as Administrator
# Navigate to project directory
cd C:\path\to\hyfuzz-server-windows

# Create virtual environment
python -m venv venv

# Verify venv creation
dir venv
```

### Activate Virtual Environment
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# You should see (venv) in your command prompt
# Expected: (venv) PS C:\path\to\hyfuzz-server-windows>

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

### Upgrade pip
```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify
pip --version
```

## Project Setup

### Step 1: Clone or Extract Project
```powershell
# Option 1: Clone from repository
git clone https://github.com/your-org/hyfuzz-server-windows.git
cd hyfuzz-server-windows

# Option 2: Extract from ZIP
# Extract the archive and navigate to the directory
cd hyfuzz-server-windows
```

### Step 2: Verify Project Structure
```powershell
# Check key directories exist
dir src
dir tests
dir config
dir data

# Expected directories:
# src/ - source code
# client_tests/ - test suite
# config/ - configuration files
# data/ - data and resources
# logs/ - log files (created on first run)
# scripts/ - utility scripts
```

### Step 3: Install Dependencies
```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Install development dependencies
pip install -r requirements-dev.txt

# This installs:
# - Core dependencies (from requirements.txt)
# - Testing frameworks (pytest, coverage)
# - Code quality tools (black, flake8, mypy)
# - Development utilities

# Verify installation
pip list
```

### Step 4: Create Initial Directories
```powershell
# Create logs directory if it doesn't exist
mkdir -Force logs
mkdir -Force data\knowledge_cache

# Set appropriate permissions
# (Usually not needed on Windows, but good practice)
```

## Ollama Installation & Configuration

### Step 1: Download Ollama

1. Visit https://ollama.ai/
2. Click "Download" for Windows
3. Run the installer
4. Complete installation wizard

### Step 2: Verify Ollama Installation
```powershell
# Check Ollama version
ollama --version

# Should return version number like: ollama version 0.1.x
```

### Step 3: Start Ollama Service
```powershell
# Option 1: Using Ollama GUI
# Click Ollama icon in system tray

# Option 2: Command line
ollama serve

# Ollama will start on http://localhost:11434
# Keep this terminal window open (or run as background service)
```

### Step 4: Pull Model

Open a new PowerShell window and run:
```powershell
# Pull DeepSeek R1 model (recommended)
ollama pull deepseek-r1

# Alternative models:
# ollama pull deepseek-coder
# ollama pull mistral
# ollama pull neural-chat

# This downloads the model (several GB)
# Be patient, it may take 5-30 minutes depending on internet speed
```

### Step 5: Verify Model Installation
```powershell
# List installed models
ollama list

# Expected output:
# NAME              ID              SIZE     MODIFIED
# deepseek-r1       xxxxx           4.0GB    2 minutes ago

# Test model
ollama run deepseek-r1 "Hello, write a poem about programming"
```

## Environment Configuration

### Step 1: Create .env File
```powershell
# Copy template to .env
Copy-Item config\.env.template .env

# Or manually create:
# Open notepad
notepad .env
```

### Step 2: Configure .env File

Edit `.env` and set the following:
```bash
# ============================================================================
# ESSENTIAL CONFIGURATION
# ============================================================================

# Server binding
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Ollama integration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/server.log

# Development
DEBUG=false
ENVIRONMENT=development
```

### Step 3: Verify Configuration
```powershell
# Read and verify .env
type .env

# Check important variables are set
# Especially: OLLAMA_BASE_URL and OLLAMA_MODEL
```

## Verification & Testing

### Step 1: Health Check
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run health check script
python scripts/health_check.py

# Expected output:
# System Health Check
# ✓ Python Environment
# ✓ Virtual Environment
# ✓ Dependencies
# ✓ Ollama Connection
# ✓ Model Availability
# ✓ Configuration Files
# All checks passed!
```

### Step 2: Basic Import Test
```powershell
# Test Python imports
python -c "import src; print('Imports successful')"

# Test specific modules
python -c "from src.config.settings import Settings; print('Config module OK')"
```

### Step 3: Run Unit Tests
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run basic unit tests
pytest client_tests/unit/test_config.py -v

# Run all unit tests
pytest client_tests/unit/ -v
```

## IDE Setup (PyCharm)

### Step 1: Open Project in PyCharm

1. Launch PyCharm
2. File → Open
3. Select project directory (`hyfuzz-server-windows`)
4. Click "Open"

### Step 2: Configure Python Interpreter

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add...
3. Select "Existing Environment"
4. Navigate to: `hyfuzz-server-windows\venv\Scripts\python.exe`
5. Click OK

### Step 3: Create Run Configuration

1. Run → Edit Configurations
2. Click "+" → Python
3. Configure:
   - **Name**: MCP Server Development
   - **Script path**: `src/__main__.py`
   - **Working directory**: `<project root>`
   - **Python interpreter**: Select venv
   - **Environment variables**: 
```
     PYTHONUNBUFFERED=1
     LOG_LEVEL=DEBUG
```
4. Click OK

### Step 4: Mark Source Root

1. Right-click `src` folder
2. Mark Directory as → Sources Root
3. Right-click `tests` folder
4. Mark Directory as → Test Sources Root

### Step 5: Configure Code Style

1. File → Settings → Editor → Code Style → Python
2. Set to: PEP 8 (with max line length 100)
3. Enable optimization imports

## Running the Server

### Option 1: Command Line
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run server
python -m src

# Expected output:
# 2025-01-15 10:30:45 INFO:root:Starting MCP Server...
# 2025-01-15 10:30:45 INFO:root:Configuration loaded
# 2025-01-15 10:30:45 INFO:root:MCP Server started successfully
# 2025-01-15 10:30:45 INFO:root:HTTP server listening on 0.0.0.0:5000
```

### Option 2: PyCharm

1. Open `src/__main__.py`
2. Right-click → Run 'src'
3. Or press Ctrl+Shift+F10

### Option 3: Using Scripts
```powershell
# Using provided start script
python scripts/start_server.py

# Using batch file (Windows-specific)
scripts\start_server.bat
```

### Verify Server is Running

In a new PowerShell window:
```powershell
# Test server connectivity
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0", "timestamp": "2025-01-15T10:31:00Z"}

# Test MCP initialization
curl -X POST http://localhost:5000/mcp/initialize `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"protocolVersion": "2024.01", "clientInfo": {"name": "test", "version": "1.0"}}'
```

## Advanced Configuration

### Using Different Configurations
```powershell
# Run with production config
python -m src --config config/config_prod.yaml

# Run with specific port
python -m src --port 8000

# Run with debug mode
python -m src --debug

# Run with custom log level
set LOG_LEVEL=DEBUG
python -m src
```

### Redis Caching (Optional)

1. Install Redis:
```powershell
   choco install redis-64 -y
```

2. Update .env:
```bash
   CACHE_BACKEND=redis
   REDIS_URL=redis://localhost:6379
```

3. Start Redis:
```powershell
   redis-server
```

### Docker Deployment (Optional)
```powershell
# Build Docker image
docker build -t hyfuzz-server:latest .

# Run in Docker
docker run -p 5000:5000 hyfuzz-server:latest

# Or use docker-compose
docker-compose up
```

## Next Steps

1. **Verify Installation**: Run health check script
2. **Run Tests**: Execute test suite
3. **Try Examples**: Review example configurations
4. **Read Documentation**: Check `docs/` folder
5. **Configure Client**: Set up Ubuntu MCP Client

## Troubleshooting

### Common Setup Issues

**Issue: "python is not recognized"**
- Solution: Reinstall Python with "Add to PATH" checked

**Issue: "pip: command not found"**
- Solution: Use `python -m pip` instead

**Issue: "cannot open file venv/Scripts/Activate.ps1"**
- Solution: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

**Issue: "Ollama connection refused"**
- Solution: Ensure Ollama is running: `ollama serve`

**Issue: "Model not found"**
- Solution: Pull model: `ollama pull deepseek-r1`

For more troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Getting Help

1. Check [README.md](README.md)
2. Review [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Check existing GitHub issues
4. Create new GitHub issue with error details

---

**Last Updated**: January 2025
**Version**: 1.0.0