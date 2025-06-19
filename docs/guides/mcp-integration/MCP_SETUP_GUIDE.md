# MCP Integration Setup Guide

A comprehensive guide for setting up Model Context Protocol (MCP) servers in Braid agents.

## Overview

This guide covers the complete setup process for integrating MCP servers into your Braid agents, from initial configuration to production deployment.

## Table of Contents

1. [Quick Start](#quick-start)
2. [MCP Server Types](#mcp-server-types)
3. [Environment Setup](#environment-setup)
4. [Automated Setup](#automated-setup)
5. [Manual Setup](#manual-setup)
6. [Testing MCP Servers](#testing-mcp-servers)
7. [Agent Integration](#agent-integration)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

## Quick Start

For existing agents with MCP configuration:

```bash
# 1. Run the automated MCP setup
./scripts/setup_mcp_servers.sh

# 2. Test MCP connections
python3 test_mcp_connections.py

# 3. Start your agent
python3 your_agent.py
```

## MCP Server Types

### Currently Supported MCP Servers

| MCP Server | Category | Description | Repository |
|------------|----------|-------------|------------|
| **Perplexity** | Data/Research | Real-time web search and research | `https://github.com/ppl-ai/modelcontextprotocol` |
| **Xero** | Finance | Accounting and financial management | `https://github.com/XeroAPI/xero-mcp-server` |
| **Notion** | Productivity | Workspace and knowledge management | `https://github.com/makenotion/notion-mcp-server` |
| **MongoDB** | Data | Database operations and management | `https://github.com/mongodb-js/mongodb-mcp-server` |
| **AlphaVantage** | Finance | Stock market and financial data | `https://github.com/calvernaz/alphavantage` |
| **Twilio** | Communication | SMS, voice, and messaging APIs | `https://github.com/twilio-labs/mcp` |

### MCP Capabilities by Server

#### Perplexity MCP Tools
- `perplexity_ask`: Real-time conversational search
- `perplexity_research`: Deep research with citations
- `perplexity_reason`: Advanced reasoning tasks

#### Xero MCP Tools (50+ tools)
- Financial reporting (P&L, Balance Sheet, Trial Balance)
- Invoice and payment management
- Contact and customer management
- Bank transaction processing
- Tax calculation and tracking

#### Notion MCP Tools (19+ tools)
- Page and database creation/management
- Content editing and formatting
- Workspace search and organization
- Comment and collaboration features

## Environment Setup

### 1. Required Environment Variables

Create a `.env` file with the following variables based on your MCP servers:

```bash
# Core LLM
OPENAI_API_KEY=your_openai_key

# LangSmith (optional but recommended)
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your_project_name

# Perplexity MCP
PERPLEXITY_API_KEY=your_perplexity_key

# Xero MCP  
XERO_ACCESS_TOKEN=your_xero_bearer_token
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret

# Notion MCP
NOTION_API_KEY=your_notion_integration_token

# MongoDB MCP (optional)
MONGODB_CONNECTION_STRING=your_mongodb_connection

# AlphaVantage MCP (optional)
ALPHAVANTAGE_API_KEY=your_alphavantage_key

# Twilio MCP (optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_API_KEY=your_twilio_key
TWILIO_API_SECRET=your_twilio_secret
```

### 2. API Key Setup Instructions

#### Perplexity API Key
1. Visit [https://www.perplexity.ai/](https://www.perplexity.ai/)
2. Sign up and navigate to API settings
3. Generate an API key
4. Add to `.env` as `PERPLEXITY_API_KEY`

#### Xero API Setup
1. Visit [https://developer.xero.com/](https://developer.xero.com/)
2. Create an app and get Client ID/Secret
3. Complete OAuth flow to get Bearer Token
4. Add credentials to `.env`

#### Notion API Setup
1. Visit [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Integration Token
4. Add to `.env` as `NOTION_API_KEY`

## Automated Setup

### Using the MCP Setup Script

```bash
# Make the script executable
chmod +x scripts/setup_mcp_servers.sh

# Run the automated setup
./scripts/setup_mcp_servers.sh

# This will:
# 1. Clone all required MCP server repositories
# 2. Install dependencies
# 3. Validate environment variables
# 4. Test server connections
# 5. Generate server startup scripts
```

### What the Automated Setup Does

1. **Repository Management**
   - Clones MCP server repositories to `./mcp_servers/`
   - Updates existing repositories if already present
   - Installs Node.js dependencies for each server

2. **Environment Validation**
   - Checks for required environment variables
   - Validates API key formats
   - Tests basic connectivity where possible

3. **Server Configuration**
   - Generates individual startup scripts for each MCP server
   - Creates a unified `start_all_mcp_servers.sh` script
   - Sets up proper environment variable passing

4. **Testing Framework**
   - Generates MCP connection test scripts
   - Creates health check endpoints
   - Provides debugging utilities

## Manual Setup

If you prefer manual setup or need to customize the process:

### 1. Clone MCP Server Repositories

```bash
# Create MCP servers directory
mkdir -p mcp_servers && cd mcp_servers

# Clone Perplexity MCP
git clone https://github.com/ppl-ai/modelcontextprotocol.git perplexity
cd perplexity/perplexity-ask && npm install && cd ../..

# Clone Xero MCP
git clone https://github.com/XeroAPI/xero-mcp-server.git xero
cd xero && npm install && cd ..

# Clone Notion MCP
git clone https://github.com/makenotion/notion-mcp-server.git notion
cd notion && npm install && npm run build && cd ..

# Return to project root
cd ..
```

### 2. Create Startup Scripts

Create individual startup scripts for each MCP server:

**`scripts/start_perplexity_mcp.sh`:**
```bash
#!/bin/bash
cd mcp_servers/perplexity/perplexity-ask
PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY node dist/index.js
```

**`scripts/start_xero_mcp.sh`:**
```bash
#!/bin/bash
cd mcp_servers/xero
XERO_CLIENT_BEARER_TOKEN=$XERO_ACCESS_TOKEN \
XERO_CLIENT_ID=$XERO_CLIENT_ID \
XERO_CLIENT_SECRET=$XERO_CLIENT_SECRET \
node dist/index.js
```

**`scripts/start_notion_mcp.sh`:**
```bash
#!/bin/bash
cd mcp_servers/notion
NOTION_API_KEY=$NOTION_API_KEY node bin/cli.mjs
```

### 3. Create Master Startup Script

**`scripts/start_all_mcp_servers.sh`:**
```bash
#!/bin/bash
# Start all MCP servers for the agent

echo "🚀 Starting all MCP servers..."

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found"
    exit 1
fi

# Start Perplexity MCP
if [ ! -z "$PERPLEXITY_API_KEY" ]; then
    echo "📊 Starting Perplexity MCP..."
    ./scripts/start_perplexity_mcp.sh &
    PERPLEXITY_PID=$!
    echo "   PID: $PERPLEXITY_PID"
fi

# Start Xero MCP
if [ ! -z "$XERO_ACCESS_TOKEN" ]; then
    echo "💰 Starting Xero MCP..."
    ./scripts/start_xero_mcp.sh &
    XERO_PID=$!
    echo "   PID: $XERO_PID"
fi

# Start Notion MCP
if [ ! -z "$NOTION_API_KEY" ]; then
    echo "📝 Starting Notion MCP..."
    ./scripts/start_notion_mcp.sh &
    NOTION_PID=$!
    echo "   PID: $NOTION_PID"
fi

# Save PIDs for cleanup
echo "$PERPLEXITY_PID $XERO_PID $NOTION_PID" > mcp_servers.pid

echo "✅ All MCP servers started!"
echo "🛑 To stop: ./scripts/stop_all_mcp_servers.sh"

# Keep script running
wait
```

## Testing MCP Servers

### Automated Testing

```bash
# Test all MCP server connections
python3 test_mcp_connections.py

# Test specific MCP server
python3 test_mcp_connections.py --server perplexity
python3 test_mcp_connections.py --server xero
python3 test_mcp_connections.py --server notion
```

### Manual Testing

```bash
# Start MCP servers
./scripts/start_all_mcp_servers.sh

# In another terminal, test individual servers
python3 -c "
import subprocess
import json

# Test Perplexity MCP
process = subprocess.Popen(
    ['node', 'mcp_servers/perplexity/perplexity-ask/dist/index.js'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env={'PERPLEXITY_API_KEY': 'your_key'}
)

# Send initialization request
init_request = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {'name': 'test', 'version': '1.0.0'}
    }
}

process.stdin.write(json.dumps(init_request) + '\n')
process.stdin.flush()

response = process.stdout.readline()
print('Response:', response)
process.terminate()
"
```

## Agent Integration

### 1. MCP Client Integration

Add MCP client functionality to your agent:

```python
# your_agent.py
import subprocess
import json
from typing import Dict, Any, List

class MCPClient:
    def __init__(self, server_path: str, server_args: list = None, env_vars: dict = None):
        self.server_path = server_path
        self.server_args = server_args or []
        self.env_vars = env_vars or {}
        self.process = None
        
    def start(self) -> bool:
        """Start the MCP server process."""
        env = os.environ.copy()
        env.update(self.env_vars)
        
        cmd = [self.server_path] + self.server_args
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            return True
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process:
            raise Exception("MCP server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        response = self.process.stdout.readline()
        return json.loads(response)
    
    def stop(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            self.process.wait()

class MCPManager:
    def __init__(self):
        self.clients = {}
        
    def setup_perplexity_mcp(self):
        """Setup Perplexity MCP client."""
        self.clients['perplexity'] = MCPClient(
            server_path="node",
            server_args=["mcp_servers/perplexity/perplexity-ask/dist/index.js"],
            env_vars={"PERPLEXITY_API_KEY": os.getenv('PERPLEXITY_API_KEY')}
        )
        
    def setup_xero_mcp(self):
        """Setup Xero MCP client."""
        self.clients['xero'] = MCPClient(
            server_path="node",
            server_args=["mcp_servers/xero/dist/index.js"],
            env_vars={
                "XERO_CLIENT_BEARER_TOKEN": os.getenv('XERO_ACCESS_TOKEN'),
                "XERO_CLIENT_ID": os.getenv('XERO_CLIENT_ID'),
                "XERO_CLIENT_SECRET": os.getenv('XERO_CLIENT_SECRET')
            }
        )
        
    def setup_notion_mcp(self):
        """Setup Notion MCP client."""
        self.clients['notion'] = MCPClient(
            server_path="node", 
            server_args=["mcp_servers/notion/bin/cli.mjs"],
            env_vars={"NOTION_API_KEY": os.getenv('NOTION_API_KEY')}
        )
        
    def start_all(self) -> Dict[str, bool]:
        """Start all configured MCP clients."""
        results = {}
        for name, client in self.clients.items():
            results[name] = client.start()
        return results
        
    def stop_all(self):
        """Stop all MCP clients."""
        for client in self.clients.values():
            client.stop()
```

### 2. Agent Tool Integration

Integrate MCP tools into your LangGraph agent:

```python
from langchain.tools import tool

@tool
def perplexity_research(query: str) -> str:
    """Perform real-time research using Perplexity MCP."""
    mcp_client = mcp_manager.clients['perplexity']
    
    # Initialize if not already done
    init_response = mcp_client.send_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "agent", "version": "1.0.0"}
    })
    
    # Call the research tool
    response = mcp_client.send_request("tools/call", {
        "name": "perplexity_research",
        "arguments": {
            "messages": [{"role": "user", "content": query}]
        }
    })
    
    return response.get("result", {}).get("content", [{}])[0].get("text", "")

@tool
def xero_get_profit_loss() -> str:
    """Get profit and loss report from Xero."""
    mcp_client = mcp_manager.clients['xero']
    
    response = mcp_client.send_request("tools/call", {
        "name": "list-xero-profit-and-loss",
        "arguments": {}
    })
    
    return str(response.get("result", {}))

@tool  
def notion_create_page(title: str, content: str) -> str:
    """Create a new page in Notion."""
    mcp_client = mcp_manager.clients['notion']
    
    response = mcp_client.send_request("tools/call", {
        "name": "API-post-page",
        "arguments": {
            "parent": {"page_id": "your_parent_page_id"},
            "properties": {
                "title": [{"text": {"content": title}}]
            },
            "children": [content]
        }
    })
    
    return str(response.get("result", {}))
```

## Production Deployment

### Docker Configuration

Create a `docker-compose.mcp.yml` for MCP servers:

```yaml
version: '3.8'

services:
  perplexity-mcp:
    build:
      context: ./mcp_servers/perplexity/perplexity-ask
      dockerfile: Dockerfile
    environment:
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
    ports:
      - "3001:3001"
    restart: unless-stopped
    
  xero-mcp:
    build:
      context: ./mcp_servers/xero
      dockerfile: Dockerfile
    environment:
      - XERO_CLIENT_BEARER_TOKEN=${XERO_ACCESS_TOKEN}
      - XERO_CLIENT_ID=${XERO_CLIENT_ID}
      - XERO_CLIENT_SECRET=${XERO_CLIENT_SECRET}
    ports:
      - "3002:3002"
    restart: unless-stopped
    
  notion-mcp:
    build:
      context: ./mcp_servers/notion
      dockerfile: Dockerfile
    environment:
      - NOTION_API_KEY=${NOTION_API_KEY}
    ports:
      - "3003:3003"
    restart: unless-stopped
    
  your-agent:
    build: .
    depends_on:
      - perplexity-mcp
      - xero-mcp
      - notion-mcp
    environment:
      - MCP_PERPLEXITY_URL=http://perplexity-mcp:3001
      - MCP_XERO_URL=http://xero-mcp:3002
      - MCP_NOTION_URL=http://notion-mcp:3003
    ports:
      - "8000:8000"
    restart: unless-stopped

networks:
  default:
    name: mcp-network
```

### Kubernetes Deployment

Create Kubernetes manifests for MCP servers:

```yaml
# k8s/mcp-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-servers
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-servers
  template:
    metadata:
      labels:
        app: mcp-servers
    spec:
      containers:
      - name: perplexity-mcp
        image: your-registry/perplexity-mcp:latest
        env:
        - name: PERPLEXITY_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: perplexity-api-key
        ports:
        - containerPort: 3001
        
      - name: xero-mcp
        image: your-registry/xero-mcp:latest
        env:
        - name: XERO_CLIENT_BEARER_TOKEN
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: xero-bearer-token
        ports:
        - containerPort: 3002
        
      - name: notion-mcp
        image: your-registry/notion-mcp:latest
        env:
        - name: NOTION_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: notion-api-key
        ports:
        - containerPort: 3003
```

## Troubleshooting

### Common Issues

#### 1. MCP Server Won't Start
```bash
# Check environment variables
echo $PERPLEXITY_API_KEY
echo $XERO_ACCESS_TOKEN
echo $NOTION_API_KEY

# Check Node.js version
node --version  # Should be 18+

# Check server logs
cat mcp_servers/perplexity/error.log
```

#### 2. Connection Refused
```bash
# Check if servers are running
ps aux | grep node

# Check ports
lsof -i :3001
lsof -i :3002
lsof -i :3003

# Test manual connection
telnet localhost 3001
```

#### 3. API Authentication Errors
```bash
# Test API keys directly
curl -H "Authorization: Bearer $PERPLEXITY_API_KEY" https://api.perplexity.ai/
curl -H "Authorization: Bearer $XERO_ACCESS_TOKEN" https://api.xero.com/connections
```

### Debug Mode

Enable debug logging for MCP servers:

```bash
# Start with debug logging
DEBUG=mcp:* ./scripts/start_all_mcp_servers.sh

# Or for individual servers
DEBUG=perplexity:* node mcp_servers/perplexity/perplexity-ask/dist/index.js
```

### Health Checks

Create health check endpoints:

```python
# health_check.py
import requests
import subprocess
import json

def check_mcp_health():
    """Check health of all MCP servers."""
    servers = {
        'perplexity': 'mcp_servers/perplexity/perplexity-ask/dist/index.js',
        'xero': 'mcp_servers/xero/dist/index.js',
        'notion': 'mcp_servers/notion/bin/cli.mjs'
    }
    
    results = {}
    
    for name, path in servers.items():
        try:
            # Try to start and get initialization response
            process = subprocess.Popen(
                ['node', path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send initialization
            init_request = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {'name': 'health-check', 'version': '1.0.0'}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + '\n')
            process.stdin.flush()
            
            response = process.stdout.readline()
            data = json.loads(response)
            
            results[name] = {
                'status': 'healthy' if 'result' in data else 'unhealthy',
                'response': data
            }
            
            process.terminate()
            
        except Exception as e:
            results[name] = {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    return results

if __name__ == "__main__":
    health = check_mcp_health()
    for server, status in health.items():
        print(f"{server}: {status['status']}")
```

## Best Practices

### 1. Environment Management
- Use separate `.env` files for different environments
- Never commit API keys to version control
- Use environment variable validation before starting servers

### 2. Error Handling
- Implement retries for MCP communication
- Graceful fallbacks when MCP servers are unavailable
- Comprehensive logging for debugging

### 3. Performance
- Connection pooling for multiple requests
- Caching for frequently accessed data
- Health checks and automatic restart capabilities

### 4. Security
- Use secrets management for production
- Implement proper authentication and authorization
- Regular security updates for MCP server dependencies

## Next Steps

1. **Agent Templates**: Update agent templates to include MCP integration by default
2. **Monitoring**: Add monitoring and alerting for MCP server health
3. **Scaling**: Implement load balancing for high-traffic scenarios
4. **Testing**: Expand automated testing coverage for all MCP integrations

For additional help, see:
- [MCP Testing Framework](./MCP_TESTING_FRAMEWORK.md)
- [Production Deployment Guide](./MCP_PRODUCTION_DEPLOYMENT.md)
- [Troubleshooting Guide](./MCP_TROUBLESHOOTING.md)