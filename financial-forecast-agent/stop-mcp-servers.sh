#!/bin/bash

echo "🛑 Stopping MCP Servers..."
echo "=========================="

# Stop and remove containers
docker-compose -f docker-compose.mcp.yml down

# Optional: Remove volumes (uncomment to clean cache)
# docker-compose -f docker-compose.mcp.yml down -v

echo "✅ MCP Servers stopped successfully!"
echo ""
echo "💡 To restart: ./start-mcp-servers.sh"
echo "🗑️  To clean cache: docker-compose -f docker-compose.mcp.yml down -v"