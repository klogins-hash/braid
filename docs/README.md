# Braid Documentation Hub

Welcome to the Braid documentation! This guide will help you navigate our organized documentation structure to find exactly what you need.

## 📚 Documentation Structure

### 🚀 Getting Started
**New to Braid? Start here!**

- **[Quick Start Guide](getting-started/QUICK_START.md)** - Get up and running in 5 minutes
- **[Claude Code Guide](getting-started/CLAUDE_CODE_GUIDE.md)** - Essential Claude Code integration patterns

### 🎓 Tutorials
**Step-by-step learning paths**

- **[LangGraph Agent Guide](tutorials/langgraph_agent_guide/)** - Complete 15-part series
  - [00 Introduction](tutorials/langgraph_agent_guide/00_introduction.md) - Overview and setup
  - [01 Core Concepts](tutorials/langgraph_agent_guide/01_core_concepts.md) - States, nodes, and edges
  - [02 Building an Agent](tutorials/langgraph_agent_guide/02_building_an_agent.md) - Your first agent
  - [03 Adding Memory](tutorials/langgraph_agent_guide/03_adding_memory.md) - Persistent conversations
  - [04 Advanced State Management](tutorials/langgraph_agent_guide/04_advanced_state_management.md)
  - [05 Advanced Graph Patterns](tutorials/langgraph_agent_guide/05_advanced_graph_patterns.md)
  - [06 Debugging and Control](tutorials/langgraph_agent_guide/06_debugging_and_control.md)
  - [07 Deployment](tutorials/langgraph_agent_guide/07_deployment.md)
  - [08 Production Best Practices](tutorials/langgraph_agent_guide/08_production_best_practices.md) ⭐
  - [09 Advanced Agent Architectures](tutorials/langgraph_agent_guide/09_advanced_agent_architectures.md)
  - [10 Environment and Secrets](tutorials/langgraph_agent_guide/10_environment_and_secrets.md)
  - [11 Agent Development Playbook](tutorials/langgraph_agent_guide/11_agent_development_playbook.md)
  - [12 Core Memory Components](tutorials/langgraph_agent_guide/12_core_memory_components.md)
  - [13 RAG with LlamaIndex](tutorials/langgraph_agent_guide/13_rag_with_llamaindex.md)
  - [14 Core Tool Toolkit](tutorials/langgraph_agent_guide/14_core_tool_toolkit.md)
  - [15 Agent Creation Checklist](tutorials/langgraph_agent_guide/15_agent_creation_checklist.md)

### 🛠️ Development Guides
**Building production-ready agents**

#### Agent Development
- **[Agent Development Best Practices](guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md)** ⭐ - Essential patterns and anti-patterns
- **[Agent Creator Template](guides/agent-development/agent-creator-template.md)** - Standard template structure

#### MCP Integration (Model Context Protocol)
- **[MCP Integration Hub](guides/mcp-integration/README.md)** ⭐ - Complete MCP documentation portal
- **[MCP Setup Guide](guides/mcp-integration/MCP_SETUP_GUIDE.md)** ⭐ - Comprehensive setup and configuration
- **[MCP Deployment Guide](guides/mcp-integration/MCP_DEPLOYMENT_GUIDE.md)** ⭐ - Production deployment with Docker/K8s

#### API Integrations  
- **[Live API Integration Checklist](guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md)** ⭐ - Pre-development checklist
- **[Xero API Integration Guide](guides/api-integrations/XERO_API_INTEGRATION_GUIDE.md)** ⭐ - Comprehensive troubleshooting

### 📖 Reference
**Quick lookup and technical details**

- **[CLI Usage](reference/CLI_USAGE.md)** - Command line interface reference
- **[Tool Reference](reference/TOOL_REFERENCE.md)** - Available tools and usage
- **[Tool Selection Guide](reference/TOOL_SELECTION_GUIDE.md)** - Choosing the right tools

## 🎯 Quick Navigation by Use Case

### I'm New to Braid
1. [Quick Start Guide](getting-started/QUICK_START.md)
2. [LangGraph Introduction](tutorials/langgraph_agent_guide/00_introduction.md)
3. [Building Your First Agent](tutorials/langgraph_agent_guide/02_building_an_agent.md)

