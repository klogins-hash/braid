#!/bin/bash
set -e

echo "🚀 Starting MCP server: alphavantage"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: python -m alphavantage_mcp_server"
exec python -m alphavantage_mcp_server
