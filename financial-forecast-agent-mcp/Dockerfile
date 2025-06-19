# MCP-Enabled Agent Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js version (MCP servers require Node 18+)
RUN node --version && npm --version

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent.py .
COPY test_agent.py .
COPY setup_mcp_servers.sh .

# Make scripts executable
RUN chmod +x setup_mcp_servers.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash agent && \
    chown -R agent:agent /app

# Switch to non-root user
USER agent

# Set up MCP servers during build (optional - can be done at runtime)
# RUN ./setup_mcp_servers.sh --no-test

# Create directories for logs and data
RUN mkdir -p logs mcp_servers

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port for potential HTTP interface
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "agent.py"]