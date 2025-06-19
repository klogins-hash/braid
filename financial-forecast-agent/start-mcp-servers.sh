#!/bin/bash

echo "🚀 Starting MCP Servers with Docker Compose..."
echo "================================================"

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ No .env file found. Please create ../.env with:"
    echo "   XERO_BEARER_TOKEN=your_token_here"
    echo "   PERPLEXITY_API_KEY=your_key_here"
    echo "   NOTION_API_KEY=your_key_here"
    exit 1
fi

# Load environment variables
set -a
source ../.env
set +a

# Create cache directories
mkdir -p xero-cache perplexity-cache notion-cache

# Start MCP servers
echo "🐳 Starting MCP servers..."
docker-compose -f docker-compose.mcp.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

echo "📊 Xero MCP Server:"
curl -s http://localhost:3002/health | jq . 2>/dev/null || echo "  Status: Starting up..."

echo "🔍 Perplexity MCP Server:"
curl -s http://localhost:3003/health | jq . 2>/dev/null || echo "  Status: Starting up..."

echo "📝 Notion MCP Server:"
curl -s http://localhost:3001/health | jq . 2>/dev/null || echo "  Status: Starting up..."

echo "🌐 MCP Gateway:"
curl -s http://localhost:3000/health | jq . 2>/dev/null || echo "  Status: Starting up..."

echo ""
echo "✅ MCP Servers Started!"
echo "================================================"
echo "🔗 Access points:"
echo "   Xero MCP:       http://localhost:3002"
echo "   Perplexity MCP: http://localhost:3003" 
echo "   Notion MCP:     http://localhost:3001"
echo "   Gateway:        http://localhost:3000"
echo ""
echo "📊 View logs: docker-compose -f docker-compose.mcp.yml logs -f"
echo "🛑 Stop servers: ./stop-mcp-servers.sh"