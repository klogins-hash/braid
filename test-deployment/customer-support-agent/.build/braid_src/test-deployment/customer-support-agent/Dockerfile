# Multi-stage optimized Dockerfile for Braid Agent
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1001 agent

# Stage 1: Dependencies
FROM base as dependencies
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM base as production
WORKDIR /app

# Copy installed packages from dependencies stage
COPY --from=dependencies /root/.local /home/agent/.local
ENV PATH=/home/agent/.local/bin:$PATH

# Copy application code
COPY --chown=agent:agent . .

# Set up directories
RUN mkdir -p data logs cache config monitoring \
    && chown -R agent:agent /app

# Switch to non-root user
USER agent

# Environment configuration
ENV PYTHONPATH=/app
ENV LOG_LEVEL=info
ENV MCP_TIMEOUT=60

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "agent.py"]
