#!/bin/bash
################################################################################
# HyFuzz Health Check Script
################################################################################
# Performs comprehensive health checks on the HyFuzz server
#
# Usage:
#   ./scripts/health_check.sh [options]
#
# Options:
#   --verbose    - Show detailed output
#   --json       - Output results in JSON format
#   --alerts     - Exit with error code if checks fail (for monitoring)
#
# Example:
#   ./scripts/health_check.sh
#   ./scripts/health_check.sh --verbose
#   ./scripts/health_check.sh --json --alerts
#
################################################################################

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

# Default options
VERBOSE=false
JSON_OUTPUT=false
ALERT_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --alerts)
            ALERT_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Health check results
declare -A CHECKS
OVERALL_STATUS="healthy"

################################################################################
# Helper Functions
################################################################################

log_info() {
    if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_pass() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}[✓]${NC} $1"
    fi
}

log_warn() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}[⚠]${NC} $1"
    fi
}

log_fail() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}[✗]${NC} $1"
    fi
    OVERALL_STATUS="unhealthy"
}

record_check() {
    local name=$1
    local status=$2
    local message=$3
    CHECKS["$name"]="$status:$message"
}

################################################################################
# Health Checks
################################################################################

check_process() {
    log_info "Checking if HyFuzz process is running..."

    if pgrep -f "python.*src/__main__.py" > /dev/null; then
        PID=$(pgrep -f "python.*src/__main__.py")
        log_pass "Process is running (PID: $PID)"
        record_check "process" "pass" "Running with PID $PID"
        return 0
    else
        log_fail "Process is not running"
        record_check "process" "fail" "Process not found"
        return 1
    fi
}

check_memory() {
    log_info "Checking memory usage..."

    if pgrep -f "python.*src/__main__.py" > /dev/null; then
        PID=$(pgrep -f "python.*src/__main__.py")

        # Get memory usage in MB
        MEM_MB=$(ps -p $PID -o rss= | awk '{print $1/1024}')

        # Check if memory usage is reasonable (< 1GB)
        if (( $(echo "$MEM_MB < 1024" | bc -l) )); then
            log_pass "Memory usage: ${MEM_MB}MB (healthy)"
            record_check "memory" "pass" "${MEM_MB}MB"
            return 0
        else
            log_warn "Memory usage: ${MEM_MB}MB (high)"
            record_check "memory" "warn" "${MEM_MB}MB (high)"
            return 0
        fi
    else
        log_warn "Cannot check memory (process not running)"
        record_check "memory" "skip" "Process not running"
        return 1
    fi
}

check_cpu() {
    log_info "Checking CPU usage..."

    if pgrep -f "python.*src/__main__.py" > /dev/null; then
        PID=$(pgrep -f "python.*src/__main__.py")

        # Get CPU usage percentage
        CPU_PERCENT=$(ps -p $PID -o %cpu= | tr -d ' ')

        # Check if CPU usage is reasonable (< 80%)
        if (( $(echo "$CPU_PERCENT < 80" | bc -l) )); then
            log_pass "CPU usage: ${CPU_PERCENT}% (healthy)"
            record_check "cpu" "pass" "${CPU_PERCENT}%"
            return 0
        else
            log_warn "CPU usage: ${CPU_PERCENT}% (high)"
            record_check "cpu" "warn" "${CPU_PERCENT}% (high)"
            return 0
        fi
    else
        log_warn "Cannot check CPU (process not running)"
        record_check "cpu" "skip" "Process not running"
        return 1
    fi
}

check_logs() {
    log_info "Checking logs for errors..."

    LOG_FILE="$PROJECT_ROOT/logs/hyfuzz.log"

    if [ ! -f "$LOG_FILE" ]; then
        log_warn "Log file not found: $LOG_FILE"
        record_check "logs" "warn" "Log file not found"
        return 0
    fi

    # Check for recent errors (last 100 lines)
    ERROR_COUNT=$(tail -100 "$LOG_FILE" | grep -ci "error\|critical" || true)

    if [ "$ERROR_COUNT" -eq 0 ]; then
        log_pass "No recent errors in logs"
        record_check "logs" "pass" "No errors"
        return 0
    elif [ "$ERROR_COUNT" -lt 5 ]; then
        log_warn "Found $ERROR_COUNT recent errors"
        record_check "logs" "warn" "$ERROR_COUNT errors"
        return 0
    else
        log_fail "Found $ERROR_COUNT recent errors"
        record_check "logs" "fail" "$ERROR_COUNT errors"
        return 1
    fi
}

