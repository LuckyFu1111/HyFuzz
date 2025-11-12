#!/bin/bash
################################################################################
# HyFuzz Deployment Script
################################################################################
# Automates the deployment process for HyFuzz server
#
# Usage:
#   ./scripts/deploy.sh [environment] [options]
#
# Environments:
#   staging     - Deploy to staging environment
#   production  - Deploy to production environment
#
# Options:
#   --skip-tests     - Skip running tests
#   --skip-backup    - Skip backup creation
#   --force          - Force deployment without confirmation
#
# Example:
#   ./scripts/deploy.sh staging
#   ./scripts/deploy.sh production --force
#
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
ENVIRONMENT="${1:-staging}"
SKIP_TESTS=false
SKIP_BACKUP=false
FORCE=false

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm() {
    if [ "$FORCE" = true ]; then
        return 0
    fi

    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled by user"
        exit 1
    fi
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "Required command '$1' not found"
        exit 1
    fi
}

################################################################################
# Pre-flight Checks
################################################################################

log_info "Starting HyFuzz deployment to $ENVIRONMENT..."
echo

# Check required commands
log_info "Checking required commands..."
check_command python
check_command git
check_command pip

# Check we're in the right directory
if [ ! -f "$PROJECT_ROOT/setup.py" ]; then
    log_error "Not in HyFuzz project root directory"
    exit 1
fi

# Check environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Invalid environment: $ENVIRONMENT (must be 'staging' or 'production')"
    exit 1
fi

# Check .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_error ".env file not found!"
    log_error "Please create .env from .env.example and configure it"
    exit 1
fi

# Check JWT_SECRET_KEY is set
if ! grep -q "JWT_SECRET_KEY=" "$PROJECT_ROOT/.env" || grep -q "JWT_SECRET_KEY=your-secret-key-here" "$PROJECT_ROOT/.env"; then
    log_error "JWT_SECRET_KEY not properly configured in .env!"
    exit 1
fi

log_success "Pre-flight checks passed"
echo

################################################################################
# Confirmation
################################################################################

echo "=========================================="
echo "Deployment Configuration:"
echo "=========================================="
echo "Environment:  $ENVIRONMENT"
echo "Project Root: $PROJECT_ROOT"
echo "Skip Tests:   $SKIP_TESTS"
echo "Skip Backup:  $SKIP_BACKUP"
echo "Git Branch:   $(git branch --show-current)"
echo "Git Commit:   $(git rev-parse --short HEAD)"
echo "=========================================="
echo

confirm "Proceed with deployment?"

################################################################################
# Backup
################################################################################

if [ "$SKIP_BACKUP" = false ]; then
    log_info "Creating backup..."

    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_${ENVIRONMENT}_${TIMESTAMP}.tar.gz"

    tar -czf "$BACKUP_FILE" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='backups' \
        --exclude='cache' \
        --exclude='venv' \
        -C "$PROJECT_ROOT" .

    log_success "Backup created: $BACKUP_FILE"
else
    log_warning "Skipping backup (--skip-backup specified)"
fi

echo

################################################################################
# Stop Running Services
################################################################################

log_info "Stopping running services..."

# Try to stop systemd service if it exists
if systemctl is-active --quiet hyfuzz 2>/dev/null; then
    sudo systemctl stop hyfuzz
    log_success "Stopped systemd service"
else
    # Try to kill running process
    if pgrep -f "python.*src/__main__.py" > /dev/null; then
        pkill -f "python.*src/__main__.py" || true
        sleep 2
        log_success "Stopped running process"
    else
        log_info "No running services found"
    fi
fi

echo

################################################################################
# Update Code
################################################################################

log_info "Updating code..."

cd "$PROJECT_ROOT"

# Pull latest changes (if on a tracked branch)
if git rev-parse --abbrev-ref --symbolic-full-name @{u} &>/dev/null; then
    git pull
    log_success "Code updated from git"
else
    log_info "Not on a tracked branch, skipping git pull"
fi

echo

################################################################################
# Install Dependencies
################################################################################

log_info "Installing dependencies..."

