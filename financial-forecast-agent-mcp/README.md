# Financial Forecasting Agent with MCP Integration

A production-ready financial forecasting agent that uses Model Context Protocol (MCP) servers for real-time data integration and automated report generation.

## 🎯 Overview

This agent implements a comprehensive 6-step financial forecasting workflow:

1. **📊 Xero Data Retrieval** - Get historical financial data via Xero MCP
2. **🏢 Client Information** - Retrieve business context and details  
3. **🔍 Market Research** - Conduct industry analysis via Perplexity MCP
4. **📋 Forecast Assumptions** - Generate data-driven assumptions
5. **📈 Financial Projections** - Calculate 5-year forecasts
6. **📄 Notion Report** - Create comprehensive reports via Notion MCP

## 🚀 Features

- **MCP Integration**: Direct connection to Perplexity, Xero, and Notion servers
- **Automated Workflow**: Complete end-to-end forecasting process
- **Real-time Data**: Live financial data from Xero accounting system
- **Market Intelligence**: Current market trends via Perplexity research
- **Professional Reports**: Formatted reports automatically created in Notion
- **Error Handling**: Graceful fallbacks when MCP servers are unavailable
- **Production Ready**: Logging, monitoring, and graceful shutdown

## 🔧 Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for MCP servers)
- **Git** (for MCP server repositories)

### Required API Keys

