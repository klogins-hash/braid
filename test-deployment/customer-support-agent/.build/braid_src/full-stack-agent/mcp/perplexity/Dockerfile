# Auto-generated Dockerfile for MCP Server
# Template: custom_mcp
FROM alpine:3.18

# Create non-root user for security
RUN adduser --disabled-password --gecos '' mcp

# Install system dependencies
RUN apk add --no-cache curl

# Set working directory
WORKDIR /app
RUN chown mcp:mcp /app

# Copy MCP server files
COPY --chown=mcp:mcp . /app/

# Install MCP dependencies

# Health check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=60s \
            --retries=3 \
    CMD curl -f http://localhost:8080/health

# Switch to non-root user
USER mcp

# Expose ports
EXPOSE 8080

CMD ["sh", "/app/start.sh"]

# Production optimizations
