# Quick Start Guide - MCP Financial Forecast Agent

## 🚀 1-Minute Setup

```bash
# 1. Run complete test (recommended)
./test_local_setup.sh

# 2. OR manual setup:

# Start MCP servers
./start_mcp_servers.sh &

# Run the agent
docker-compose up --build

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## 📋 What You Should See

### ✅ Successful Output:
```
✅ MCP production agent initialized successfully
🔗 MCP Server Connection Status:
   Xero MCP: Will be accessed via MCP tools
   Perplexity MCP: Will be accessed via MCP tools  
   Notion MCP: Will be accessed via MCP tools
📊 MCP-BASED PRODUCTION FORECAST RESULTS
"mcp_tools_used": ["Xero MCP", "Perplexity MCP", "Notion MCP"]
```

### 🏥 Health Check Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-19T15:01:50.721857",
  "environment": "production",
  "version": "1.0.0"
}
```

## 🛑 Stop Everything

```bash
# Stop MCP servers
./stop_mcp_servers.sh

# Stop Docker container
docker-compose down
```

## 🔧 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `SECRET_KEY` error | Set `SECRET_KEY` in docker-compose.yml |
| MCP servers not starting | Check logs in `logs/mcp/` directory |
| Docker build fails | Run `docker system prune -f` and retry |
| Port conflicts | Check `lsof -i :8000` and kill processes |
| API key errors | Verify `.env` file has all required keys |

## 📂 Key Files

- `run_production_mcp.py` - Main MCP-based agent
- `docker-compose.yml` - Docker configuration  
- `start_mcp_servers.sh` - Start all MCP servers
- `test_local_setup.sh` - Complete system test
- `LOCAL_SETUP_GUIDE.md` - Detailed setup guide

## 🎯 Next Steps

1. ✅ Basic setup working
2. 🔌 Configure real MCP servers
3. 🚀 Deploy to production
4. 📊 Add monitoring/alerting