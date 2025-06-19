#!/bin/bash
set -e

echo "🚀 Starting MCP server: mongodb"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: npx -y mongodb-mcp-server"
exec npx -y mongodb-mcp-server
