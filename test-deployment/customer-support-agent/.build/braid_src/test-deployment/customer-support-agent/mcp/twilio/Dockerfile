# Auto-generated Dockerfile for MCP Server
# Template: nodejs_mcp
FROM node:18-slim

# Create non-root user for security
RUN adduser --disabled-password --gecos '' mcp

# Install system dependencies
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
RUN npm config set fund false
RUN npm config set audit false

# Set working directory
WORKDIR /app
RUN chown mcp:mcp /app

# Copy MCP server files
COPY --chown=mcp:mcp . /app/

# Install MCP dependencies
RUN npm ci --only=production
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=60s \
            --retries=3 \
    CMD node -e process.exit(0)

# Switch to non-root user
USER mcp

# Expose ports
EXPOSE 3000

CMD ["node", "/app/server.js"]

# Production optimizations
ENV NODE_ENV=production
RUN npm prune --production
