#!/bin/bash
set -e

echo "🚀 Starting MCP server: notion"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: npx -y @makenotion/notion-mcp-server"
exec npx -y @makenotion/notion-mcp-server
