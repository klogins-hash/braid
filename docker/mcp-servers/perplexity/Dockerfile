# Dockerfile for Perplexity MCP Server
FROM node:18-alpine

WORKDIR /app

# Install git for cloning
RUN apk add --no-cache git

# Clone the Perplexity MCP repository
RUN git clone https://github.com/ppl-ai/modelcontextprotocol.git .

# Install dependencies for perplexity-ask
WORKDIR /app/perplexity-ask
RUN npm install
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -S mcp -u 1001

# Set up directories and permissions
RUN chown -R mcp:mcp /app
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "const proc = require('child_process').spawn('node', ['dist/index.js']); proc.stdin.write(JSON.stringify({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'health',version:'1.0.0'}}})+'\n'); proc.stdout.on('data', (data) => { const resp = JSON.parse(data.toString()); if (resp.result) process.exit(0); else process.exit(1); }); setTimeout(() => process.exit(1), 5000);"

# Expose port (MCP uses stdio, but useful for health checks)
EXPOSE 3001

# Default command
CMD ["node", "dist/index.js"]