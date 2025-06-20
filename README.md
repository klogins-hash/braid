# Braid - AI Agent Development System

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Build sophisticated AI agents through natural conversation with Claude Code. No templates, no complex setup - just describe what you want and get production-ready agents in minutes.**

## ⚡ **Simple as 1-2-3**

```
1. "Please prepare to create a LangGraph agent by reviewing the docs and examples"
2. "I need an agent that [describes what you want it to do]"  
3. "Optional Pro Pack and production deployment" (for enterprise features)
```

**That's it.** Claude Code handles all the complexity - architecture, integrations, testing, deployment.

## 🎯 **What You Get**

**🤖 Production-Ready Agents**
- LangGraph workflows with proper observability
- Built-in error handling and fallbacks
- Enterprise-grade security and monitoring

**🔌 40+ Pre-Built Integrations**  
- Google Workspace, Slack, Xero, Notion, Perplexity
- Financial data, web research, document generation
- Team communication, data processing, workflows

**📦 Complete Deployment**
- Docker containers with optimized configurations
- Monitoring, logging, and health checks
- Kubernetes manifests (when needed)

## 💬 Real Examples

### Financial Operations Assistant
```
Requirements: Pull financials from Xero → Analyze trends → Generate reports in Notion → Notify team on Slack
Tools: MCPs: xero, notion + Tools: slack, gworkspace
Result: Fully automated financial operations and reporting system
```

### Autonomous AR Clerk
```
Requirements: Monitor Google Drive for contracts → Create invoices in Xero → Automate collections via email/SMS
Tools: MCPs: xero, twilio + Tools: gworkspace, slack
Result: End-to-end autonomous accounts receivable management
```

### Sales Intelligence Engine
```
Requirements: Scan web for sales triggers → Enrich with Notion CRM data → Brief team on Slack → Draft outreach in Gmail
Tools: MCPs: perplexity, notion + Tools: gworkspace, slack
Result: Proactive sales opportunity discovery and outreach engine
```

## Getting Started

### Prerequisites
- Python 3.11+ installed
- Access to Claude Code
- API keys for desired integrations (OpenAI, Slack, etc.)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd braid

# Set up environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies only (recommended)
pip install -e .

# Or install with specific capabilities:
pip install -e '.[financial,xero,notion]'     # Financial agent
pip install -e '.[research,perplexity]'       # Research agent  
pip install -e '.[complete-financial]'        # Full financial stack
```

### 📦 Smart Dependencies
Braid uses selective installation - install only what you need:
- **Core**: Essential LangGraph + LangChain components
- **Integrations**: `xero`, `notion`, `perplexity`, `gworkspace`, `slack`
- **Agent Types**: `financial`, `research`, `retrieval`, `memory`
- **Bundles**: `complete-financial`, `complete-research`

See [Dependency Guide](docs/guides/DEPENDENCY_GUIDE.md) for details.

### Start Building
1. **Ask Claude Code to prepare**: "Please prepare to create a LangGraph agent by reviewing the docs and examples."
2. **Fill out requirements**: Use [agent-creator-template.md](./agent-creator-template.md)  
3. **Create your agent**: "Please read my requirements and create the agent"
4. **Enhance & deploy**: Optional Pro Pack and production deployment

## Documentation

**For Users**:
- **[agent-creator-template.md](./agent-creator-template.md)** - Requirements template
- **[QUICK_START.md](./QUICK_START.md)** - 5-minute setup guide

**For Claude Code**:
- **[CLAUDE_CODE_GUIDE.md](./CLAUDE_CODE_GUIDE.md)** - Complete development reference
- **[TOOL_REFERENCE.md](./TOOL_REFERENCE.md)** - Tool capabilities
- **[TOOL_SELECTION_GUIDE.md](./TOOL_SELECTION_GUIDE.md)** - Decision frameworks

**Advanced Topics**:
- **[langgraph_agent_guide/](./langgraph_agent_guide/)** - Deep LangGraph concepts
- **[PRODUCTION_MCP_SUMMARY.md](./PRODUCTION_MCP_SUMMARY.md)** - MCP architecture

## What Makes Braid Different

### Traditional Approach
```
1. Learn LangGraph concepts (weeks)
2. Set up project structure (hours)  
3. Configure tools and integrations (days)
4. Write boilerplate code (hours)
5. Set up testing framework (hours)
6. Configure deployment (days)
7. Debug and iterate (weeks)
```

### Braid + Claude Code
```
1. Describe what you want (minutes)
2. Get production-ready agent (minutes)
3. Test and iterate (minutes)
4. Deploy to production (minutes)
```

## Enterprise Features

- **Security**: Non-root containers, secret management, network isolation
- **Monitoring**: Health checks, metrics collection, error tracking
- **Scalability**: Kubernetes support, resource optimization, auto-scaling ready
- **Reliability**: Circuit breakers, retry logic, graceful degradation
- **Observability**: LangSmith integration, detailed tracing, performance monitoring

---

**🚀 Ready to build sophisticated AI agents?** Start by asking Claude Code to prepare for agent development, then describe what you want to build.