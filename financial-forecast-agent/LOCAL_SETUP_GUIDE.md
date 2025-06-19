# Local Setup Guide for MCP-Based Financial Forecast Agent

This guide will help you set up and test the complete MCP-based financial forecasting system on your local device.

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Python 3.11+** for running MCP servers
3. **Node.js** (for MCP if needed)
4. **Git** for cloning repositories

## Step 1: Start MCP Servers

The agent requires three MCP servers to be running on your host machine.

### Option A: Start Individual MCP Servers

```bash
# Terminal 1 - Xero MCP Server
cd /Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid/financial-forecast-agent
python -m mcp.xero.server --port 3001

# Terminal 2 - Perplexity MCP Server  
python -m mcp.perplexity.server --port 3002

# Terminal 3 - Notion MCP Server
python -m mcp.notion.server --port 3003
```

### Option B: Start All MCP Servers with Script

Create a startup script to launch all MCP servers:

```bash
#!/bin/bash
# start_mcp_servers.sh

echo "🚀 Starting all MCP servers..."

# Start Xero MCP
echo "📊 Starting Xero MCP server on port 3001..."
python -m mcp.xero.server --port 3001 &
XERO_PID=$!

# Start Perplexity MCP  
echo "🔍 Starting Perplexity MCP server on port 3002..."
python -m mcp.perplexity.server --port 3002 &
PERPLEXITY_PID=$!

# Start Notion MCP
echo "📝 Starting Notion MCP server on port 3003..."
python -m mcp.notion.server --port 3003 &
NOTION_PID=$!

echo "✅ All MCP servers started!"
echo "   Xero MCP: http://localhost:3001 (PID: $XERO_PID)"
echo "   Perplexity MCP: http://localhost:3002 (PID: $PERPLEXITY_PID)"  
echo "   Notion MCP: http://localhost:3003 (PID: $NOTION_PID)"

# Save PIDs for cleanup
echo "$XERO_PID $PERPLEXITY_PID $NOTION_PID" > mcp_pids.txt

echo "Press Ctrl+C to stop all servers..."
wait
```

Make it executable and run:
```bash
chmod +x start_mcp_servers.sh
./start_mcp_servers.sh
```

## Step 2: Verify Environment Configuration

Ensure your `.env` file has all required variables:

```bash
# Check current .env
cat .env | grep -E "(OPENAI|XERO|PERPLEXITY|NOTION|LANGCHAIN)"
```

Required variables:
- `OPENAI_API_KEY` - For LLM processing
- `XERO_ACCESS_TOKEN` - For financial data
- `PERPLEXITY_API_KEY` - For market research
- `NOTION_API_KEY` - For report generation (optional)
- `LANGCHAIN_API_KEY` - For tracing (optional)

## Step 3: Test MCP Connectivity

Before running the full agent, test that MCP servers are accessible:

```bash
# Test Xero MCP
curl -X POST http://localhost:3001/health || echo "Xero MCP not running"

# Test Perplexity MCP  
curl -X POST http://localhost:3002/health || echo "Perplexity MCP not running"

# Test Notion MCP
curl -X POST http://localhost:3003/health || echo "Notion MCP not running"
```

## Step 4: Run the MCP-Based Agent

### Option A: Run with Docker (Recommended)

```bash
# Build and run the containerized agent
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### Option B: Run Directly (for Development)

```bash
# Install dependencies
pip install -e .

# Run the MCP-based agent directly
python run_production_mcp.py
```

## Step 5: Test the Complete System

### Check Health Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Readiness check (verifies MCP connectivity)
curl http://localhost:8000/ready

# Metrics
curl http://localhost:8000/metrics
```

### Test Forecast Generation

The agent will automatically run a forecast for `user_123`. To test with different users:

```bash
# Set different test user
export TEST_USER_ID=user_456
docker-compose up --build
```

### Monitor the Workflow

Watch the logs to see the MCP-based workflow:

```bash
docker-compose logs -f financial-forecast-mcp
```

You should see:
- ✅ MCP servers being accessed
- 📊 Xero data retrieval via MCP
- 🔍 Market research via Perplexity MCP
- 📝 Notion report creation via MCP
- 📈 5-year forecast generation

## Step 6: Troubleshooting

### MCP Servers Not Starting

```bash
# Check if ports are in use
lsof -i :3001
lsof -i :3002  
lsof -i :3003

# Kill existing processes
kill $(cat mcp_pids.txt)
```

### Docker Networking Issues

```bash
# Verify host networking
docker inspect financial-forecast-mcp | grep NetworkMode

# Check if container can reach host
docker exec -it financial-forecast-mcp curl http://host.docker.internal:3001/health
```

### Environment Variable Issues

```bash
# Check env vars in container
docker exec -it financial-forecast-mcp printenv | grep -E "(OPENAI|XERO|PERPLEXITY)"
```

### API Token Issues

```bash
# Test Xero token directly
curl -H "Authorization: Bearer $XERO_ACCESS_TOKEN" https://api.xero.com/connections

# Test Perplexity key
curl -H "Authorization: Bearer $PERPLEXITY_API_KEY" https://api.perplexity.ai/chat/completions
```

## Step 7: Complete Test Workflow

Here's the complete test sequence:

```bash
# 1. Start MCP servers
./start_mcp_servers.sh &

# 2. Wait a moment for servers to start
sleep 5

# 3. Test MCP connectivity
curl http://localhost:3001/health
curl http://localhost:3002/health  
curl http://localhost:3003/health

# 4. Run the agent
docker-compose up --build

# 5. In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics

# 6. Check logs for successful forecast
docker-compose logs financial-forecast-mcp | grep "✅.*forecast completed"
```

## Expected Output

When everything works correctly, you should see:

```
✅ MCP production agent initialized successfully
🔗 MCP Server Connection Status:
   Xero MCP: Will be accessed via MCP tools
   Perplexity MCP: Will be accessed via MCP tools  
   Notion MCP: Will be accessed via MCP tools
📊 MCP-BASED PRODUCTION FORECAST RESULTS
   "mcp_tools_used": ["Xero MCP", "Perplexity MCP", "Notion MCP"]
   "processing_time_seconds": 0.116477
```

## Cleanup

```bash
# Stop the agent
docker-compose down

# Stop MCP servers
kill $(cat mcp_pids.txt)
rm mcp_pids.txt

# Clean up Docker
docker system prune -f
```

## Next Steps

Once the local setup is working:
1. Deploy to staging environment
2. Set up production monitoring
3. Configure CI/CD pipelines
4. Add automated testing

The system is now fully MCP-based as requested, with production monitoring and Docker deployment capabilities.