#!/bin/bash
# HyFuzz Mac MCP Server launcher script
# This script starts the HyFuzz MCP server on macOS

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import src" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Set Python path
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Default values
HOST="${SERVER_HOST:-127.0.0.1}"
PORT="${SERVER_PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
TRANSPORT="${TRANSPORT:-http}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --transport)
            TRANSPORT="$2"
            shift 2
            ;;
        --smoke-test)
            SMOKE_TEST="--smoke-test"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --host HOST         Server host (default: 127.0.0.1)"
            echo "  --port PORT         Server port (default: 8000)"
            echo "  --log-level LEVEL   Logging level (default: INFO)"
            echo "  --transport TYPE    Transport type: stdio, http, websocket (default: http)"
            echo "  --smoke-test        Run smoke test and exit"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start the server
echo "Starting HyFuzz MCP Server on macOS..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Transport: $TRANSPORT"
echo "Log Level: $LOG_LEVEL"
echo ""

python -m src \
    --host "$HOST" \
    --port "$PORT" \
    --transport "$TRANSPORT" \
    --log-level "$LOG_LEVEL" \
    $SMOKE_TEST

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
