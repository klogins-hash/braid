
# Multi-stage build for production-ready agent
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agent
WORKDIR /app
RUN chown agent:agent /app

# Stage 1: Build dependencies
FROM base as builder
WORKDIR /app

# Copy and install Braid toolkit
COPY ./braid_src /app/braid_src
RUN pip install --no-cache-dir /app/braid_src

# Install agent dependencies using pip (not poetry for production)
COPY ./agent_code/pyproject.toml ./agent_code/requirements.txt* ./agent_code/README.md* ./
COPY ./agent_code/src/ ./src/
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install --no-cache-dir -e .; \
    fi

# Stage 2: Production image
FROM base as production
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy agent source code
COPY ./agent_code/src/ ./src/

# Set up environment
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import sales_intelligence_agent_v3.configuration; print('Health check passed')" || exit 1

# Switch to non-root user
USER agent

# Expose port (adjust as needed)
EXPOSE 8000

# Command to run the agent
CMD ["python", "src/sales_intelligence_agent_v3/graph.py"]