### I'm Building a Production Agent
1. **[Agent Development Best Practices](guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md)** ⭐
2. **[Live API Integration Checklist](guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md)** ⭐
3. **[MCP Integration Hub](guides/mcp-integration/README.md)** ⭐ (for MCP-enabled agents)
4. [Production Best Practices](tutorials/langgraph_agent_guide/08_production_best_practices.md)

### I'm Integrating with APIs
1. **[Live API Integration Checklist](guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md)** ⭐
2. **[Xero API Integration Guide](guides/api-integrations/XERO_API_INTEGRATION_GUIDE.md)** (for Xero specifically)
3. [Tool Selection Guide](reference/TOOL_SELECTION_GUIDE.md)

### I'm Troubleshooting Issues
1. **[Agent Development Best Practices](guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md)** - Common anti-patterns
2. **[Xero API Integration Guide](guides/api-integrations/XERO_API_INTEGRATION_GUIDE.md)** - API-specific issues
3. [Debugging and Control](tutorials/langgraph_agent_guide/06_debugging_and_control.md)

### I'm Planning Deployment
1. [Deployment Guide](tutorials/langgraph_agent_guide/07_deployment.md)
2. [Production Best Practices](tutorials/langgraph_agent_guide/08_production_best_practices.md)
3. [Environment and Secrets](tutorials/langgraph_agent_guide/10_environment_and_secrets.md)

## ⭐ Key Documents for Complex Agents

These documents were created from real production experience and prevent major issues:

### 🚨 Critical for LangSmith Tracing
- **[Agent Development Best Practices](guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md)**
  - Prevents isolated traces (tools appearing as separate events)
  - Shows proper agent → tools → agent flow
  - Includes real examples from financial forecasting agent

### 🚨 Critical for Live API Integration
- **[Live API Integration Checklist](guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md)**
  - Pre-development checklist preventing common issues
  - Authentication, data handling, and tracing patterns
  - API-specific considerations and debugging tools

### 🚨 Critical for Xero Integration
- **[Xero API Integration Guide](guides/api-integrations/XERO_API_INTEGRATION_GUIDE.md)**
  - OAuth vs client credentials confusion
  - XML vs JSON response handling
  - Real vs fake data transparency issues

## 📁 Templates and Examples

Production-ready templates with battle-tested patterns:

### Financial Forecasting Agent Template
- **Location**: `templates/production-financial-agent/`
- **Features**: Live Xero/Perplexity/Notion integration, proper LangSmith tracing
- **Use Case**: Complex multi-API agents with financial data processing

### Other Templates
- **Data Enrichment**: `templates/data-enrichment/`
- **Memory Agent**: `templates/memory-agent/`
- **React Agent**: `templates/react-agent/`
- **Retrieval Agent**: `templates/retrieval-agent-template/`

## 🔧 Development Tools

### MCP (Model Context Protocol) System
- **Complete Documentation**: [MCP Integration Hub](guides/mcp-integration/README.md)
- **Production Templates**: `templates/mcp-agent/` - Ready-to-use MCP agent template
- **Testing Framework**: `tests/mcp_test_framework.py` - Comprehensive MCP testing
- **Deployment Automation**: `scripts/setup_mcp_servers.sh`, `scripts/build_mcp_images.sh`
- **Container Configs**: `docker/mcp-servers/`, `k8s/mcp-deployment.yaml`

### Core Tools and Utilities
- **Tool Loader**: `core/tool_loader.py`
- **Memory Management**: `core/memory.py`
- **Integration Helpers**: `core/integrations/`

---

## 💡 Pro Tips

1. **Start with the checklist**: Always use the [Live API Integration Checklist](guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md) before building complex agents
2. **Check LangSmith traces**: Use patterns from [Agent Development Best Practices](guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md) to ensure unified workflow traces
3. **Use production templates**: Copy from `templates/production-financial-agent/` for complex multi-API agents
4. **Validate early**: Test API connections and data parsing before building the full workflow

## 🤝 Contributing

When adding new documentation:
- Place guides by use case in appropriate `guides/` subfolder
- Update this navigation index
- Include real examples and anti-patterns when possible
- Cross-reference related documents

---

*This documentation structure was created based on real production experience building complex financial forecasting agents with live API integrations.*