#!/bin/bash
set -e

echo "🚀 Starting MCP server: perplexity"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: npx -y mcp-perplexity"
exec npx -y mcp-perplexity