- **OpenAI API Key** - For the core LLM
- **Perplexity API Key** - For market research ([Get key](https://www.perplexity.ai/))
- **Xero Credentials** - Bearer token, Client ID, Client Secret ([Setup guide](https://developer.xero.com/))
- **Notion API Key** - Integration token ([Setup guide](https://www.notion.so/my-integrations))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Copy the agent (if using template)
cp -r templates/mcp-agent financial-forecast-agent-mcp
cd financial-forecast-agent-mcp

# Or if already in the directory
cd financial-forecast-agent-mcp

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual API keys
# OPENAI_API_KEY=your_openai_key
# PERPLEXITY_API_KEY=your_perplexity_key  
# XERO_ACCESS_TOKEN=your_xero_token
# NOTION_API_KEY=your_notion_key
```

### 3. Setup MCP Servers

```bash
# Run automated MCP setup
./setup_mcp_servers.sh

# This will:
# - Clone MCP server repositories
# - Install Node.js dependencies
# - Validate environment variables
# - Test server connections
```

### 4. Run the Agent

```bash
# Start the financial forecasting agent
python agent.py

# Interactive commands:
# - 'forecast' - Run complete 6-step workflow
# - 'status' - Check MCP server status
# - 'help' - Show available commands
# - 'quit' - Exit the agent
```

## 🔄 Workflow Details

### Step 1: Xero Data Retrieval
- Connects to Xero MCP server
- Retrieves profit & loss, balance sheet data
- Provides historical financial baseline

### Step 2: Client Information
- Gathers business context (industry, location, strategy)
- Retrieves company demographics
- Sets forecasting parameters

### Step 3: Market Research  
- Uses Perplexity MCP for real-time market analysis
- Researches industry trends and growth outlook
- Identifies market opportunities and risks

### Step 4: Forecast Assumptions
- Generates data-driven assumptions
- Incorporates market research insights
- Creates structured assumption framework

### Step 5: Financial Projections
- Calculates 5-year financial forecasts
- Applies assumptions to historical data
- Generates multiple scenarios (base, optimistic, pessimistic)

### Step 6: Notion Report
- Creates comprehensive forecast report
- Includes executive summary, data tables, charts
- Automatically publishes to Notion workspace

## 🧪 Testing

### Test MCP Connections

```bash
# Test all MCP servers
python test_agent.py --test-mcp

# Test complete workflow
python test_agent.py --test-workflow

# Run full test suite
python test_agent.py --all
```

### Manual Testing

```bash
# Check MCP server status
python -c "
from agent import mcp_manager
results = mcp_manager.start_all()
print('MCP Status:', results)
"
```

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   ```bash
   # Check Node.js version (must be 18+)
   node --version
   
   # Verify environment variables
   echo $PERPLEXITY_API_KEY
   echo $XERO_ACCESS_TOKEN
   echo $NOTION_API_KEY
   
   # Re-run MCP setup
   ./setup_mcp_servers.sh
   ```

2. **Agent Workflow Errors**
   ```bash
   # Enable debug logging
   export DEBUG=true
   python agent.py
   
   # Check LangSmith traces (if configured)
   # Visit https://smith.langchain.com/
   ```

3. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x setup_mcp_servers.sh
   chmod +x test_agent.py
   ```

### Debug Mode

```bash
# Enable verbose logging
DEBUG=mcp:* python agent.py

# Test individual MCP servers
python test_agent.py --server perplexity
python test_agent.py --server xero
python test_agent.py --server notion
```

## 📊 MCP Server Status

The agent provides real-time status of all MCP servers:

```bash
# In interactive mode, type 'status'
👤 You: status

📊 MCP Server Status:
  Perplexity: 🟢 Running (3 tools)
  Xero: 🟢 Running (52 tools) 
  Notion: 🟢 Running (19 tools)
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM |
| `PERPLEXITY_API_KEY` | Yes | Perplexity API for market research |
| `XERO_ACCESS_TOKEN` | Yes | Xero bearer token for financial data |
| `XERO_CLIENT_ID` | Optional | Xero client ID |
| `XERO_CLIENT_SECRET` | Optional | Xero client secret |
| `NOTION_API_KEY` | Yes | Notion integration token |
| `NOTION_DEFAULT_PAGE_ID` | Optional | Default parent page for reports |
| `LANGCHAIN_API_KEY` | Optional | LangSmith tracing |

### Forecasting Settings

```bash
# Optional configuration
DEFAULT_FORECAST_YEARS=5
DEFAULT_USER_ID=user_123
FORECAST_CONFIDENCE_LEVEL=80
```

## 🚢 Production Deployment

### Docker Deployment

```bash
# Build container
docker build -t financial-forecast-agent .

# Run with environment file
docker run --env-file .env financial-forecast-agent
```

### With External MCP Servers

```bash
# Use production MCP server URLs
export MCP_PERPLEXITY_URL=http://perplexity-mcp:3001
export MCP_XERO_URL=http://xero-mcp:3002
export MCP_NOTION_URL=http://notion-mcp:3003

python agent.py
```

## 📈 Example Output

```
💰 Financial Forecasting Agent with MCP Integration
============================================================
📊 6-Step Workflow: Xero → Client Info → Market Research → Assumptions → Forecast → Notion Report
🔌 MCP Servers: Perplexity (research), Xero (financial data), Notion (reporting)

👤 You: forecast

🚀 Starting 6-step financial forecasting workflow...
📊 Step 1: Retrieving Xero financial data...
🏢 Step 2: Getting client information...
🔍 Step 3: Conducting market research...
📋 Step 4: Generating forecast assumptions...
📈 Step 5: Calculating financial forecast...
📄 Step 6: Creating Notion report...

✅ Financial forecast completed for user_123

🤖 Result:
Comprehensive 5-year financial forecast completed with:
- Historical analysis from Xero data
- Market research insights
- Data-driven assumptions  
- 5-year projections showing 15% annual growth
- Professional report created in Notion
```

## 🔗 Related Documentation

- **[MCP Setup Guide](../docs/guides/mcp-integration/MCP_SETUP_GUIDE.md)** - Complete MCP integration guide
- **[MCP Deployment Guide](../docs/guides/mcp-integration/MCP_DEPLOYMENT_GUIDE.md)** - Production deployment
- **[MCP Testing Framework](../tests/README.md)** - Testing and validation

## 🆘 Support

For issues or questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review MCP server logs in `logs/` directory
3. Enable debug mode for detailed logging
4. Refer to the [MCP Integration Hub](../docs/guides/mcp-integration/README.md)

---

**Built with the Braid MCP Integration System** - A standardized approach to Model Context Protocol integration for production AI agents.