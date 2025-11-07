# Multi-stage Dockerfile for HyFuzz Ubuntu Client
# Stage 1: Builder
FROM ubuntu:22.04 as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     python3     python3-pip     python3-dev     gcc     g++     make     && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     python3     python3-pip     strace     ltrace     gdb     netcat     && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash hyfuzz

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/hyfuzz/.local

# Copy application code
COPY --chown=hyfuzz:hyfuzz . .

# Set environment variables
ENV PATH=/home/hyfuzz/.local/bin:$PATH     PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER hyfuzz

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3     CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Run client
CMD ["python3", "-m", "src"]