pip install -r requirements.txt --quiet
log_success "Dependencies installed"

echo

################################################################################
# Run Tests
################################################################################

if [ "$SKIP_TESTS" = false ]; then
    log_info "Running tests..."

    # Run unit tests for security modules
    python -m pytest tests/unit/test_safe_serializer.py -v || {
        log_error "SafeSerializer tests failed!"
        exit 1
    }

    python -m pytest tests/unit/test_safe_imports.py -v || {
        log_error "SafeImports tests failed!"
        exit 1
    }

    python -m pytest tests/unit/test_exception_handler.py -v || {
        log_error "ExceptionHandler tests failed!"
        exit 1
    }

    log_success "All tests passed"
else
    log_warning "Skipping tests (--skip-tests specified)"
fi

echo

################################################################################
# Database Migration (if needed)
################################################################################

log_info "Checking for database migrations..."

# Add your migration commands here if needed
# Example:
# python scripts/migrate_database.py

log_info "No migrations needed"

echo

################################################################################
# Cache Migration
################################################################################

log_info "Migrating cache files..."

# Old pickle caches will be automatically migrated when accessed
# Just log that this will happen

log_info "Cache will be migrated automatically on first access"

echo

################################################################################
# Start Services
################################################################################

log_info "Starting services..."

# Try to start systemd service if configured
if [ -f "/etc/systemd/system/hyfuzz.service" ]; then
    sudo systemctl start hyfuzz
    sleep 2

    if systemctl is-active --quiet hyfuzz; then
        log_success "Started systemd service"
    else
        log_error "Failed to start systemd service"
        exit 1
    fi
else
    # Start with screen or tmux if available
    if command -v screen &> /dev/null; then
        screen -dmS hyfuzz python src/__main__.py
        sleep 2
        log_success "Started with screen (session: hyfuzz)"
        log_info "Attach with: screen -r hyfuzz"
    elif command -v tmux &> /dev/null; then
        tmux new-session -d -s hyfuzz 'python src/__main__.py'
        sleep 2
        log_success "Started with tmux (session: hyfuzz)"
        log_info "Attach with: tmux attach -t hyfuzz"
    else
        log_warning "screen/tmux not found, starting in background..."
        nohup python src/__main__.py > logs/hyfuzz.log 2>&1 &
        sleep 2
        log_success "Started in background"
    fi
fi

echo

################################################################################
# Health Check
################################################################################

log_info "Running health check..."

# Wait a bit for service to start
sleep 3

# Check if process is running
if pgrep -f "python.*src/__main__.py" > /dev/null; then
    log_success "Process is running"

    # Get PID
    PID=$(pgrep -f "python.*src/__main__.py")
    log_info "PID: $PID"
else
    log_error "Process is not running!"
    log_error "Check logs/hyfuzz.log for errors"
    exit 1
fi

# Check logs for errors
log_info "Checking logs for errors..."
if [ -f "logs/hyfuzz.log" ]; then
    ERROR_COUNT=$(grep -i "error\|critical" logs/hyfuzz.log | tail -10 | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        log_warning "Found $ERROR_COUNT recent errors in logs"
        log_info "Last 10 errors:"
        grep -i "error\|critical" logs/hyfuzz.log | tail -10
    else
        log_success "No recent errors in logs"
    fi
else
    log_warning "Log file not found yet"
fi

echo

################################################################################
# Deployment Summary
################################################################################

echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo
echo "Environment:    $ENVIRONMENT"
echo "Git Commit:     $(git rev-parse --short HEAD)"
echo "Backup:         ${BACKUP_FILE:-none}"
echo "Process PID:    ${PID:-unknown}"
echo "=========================================="
echo
echo "Next steps:"
echo "  1. Monitor logs: tail -f logs/hyfuzz.log"
echo "  2. Check process: ps aux | grep python"
echo "  3. Test endpoints (if applicable)"
echo "  4. Monitor for 24 hours"
echo
echo "To rollback:"
echo "  ./scripts/rollback.sh $BACKUP_FILE"
echo

log_success "Deployment complete!"
