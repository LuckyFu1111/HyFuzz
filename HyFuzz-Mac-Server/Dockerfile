# Multi-stage Dockerfile for HyFuzz Server
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     g++     make     && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3     CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Expose port
EXPOSE 8080

# Run server
CMD ["python", "-m", "src"]
