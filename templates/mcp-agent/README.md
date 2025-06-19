# MCP-Enabled Agent Template

A production-ready template for creating agents with Model Context Protocol (MCP) integration.

## Features

- **Pre-configured MCP Integration**: Connects to Xero and Notion MCP servers
- **Direct API Integrations**: Perplexity web research via core integrations
- **LangGraph Workflow**: Complete agent workflow with state management
- **Production Ready**: Error handling, logging, and graceful shutdown
- **Docker Support**: Ready for containerized deployment
- **Interactive Mode**: CLI interface for testing and development
- **Automatic Server Management**: Handles MCP server lifecycle

## Quick Start

1. **Copy the template to your project:**
   ```bash
   cp -r templates/mcp-agent your-new-agent
   cd your-new-agent
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MCP servers:**
   ```bash
   ./setup_mcp_servers.sh
   ```

5. **Run the agent:**
   ```bash
   python agent.py
   ```

## Structure

```
mcp-agent/
├── agent.py              # Main agent implementation
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── setup_mcp_servers.sh # MCP server setup script
├── test_agent.py       # Agent testing utilities
├── Dockerfile          # Docker configuration
└── README.md           # This file
```

## Configuration

### Environment Variables

Required for MCP functionality:

```bash
# Core LLM
OPENAI_API_KEY=your_openai_key

# MCP Servers
PERPLEXITY_API_KEY=your_perplexity_key
XERO_ACCESS_TOKEN=your_xero_token
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret
NOTION_API_KEY=your_notion_key

# Optional: LangSmith tracing
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your_project_name
```

### MCP Server Configuration

The agent automatically configures MCP clients based on available environment variables:

- **Perplexity MCP**: Web research and real-time search
- **Xero MCP**: Financial data and accounting operations
- **Notion MCP**: Knowledge management and report generation

## Available Tools

### Research Tools
- `web_research(query)`: Real-time web research using Perplexity
- `search_notion_workspace(query)`: Search existing knowledge base

### Financial Tools
- `get_financial_data(report_type)`: Retrieve financial reports from Xero
- Available report types: profit_and_loss, balance_sheet, trial_balance

### Productivity Tools
- `create_notion_page(title, content)`: Create documentation and reports
- `update_notion_page(page_id, content)`: Update existing pages

## Usage Examples

### Basic Agent Interaction

```python
from agent import MCPAgent

# Create and start agent
agent = MCPAgent()
agent.startup()

# Run a query
response = agent.run("Research the latest fintech trends and create a summary report in Notion")

# Shutdown when done
agent.shutdown()
```

### Interactive Mode

```bash
python agent.py

# Example interactions:
👤 You: Research the latest AI trends in financial services
👤 You: Get our company's profit and loss report for this quarter
👤 You: Create a market analysis report in Notion
```

### Custom Tool Integration

```python
from langchain.tools import tool

@tool
def custom_analysis(data: str) -> str:
    """Perform custom data analysis."""
    # Your custom logic here
    return analysis_result

# Add to agent
agent.graph = create_agent_graph([
    web_research, 
    get_financial_data, 
    create_notion_page,
    custom_analysis  # Your custom tool
])
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t my-mcp-agent .

# Run with environment file
docker run --env-file .env -it my-mcp-agent
```

### Production Deployment

For production deployment with external MCP servers:

```bash
# Update MCP server paths to use network endpoints
export MCP_PERPLEXITY_URL=http://perplexity-mcp:3001
export MCP_XERO_URL=http://xero-mcp:3002
export MCP_NOTION_URL=http://notion-mcp:3003

# Run the agent
python agent.py
```

## Testing

Run the included test suite:

```bash
# Test MCP connections
python test_agent.py --test-mcp

# Test agent workflow
python test_agent.py --test-workflow

# Full test suite
python test_agent.py --all
```

## Customization

### Adding New MCP Servers

1. **Add environment variables:**
   ```python
   # In MCPManager.setup_clients()
   if os.getenv('NEW_MCP_API_KEY'):
       self.clients['new_service'] = MCPClient(
           server_path="node",
           server_args=["path/to/new-mcp/server.js"],
           env_vars={"NEW_MCP_API_KEY": os.getenv('NEW_MCP_API_KEY')}
       )
   ```

2. **Create corresponding tools:**
   ```python
   @tool
   def new_service_action(param: str) -> str:
       """Use the new MCP service."""
       client = mcp_manager.get_client('new_service')
       result = client.call_tool("service_method", {"param": param})
       return str(result)
   ```

3. **Add to agent workflow:**
   ```python
   tools = [
       web_research, 
       get_financial_data, 
       create_notion_page,
       new_service_action  # Add your new tool
   ]
   ```

### Modifying the Workflow

Customize the LangGraph workflow in `create_agent_graph()`:

```python
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add custom nodes
    workflow.add_node("custom_step", custom_step_function)
    
    # Modify edges
    workflow.add_edge("agent", "custom_step")
    workflow.add_edge("custom_step", "tools")
    
    return workflow.compile()
```

## Troubleshooting

### MCP Server Issues

```bash
# Check MCP server status
python -c "from agent import mcp_manager; print(mcp_manager.start_all())"

# Test individual servers
./scripts/test_mcp_connections.py --server perplexity
```

### Common Problems

1. **Environment Variables Not Set**
   - Ensure `.env` file is in the correct location
   - Verify all required API keys are configured

2. **MCP Server Connection Failed**
   - Check if Node.js 18+ is installed
   - Verify MCP server repositories are cloned and built
   - Check API key validity

3. **Agent Workflow Errors**
   - Enable debug logging: `export DEBUG=true`
   - Check LangSmith traces if configured
   - Review error logs in `logs/` directory

## Best Practices

1. **Error Handling**: Always implement try-catch blocks for MCP calls
2. **Resource Management**: Use the agent's startup/shutdown methods
3. **Logging**: Enable comprehensive logging for debugging
4. **Testing**: Regularly test MCP connections and tool functionality
5. **Security**: Never commit API keys to version control

## Next Steps

- Review [MCP Setup Guide](../../docs/guides/mcp-integration/MCP_SETUP_GUIDE.md)
- See [MCP Deployment Guide](../../docs/guides/mcp-integration/MCP_DEPLOYMENT_GUIDE.md)
- Check out [Production Examples](../production-agent/) for advanced patterns