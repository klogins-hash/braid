# Claude Assistant Guide for Braid Development

This file provides essential guidance for Claude when working on Braid projects, especially when creating new agents with MCP (Model Context Protocol) integration.

## 🚀 Creating New MCP-Enabled Agents

When a user requests a new agent with MCP capabilities, follow this standardized process:

### 1. Read Key MCP Documentation First

**ALWAYS** read these files first to understand the current MCP setup:

```bash
# Core MCP documentation - READ THESE FIRST
docs/guides/mcp-integration/MCP_SETUP_GUIDE.md
docs/guides/mcp-integration/MCP_DEPLOYMENT_GUIDE.md
templates/mcp-agent/README.md
tests/README.md
```

### 2. Use the MCP Agent Template

Start with the proven template instead of building from scratch:

```bash
# Template location
templates/mcp-agent/
├── agent.py              # Main MCP-enabled agent
├── requirements.txt      # Dependencies  
├── .env.example         # Environment template
├── setup_mcp_servers.sh # MCP setup script
├── test_agent.py       # Testing utilities
├── Dockerfile          # Container config
└── README.md           # Usage guide
```

### 3. Standard MCP Integration Process

1. **Copy Template**: `cp -r templates/mcp-agent new-agent-name`
2. **Review Available MCP Servers**: Check current integrations in `docs/guides/mcp-integration/MCP_SETUP_GUIDE.md`
3. **Configure Environment**: Use `.env.example` as starting point
4. **Set Up MCP Servers**: Run `./scripts/setup_mcp_servers.sh` 
5. **Test Integration**: Use `tests/mcp_test_framework.py`
6. **Deploy if Needed**: Use `docker/` and `k8s/` configurations

### 4. Available MCP Servers (Current)

Reference these when designing agent capabilities:

| Server | Tools | Use Cases |
|--------|-------|-----------|
| **Xero** | financial reports, invoices | Accounting, financial data |
| **Notion** | page creation, search | Documentation, knowledge management |

### 4.1. Available Direct Integrations (Non-MCP)

| Integration | Tools | Use Cases |
|-------------|-------|-----------|
| **Perplexity** | web search, research, market analysis | Real-time web research, market insights |

### 5. Key Scripts to Reference

- `scripts/setup_mcp_servers.sh` - Automated MCP setup
- `scripts/build_mcp_images.sh` - Docker deployment
- `tests/mcp_test_framework.py` - Testing framework

## 📋 Agent Development Checklist

When creating any new agent, verify:

- [ ] Read MCP documentation first
- [ ] Use MCP template as starting point  
- [ ] Configure required environment variables
- [ ] Set up MCP servers if needed
- [ ] Test MCP connections before coding
- [ ] Follow existing patterns in `templates/mcp-agent/agent.py`
- [ ] Include error handling and graceful shutdown
- [ ] Add appropriate logging
- [ ] Create tests using the test framework
- [ ] Document any new MCP integrations

## 🔧 MCP Integration Patterns

### Standard MCP Client Setup
```python
from templates.mcp_agent.agent import MCPManager, MCPClient

# Use existing MCPManager
mcp_manager = MCPManager()
results = mcp_manager.start_all()
```

### Adding New MCP Servers
```python
# Add to MCPManager.setup_clients() method
if os.getenv('NEW_SERVICE_API_KEY'):
    self.clients['new_service'] = MCPClient(
        server_path="node",
        server_args=["path/to/new-mcp-server.js"],
        env_vars={"NEW_SERVICE_API_KEY": os.getenv('NEW_SERVICE_API_KEY')}
    )
```

### Tool Creation Pattern
```python
@tool
def new_mcp_tool(param: str) -> str:
    """Tool description for LLM."""
    client = mcp_manager.get_client('service_name')
    if not client:
        return "Service not available"
    
    result = client.call_tool("tool_name", {"param": param})
    return str(result.get("content", "No result"))
```

## 📁 File Structure Reference

### Core MCP Files
```
braid/
├── docs/guides/mcp-integration/    # MCP documentation
├── templates/mcp-agent/           # Agent template
├── scripts/                       # Setup and build scripts  
├── docker/                        # Container configurations
├── k8s/                          # Kubernetes manifests
├── tests/                        # Testing framework
└── CLAUDE.md                     # This file
```

### When Creating Financial Agents
- Use existing `financial-forecast-agent/` as reference
- Check `test_real_mcp.py` for proven MCP patterns
- Reference Xero MCP integration examples

### When Creating Research Agents  
- Reference web research patterns in templates
- Consider Notion MCP for report generation

## 🚨 Important Notes

### Always Check Environment
```bash
# Before starting any MCP work, verify:
ls docs/guides/mcp-integration/     # Documentation exists
ls templates/mcp-agent/            # Template is available  
ls scripts/setup_mcp_servers.sh    # Setup script exists
```

### MCP Server Dependencies
- **Node.js 18+** required for all MCP servers
- **Environment variables** must be configured
- **API keys** needed for each service

### Testing Requirements
- Always test MCP connections before integration
- Use `tests/mcp_test_framework.py` for validation
- Run tests: `python tests/mcp_test_framework.py`

### Deployment Considerations
- Use Docker configurations in `docker/`
- Reference Kubernetes manifests in `k8s/`
- Follow security best practices for API keys

## 🔄 Workflow Summary

1. **Read** → MCP documentation and templates
2. **Copy** → Use `templates/mcp-agent/` as base
3. **Configure** → Environment and MCP servers  
4. **Test** → Verify MCP connections work
5. **Develop** → Follow established patterns
6. **Deploy** → Use provided Docker/K8s configs

## 📞 Quick Reference Commands

```bash
# Setup MCP servers
./scripts/setup_mcp_servers.sh

# Test MCP connections  
python tests/mcp_test_framework.py

# Test specific agent
python templates/mcp-agent/test_agent.py

# Build for deployment
./scripts/build_mcp_images.sh

# Deploy with Docker
cd docker && docker-compose -f docker-compose.mcp.yml up -d
```

---

**Remember**: The MCP integration system is fully built and documented. Always use existing templates and patterns rather than rebuilding from scratch. The goal is consistency and reliability across all Braid agents.