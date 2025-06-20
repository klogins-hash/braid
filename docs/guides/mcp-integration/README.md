# MCP Integration Documentation Hub (ARCHIVED)

⚠️ **IMPORTANT NOTICE**: MCP integration has been archived in favor of direct API integrations.

**For new agents, use direct integrations from `core/integrations/` instead:**
- `core/integrations/xero/tools.py` - Direct Xero API integration
- `core/integrations/notion/tools.py` - Direct Notion API integration  
- `core/integrations/perplexity/tools.py` - Direct Perplexity API integration

**See [CLAUDE.md](../../CLAUDE.md) for current direct integration patterns.**

---

**Historical Documentation Below** - Model Context Protocol (MCP) integration in Braid agents.

## 📋 Quick Reference for Claude

When creating MCP-enabled agents, **ALWAYS** read these files in this order:

1. **`CLAUDE.md`** (root) - Core MCP workflow and file references
2. **`MCP_SETUP_GUIDE.md`** - Complete setup and configuration
3. **`templates/mcp-agent/README.md`** - Agent template usage
4. **`MCP_DEPLOYMENT_GUIDE.md`** - Production deployment

## 📚 Complete Documentation

### Setup and Configuration
- **[MCP_SETUP_GUIDE.md](./MCP_SETUP_GUIDE.md)** - Comprehensive setup guide with environment configuration, server installation, and testing
- **[MCP_DEPLOYMENT_GUIDE.md](./MCP_DEPLOYMENT_GUIDE.md)** - Production deployment with Docker and Kubernetes

### Templates and Testing  
- **[templates/mcp-agent/](../../templates/mcp-agent/)** - Production-ready MCP agent template
- **[tests/README.md](../../tests/README.md)** - MCP testing framework documentation

### Core Workflow Reference
- **[CLAUDE.md](../../CLAUDE.md)** - Essential guide for Claude when creating MCP agents

## 🚀 Available MCP Servers

| Server | Tools | Use Cases | Status |
|--------|-------|-----------|---------|
| **Xero** | 50+ tools | Financial reports, accounting data | ✅ Ready |
| **Notion** | 19+ tools | Knowledge management, documentation | ✅ Ready |
| **MongoDB** | Various | Database operations | 🔄 In Development |
| **AgentQL** | Various | Web automation | 🔄 In Development |
| **AlphaVantage** | Various | Financial market data | 🔄 In Development |
| **Twilio** | Various | SMS, voice messaging | 🔄 In Development |

**Note**: Perplexity is now available as a direct API integration in `core/integrations/perplexity/` rather than as an MCP server.

## 🛠️ MCP Integration Architecture

```
braid/
├── CLAUDE.md                           # 🎯 START HERE for MCP agents
├── docs/guides/mcp-integration/        # Documentation hub
│   ├── MCP_SETUP_GUIDE.md             # Complete setup guide
│   ├── MCP_DEPLOYMENT_GUIDE.md        # Production deployment
│   └── README.md                      # This file
├── templates/mcp-agent/               # Production-ready template
│   ├── agent.py                       # MCP-enabled agent implementation
│   ├── setup_mcp_servers.sh          # Automated MCP setup
│   └── test_agent.py                 # Agent testing utilities
├── scripts/                           # Automation scripts
│   ├── setup_mcp_servers.sh          # Main MCP setup script
│   └── build_mcp_images.sh           # Docker deployment automation
├── docker/                           # Container configurations
│   ├── mcp-servers/                   # Individual MCP Dockerfiles
│   └── docker-compose.mcp.yml        # MCP services deployment
├── k8s/                              # Kubernetes manifests
│   └── mcp-deployment.yaml           # Production K8s deployment
└── tests/                            # Testing framework
    ├── mcp_test_framework.py         # Comprehensive test suite
    └── test_config.json              # Test configuration
```

## 🔄 MCP Development Workflow

### For New MCP Agents (Claude Reference)

1. **Read Core Files**
   ```bash
   # ALWAYS read these first
   CLAUDE.md
   docs/guides/mcp-integration/MCP_SETUP_GUIDE.md
   templates/mcp-agent/README.md
   ```

