#!/bin/bash
set -e

echo "🚀 Starting MCP server: agentql"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: npx -y agentql-mcp"
exec npx -y agentql-mcp
