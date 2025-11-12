#!/bin/bash
################################################################################
# HyFuzz Rollback Script
################################################################################
# Rolls back to a previous deployment state
#
# Usage:
#   ./scripts/rollback.sh <backup_file>
#
# Example:
#   ./scripts/rollback.sh backups/backup_staging_20251111_120000.tar.gz
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

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Backup file required${NC}"
    echo "Usage: $0 <backup_file>"
    echo
    echo "Available backups:"
    ls -lh "$PROJECT_ROOT/backups/" 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

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
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Rollback cancelled by user"
        exit 1
    fi
}

################################################################################
# Validation
################################################################################

log_info "Starting rollback process..."
echo

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Get backup info
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
BACKUP_DATE=$(stat -c %y "$BACKUP_FILE" 2>/dev/null | cut -d' ' -f1 || stat -f %Sm -t %Y-%m-%d "$BACKUP_FILE" 2>/dev/null)

echo "=========================================="
echo "Rollback Configuration:"
echo "=========================================="
echo "Backup File:  $BACKUP_FILE"
echo "Backup Size:  $BACKUP_SIZE"
echo "Backup Date:  $BACKUP_DATE"
echo "Target Dir:   $PROJECT_ROOT"
echo "=========================================="
echo

log_warning "This will REPLACE all current files with the backup!"
confirm "Are you sure you want to proceed?"

################################################################################
# Create Safety Backup
################################################################################

log_info "Creating safety backup of current state..."

SAFETY_BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$SAFETY_BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAFETY_BACKUP="$SAFETY_BACKUP_DIR/pre_rollback_${TIMESTAMP}.tar.gz"

tar -czf "$SAFETY_BACKUP" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='backups' \
    --exclude='cache' \
    --exclude='venv' \
    -C "$PROJECT_ROOT" .

log_success "Safety backup created: $SAFETY_BACKUP"
echo

################################################################################
# Stop Services
################################################################################

log_info "Stopping services..."

# Try to stop systemd service
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
# Restore Backup
################################################################################

log_info "Restoring from backup..."

# Create temporary directory
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Extract backup to temporary directory
tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"
log_info "Backup extracted to temporary directory"

# Preserve certain files that shouldn't be rolled back
PRESERVE_FILES=(
    ".env"
    "logs"
    "cache"
)

log_info "Preserving critical files..."
for file in "${PRESERVE_FILES[@]}"; do
    if [ -e "$PROJECT_ROOT/$file" ]; then
        cp -r "$PROJECT_ROOT/$file" "$TMP_DIR/$file" || true
        log_info "Preserved: $file"
    fi
done

# Remove current files (except preserved ones and .git)
log_info "Removing current files..."
cd "$PROJECT_ROOT"
find . -maxdepth 1 ! -name '.' ! -name '..' ! -name '.git' ! -name 'backups' ! -name 'logs' ! -name 'cache' -exec rm -rf {} + 2>/dev/null || true

# Copy backup files to project root
log_info "Restoring files..."
cp -r "$TMP_DIR"/* "$PROJECT_ROOT/" 2>/dev/null || true
cp -r "$TMP_DIR"/.[^.]* "$PROJECT_ROOT/" 2>/dev/null || true

log_success "Files restored from backup"
echo

################################################################################
# Reinstall Dependencies
################################################################################

log_info "Reinstalling dependencies..."

cd "$PROJECT_ROOT"
pip install -r requirements.txt --quiet

log_success "Dependencies reinstalled"
echo

################################################################################
# Restart Services
################################################################################

log_info "Restarting services..."

# Try to start systemd service if configured
if [ -f "/etc/systemd/system/hyfuzz.service" ]; then
    sudo systemctl start hyfuzz
    sleep 2

    if systemctl is-active --quiet hyfuzz; then
        log_success "Started systemd service"
    else
        log_error "Failed to start systemd service"
        log_error "Check logs for errors"
        exit 1
    fi
else
    # Start with screen or tmux
    if command -v screen &> /dev/null; then
        screen -dmS hyfuzz python src/__main__.py
        sleep 2
        log_success "Started with screen (session: hyfuzz)"
    elif command -v tmux &> /dev/null; then
        tmux new-session -d -s hyfuzz 'python src/__main__.py'
        sleep 2
        log_success "Started with tmux (session: hyfuzz)"
    else
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
sleep 3

if pgrep -f "python.*src/__main__.py" > /dev/null; then
    log_success "Process is running"
    PID=$(pgrep -f "python.*src/__main__.py")
    log_info "PID: $PID"
else
    log_error "Process is not running!"
    log_error "Rollback may have failed"
    exit 1
fi

echo

################################################################################
# Summary
################################################################################

echo "=========================================="
echo "Rollback Summary"
echo "=========================================="
echo -e "${GREEN}✅ Rollback completed successfully!${NC}"
echo
echo "Restored from:  $BACKUP_FILE"
echo "Safety backup:  $SAFETY_BACKUP"
echo "Process PID:    $PID"
echo "=========================================="
echo
echo "Next steps:"
echo "  1. Monitor logs: tail -f logs/hyfuzz.log"
echo "  2. Run health check: ./scripts/health_check.sh"
echo "  3. Verify functionality"
echo
echo "If issues persist:"
echo "  - Check logs/hyfuzz.log"
echo "  - Verify .env configuration"
echo "  - Consider re-deploying from git"
echo

log_success "Rollback complete!"
