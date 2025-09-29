# Braid AI Agent System - Railway Deployment
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js version (MCP servers require Node 18+)
RUN node --version && npm --version

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.lock ./
COPY setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash agent && \
    chown -R agent:agent /app

# Switch to non-root user
USER agent

# Create directories for logs and data
RUN mkdir -p logs mcp_servers data

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port
EXPOSE ${PORT:-8000}

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command - will be overridden by Railway if needed
CMD ["python", "-m", "braid.server"]