check_disk_space() {
    log_info "Checking disk space..."

    # Check available disk space on root partition
    AVAILABLE=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
    AVAILABLE_GB=$(echo "scale=2; $AVAILABLE / 1024 / 1024" | bc)

    # Check if available space is > 1GB
    if (( $(echo "$AVAILABLE_GB > 1" | bc -l) )); then
        log_pass "Disk space: ${AVAILABLE_GB}GB available"
        record_check "disk" "pass" "${AVAILABLE_GB}GB available"
        return 0
    else
        log_warn "Disk space: ${AVAILABLE_GB}GB available (low)"
        record_check "disk" "warn" "${AVAILABLE_GB}GB available (low)"
        return 0
    fi
}

check_cache_size() {
    log_info "Checking cache size..."

    CACHE_DIR="$PROJECT_ROOT/cache"

    if [ ! -d "$CACHE_DIR" ]; then
        log_info "Cache directory not found (may not exist yet)"
        record_check "cache" "skip" "Directory not found"
        return 0
    fi

    # Get cache size in MB
    CACHE_MB=$(du -sm "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")

    # Check if cache size is reasonable (< 5GB)
    if [ "$CACHE_MB" -lt 5120 ]; then
        log_pass "Cache size: ${CACHE_MB}MB (healthy)"
        record_check "cache" "pass" "${CACHE_MB}MB"
        return 0
    else
        log_warn "Cache size: ${CACHE_MB}MB (large, consider cleanup)"
        record_check "cache" "warn" "${CACHE_MB}MB (large)"
        return 0
    fi
}

check_env_file() {
    log_info "Checking environment configuration..."

    ENV_FILE="$PROJECT_ROOT/.env"

    if [ ! -f "$ENV_FILE" ]; then
        log_fail ".env file not found"
        record_check "env" "fail" "File not found"
        return 1
    fi

    # Check if JWT_SECRET_KEY is set
    if grep -q "JWT_SECRET_KEY=your-secret-key-here" "$ENV_FILE" || ! grep -q "JWT_SECRET_KEY=" "$ENV_FILE"; then
        log_fail "JWT_SECRET_KEY not properly configured"
        record_check "env" "fail" "JWT_SECRET_KEY not configured"
        return 1
    fi

    log_pass "Environment configuration valid"
    record_check "env" "pass" "Configuration valid"
    return 0
}

check_python_version() {
    log_info "Checking Python version..."

    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 11 ]; then
        log_pass "Python version: $PYTHON_VERSION (compatible)"
        record_check "python" "pass" "$PYTHON_VERSION"
        return 0
    else
        log_warn "Python version: $PYTHON_VERSION (requires 3.11+)"
        record_check "python" "warn" "$PYTHON_VERSION (old)"
        return 0
    fi
}

################################################################################
# Run All Checks
################################################################################

if [ "$JSON_OUTPUT" = false ]; then
    echo "=========================================="
    echo "HyFuzz Health Check"
    echo "=========================================="
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo
fi

# Run all checks
check_process
check_env_file
check_python_version
check_memory
check_cpu
check_disk_space
check_cache_size
check_logs

################################################################################
# Output Results
################################################################################

if [ "$JSON_OUTPUT" = true ]; then
    # JSON output
    echo "{"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"status\": \"$OVERALL_STATUS\","
    echo "  \"checks\": {"

    first=true
    for check_name in "${!CHECKS[@]}"; do
        if [ "$first" = false ]; then
            echo ","
        fi
        first=false

        IFS=':' read -r status message <<< "${CHECKS[$check_name]}"
        echo -n "    \"$check_name\": {\"status\": \"$status\", \"message\": \"$message\"}"
    done

    echo
    echo "  }"
    echo "}"
else
    # Human-readable summary
    echo
    echo "=========================================="
    echo "Health Check Summary"
    echo "=========================================="

    PASS_COUNT=0
    WARN_COUNT=0
    FAIL_COUNT=0

    for check_name in "${!CHECKS[@]}"; do
        IFS=':' read -r status message <<< "${CHECKS[$check_name]}"
        case $status in
            pass) ((PASS_COUNT++)) ;;
            warn) ((WARN_COUNT++)) ;;
            fail) ((FAIL_COUNT++)) ;;
        esac
    done

    echo "Passed:   $PASS_COUNT"
    echo "Warnings: $WARN_COUNT"
    echo "Failed:   $FAIL_COUNT"
    echo "=========================================="

    if [ "$OVERALL_STATUS" = "healthy" ]; then
        echo -e "${GREEN}Overall Status: HEALTHY ✓${NC}"
    else
        echo -e "${RED}Overall Status: UNHEALTHY ✗${NC}"
    fi

    echo
fi

################################################################################
# Exit Code
################################################################################

if [ "$ALERT_MODE" = true ]; then
    if [ "$OVERALL_STATUS" = "healthy" ]; then
        exit 0
    else
        exit 1
    fi
else
    exit 0
fi
