# Braid - AI Agent Development System

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Braid is a comprehensive toolkit designed for building sophisticated LangGraph agents through AI-powered development. Instead of wrestling with complex setup and configuration, you work directly with Claude Code to create production-ready agents in minutes.

## Why Braid?

| Dimension | Traditional No-Code | Manual Coding | Braid + Claude Code |
| :--- | :--- | :--- | :--- |
| **Setup Time** | Minutes, limited scope | Hours/Days of boilerplate | Minutes, any complexity |
| **Customization** | Limited to presets | Full control, high effort | Full control, AI-assisted |
| **Production Ready** | Basic deployment | Complex infrastructure setup | Enterprise-grade packaging |
| **Debugging** | Black box flows | Manual instrumentation | Built-in observability |
| **Integration** | Preset connectors only | Build everything yourself | 40+ tools + direct API integrations |

## What You Get

Braid provides everything needed for professional agent development:

- **🏗️ Agent Architecture**: Production-ready LangGraph patterns
- **🛠️ 40+ Tools**: Google Workspace, Slack, data processing, APIs, workflows
- **🔌 Direct Integrations**: Perplexity, Xero, Notion, Google Workspace, Slack  
- **💾 Memory Systems**: Persistent conversations, RAG, vector storage
- **📦 Production Deployment**: Docker, Kubernetes, monitoring, security
- **🧪 Testing Framework**: Unit tests, integration tests, debugging tools

## How It Works

**You don't use CLIs or write boilerplate.** You work with Claude Code to build agents through natural conversation:

### Step 1: Prepare Claude Code
```
"Please prepare to create a LangGraph agent by reading your development guide."
```

Claude Code will read [CLAUDE_CODE_GUIDE.md](docs/getting-started/CLAUDE_CODE_GUIDE.md) and understand the full system.

### Step 2: Define Your Agent Requirements

Fill out the [agent-creator-template.md](docs/guides/agent-development/agent-creator-template.md) with your requirements:

```markdown
## Core Tasks and Sequences of Agent
**Your Requirements**: 
I need an agent that monitors customer support tickets, analyzes sentiment, 
and posts daily summaries to Slack with trend data in Google Sheets.

## Tools & Integrations Required
**Your Required Tools & Integrations**: 
[Claude Code will recommend optimal combinations]
```

### Step 3: Create Your Agent
```
"Please read my agent requirements and create the agent."
```

Claude Code will:
- Analyze your requirements
- Select optimal tools and integrations
- Create production-ready agent structure
- Set up all configurations and dependencies
- Provide testing and deployment instructions

### Step 4: Enhance with Pro Pack (Optional)
```
"Please add the Braid Pro Pack for enhanced testing and monitoring."
```

This adds:
- Advanced unit test suites
- Integration test frameworks
- Performance monitoring
- Error handling enhancements
- Development workflows

### Step 5: Prepare for Deployment
```
"Please prepare this agent for production deployment."
```

Claude Code will:
- Package with optimized Docker containers
- Set up production monitoring
- Create deployment documentation
- Configure security hardening
- Generate Kubernetes manifests (if needed)

## Available Capabilities

### 🛠️ Built-in Tools
- **Google Workspace**: Gmail, Calendar, Sheets, Drive
- **Slack**: Messaging, notifications, file sharing (12 tools)
- **Data Processing**: CSV, file operations, ETL transformations
- **Web Integration**: HTTP APIs, web scraping
- **Workflow Control**: Scheduling, delays, sub-processes
- **Code Execution**: Python, JavaScript runtime

### 🔌 Direct API Integrations
- **Perplexity**: Real-time web research and search
- **Xero**: Financial accounting and business data  
- **Notion**: Workspace and knowledge management
- **Google Workspace**: Gmail, Calendar, Sheets, Drive
- **Slack**: Team messaging and notifications

> **🎯 Simple Integration**: Braid provides direct API integrations with simple Python imports. No complex setup required - just configure your API keys and start building.

### 🏗️ Agent Patterns
- **ReAct Agents**: Tool-using conversational agents
- **Multi-Step Workflows**: Complex business processes
- **Memory-Enabled**: Persistent conversations
- **RAG-Powered**: Document-aware agents
- **Multi-Agent Systems**: Orchestrated agent teams

## Real Examples

### Customer Support Agent
```
Requirements: Monitor tickets → Analyze sentiment → Daily Slack reports + Google Sheets trends
Tools: http, transform, slack, gworkspace
Result: Complete automated support intelligence system
```

### Research & Analysis Agent  
```
Requirements: Search topics → Generate insights → Create reports → Share with team
Tools: http, files + Integrations: perplexity, notion
Result: AI-powered research assistant
```

### Data Processing Pipeline
```
Requirements: Fetch API data → Clean & analyze → Generate reports → Notify stakeholders
Tools: http, transform, csv, files, slack
Result: Automated data intelligence pipeline
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
pip install -e .
```

### Start Building
1. **Ask Claude Code to prepare**: "Please prepare to create a LangGraph agent"
2. **Fill out requirements**: Use [agent-creator-template.md](docs/guides/agent-development/agent-creator-template.md)  
3. **Create your agent**: "Please read my requirements and create the agent"
4. **Enhance & deploy**: Optional Pro Pack and production deployment

## Documentation

**📚 [Complete Documentation Hub](docs/README.md)** - Organized navigation for all guides and references

**🚀 Quick Access**:
- **[Getting Started](docs/getting-started/)** - Quick start and Claude Code integration
- **[Development Guides](docs/guides/)** - Agent development, API integrations, troubleshooting
- **[Tutorials](docs/tutorials/)** - Step-by-step LangGraph learning path
- **[Reference](docs/reference/)** - Tool capabilities and CLI usage

**⭐ Essential for Complex Agents**:
- **[Agent Development Best Practices](docs/guides/agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md)** - Prevents LangSmith tracing issues
- **[Live API Integration Checklist](docs/guides/api-integrations/LIVE_API_INTEGRATION_CHECKLIST.md)** - Pre-development checklist
- **[Production Templates](templates/)** - Battle-tested patterns from real projects

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