2. **Use Template**
   ```bash
   cp -r templates/mcp-agent new-agent-name
   cd new-agent-name
   ```

3. **Setup MCP Servers**
   ```bash
   ./scripts/setup_mcp_servers.sh
   # OR use agent-specific setup
   ./setup_mcp_servers.sh
   ```

4. **Test Integration**
   ```bash
   python tests/mcp_test_framework.py
   python test_agent.py --test-mcp
   ```

5. **Deploy if Needed**
   ```bash
   ./scripts/build_mcp_images.sh
   cd docker && docker-compose -f docker-compose.mcp.yml up -d
   ```

## 🎯 Common MCP Integration Patterns

### Financial Analysis Agents
- **Primary MCP**: Xero (50+ financial tools)
- **Secondary MCPs**: Notion (reporting)
- **Direct Integrations**: Perplexity (research via `core/integrations/perplexity/`)
- **Template**: Use `templates/mcp-agent/` as base

### Research and Content Agents  
- **Primary MCPs**: Notion (documentation), MongoDB (data storage)
- **Direct Integrations**: Perplexity (web research via `core/integrations/perplexity/`)
- **Pattern**: Research → Analyze → Document → Store

### Business Process Agents
- **Primary MCPs**: Xero (financial), Notion (workflow)
- **Secondary MCPs**: Twilio (notifications)
- **Direct Integrations**: Perplexity (market data via `core/integrations/perplexity/`)
- **Pattern**: Monitor → Process → Report → Notify

## 🧪 Testing and Validation

### Automated Testing
```bash
# Test all MCP connections
python tests/mcp_test_framework.py

# Test specific agent
python templates/mcp-agent/test_agent.py --all

# Performance testing
python tests/mcp_test_framework.py --performance
```

### Manual Validation
```bash
# Check MCP server status
./scripts/setup_mcp_servers.sh --test-only

# Verify environment
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Perplexity (Direct Integration):', bool(os.getenv('PERPLEXITY_API_KEY')))
print('Xero (MCP):', bool(os.getenv('XERO_ACCESS_TOKEN')))
print('Notion (MCP):', bool(os.getenv('NOTION_API_KEY')))
"
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and deploy MCP servers
./scripts/build_mcp_images.sh --push --test

# Deploy with Docker Compose
cd docker
docker-compose -f docker-compose.mcp.yml up -d
```

### Kubernetes Deployment
```bash
# Update registry and deploy
./scripts/build_mcp_images.sh --registry your-registry.com --push
kubectl apply -f k8s/mcp-deployment.yaml
```

## 🔧 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Check environment variables in `.env`
   - Verify Node.js 18+ installation
   - Run MCP test framework

2. **Agent Not Using MCP Tools**
   - Verify MCP clients are started in agent code
   - Check tool definitions match MCP server capabilities
   - Review agent logs for connection errors

3. **Performance Issues**
   - Monitor MCP server resource usage
   - Check connection pooling configuration
   - Review MCP server logs

### Debug Commands
```bash
# Enable verbose logging
DEBUG=mcp:* python your_agent.py

# Test individual MCP servers  
python tests/mcp_test_framework.py --server xero
python tests/mcp_test_framework.py --server notion

# Check agent MCP integration
python templates/mcp-agent/test_agent.py --test-tools
```

## 📈 Monitoring and Observability

### Health Checks
- MCP server health endpoints
- Agent integration status monitoring
- Performance metrics collection

### Logging
- Structured logging for MCP operations
- Error tracking and alerting
- Performance monitoring dashboards

## 🔮 Future Enhancements

### Planned MCP Integrations
- Enhanced MongoDB integration
- Advanced AgentQL web automation
- Extended Twilio messaging capabilities
- Custom MCP server development tools

### System Improvements
- Auto-scaling MCP server pools
- Advanced caching mechanisms
- Multi-region MCP deployment
- Enhanced security frameworks

---

**For Claude**: When creating MCP-enabled agents, always start by reading `CLAUDE.md` which contains the complete workflow and all necessary file references. This ensures consistent, reliable MCP integration across all Braid agents.