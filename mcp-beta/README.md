# MCP Beta Archive

⚠️ **DEPRECATED**: This folder contains archived MCP (Model Context Protocol) infrastructure that is no longer actively maintained.

## What's Here

This folder contains the original custom MCP server implementations and infrastructure that were used in early versions of Braid agents. These have been **replaced with direct API integrations** for better reliability and simplicity.

### Archived Components

- **MCP Servers**: Custom Node.js MCP server implementations
  - `xero-mcp-server/` - Xero API MCP server
  - `notion-mcp-server/` - Notion API MCP server
  
- **Infrastructure**: Docker and Kubernetes deployment files
  - `docker-compose.mcp.yml` - Docker composition for MCP servers
  - `mcp-deployment.yaml` - Kubernetes MCP deployment
  - `mcp-nginx.conf` - Nginx configuration for MCP routing
  
- **Scripts**: Setup and management scripts
  - `setup_mcp_servers.sh` - MCP server setup automation
  - `build_mcp_images.sh` - Docker image build scripts
  - `start-mcp-servers.sh` / `stop-mcp-servers.sh` - Server management
  
- **Testing**: MCP-specific test frameworks
  - `mcp_test_framework.py` - Python MCP testing utilities
  - `test_real_mcp.py` - Integration tests for MCP servers

## Why Archived?

We moved away from custom MCP infrastructure to **direct API integrations** because:

1. **Complexity**: MCP added unnecessary layers for simple API calls
2. **Reliability**: Fewer failure points with direct API calls
3. **Maintenance**: Direct integrations are easier to debug and maintain
4. **Deployment**: No need for Docker/K8s infrastructure
5. **Development Speed**: Faster to implement new integrations

## Current Architecture

**New Approach (Recommended)**:
```
Financial Agent → Direct API Integrations
├── core/integrations/xero/tools.py
├── core/integrations/notion/tools.py  
└── core/integrations/perplexity/tools.py
```

**Old Approach (Archived)**:
```
Financial Agent → MCP Servers → JSON-RPC → API Calls
├── Local Xero MCP Server (Node.js)
├── Local Notion MCP Server (Node.js)
└── Docker/K8s orchestration
```

## Future Use

These files are kept for:
- **Reference**: Understanding the evolution of Braid architecture
- **Research**: Potential future MCP experiments
- **Recovery**: Fallback if direct integrations prove insufficient

**Note**: Do not use these files for new agent development. Use the direct API integrations in `core/integrations/` instead.

## Migration Guide

If you have existing agents using MCP, migrate to direct integrations:

1. Replace MCP tool calls with direct API tools from `core/integrations/`
2. Remove MCP server startup/shutdown logic
3. Update environment variables to use direct API authentication
4. Test the agent with the new direct integration approach

For questions about migration, refer to the main Braid documentation or the updated financial forecasting agent as an example.