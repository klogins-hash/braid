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

## 💬 **Real Examples**

### **Customer Support Intelligence Agent**
```
User: "I need an agent that monitors customer support tickets, analyzes sentiment, 
      and posts daily summaries to Slack with trend data in Google Sheets."

Claude Code: [Reviews docs] → [Creates agent with HTTP tools, sentiment analysis, 
             Slack integration, Google Sheets automation] → [Production ready]
```

### **Financial Forecasting Agent**
```
User: "I need an agent that pulls Xero financial data, does market research, 
      creates 5-year forecasts, and generates professional reports in Notion."

Claude Code: [Reviews docs] → [Creates agent with Xero integration, Perplexity research, 
             financial modeling, Notion reporting] → [Production ready]
```

### **Research & Analysis Agent**
```
User: "I need an agent that researches topics using web search, analyzes the data, 
      creates comprehensive reports, and shares findings with my team."

Claude Code: [Reviews docs] → [Creates agent with Perplexity integration, data analysis, 
             report generation, team sharing] → [Production ready]
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.11+ installed
- Access to Claude Code
- API keys for desired services (OpenAI, Slack, etc.)

### **Setup (30 seconds)**
```bash
git clone <repository-url>
cd braid
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### **Build Your First Agent**
1. **Tell Claude Code to prepare:**
   ```
   "Please prepare to create a LangGraph agent by reviewing the docs and examples"
   ```

2. **Describe what you want:**
   ```
   "I need an agent that [your specific requirements]"
   ```
   
   Be specific about:
   - What the agent should do
   - Which systems it should integrate with
   - What outputs you need
   - Any specific workflows

3. **Add enterprise features** (optional):
   ```
   "Optional Pro Pack and production deployment"
   ```

## 🛠️ **What's Available**

### **Core Integrations**
| Service | Capabilities | Use Cases |
|---------|-------------|-----------|
| **🔍 Perplexity** | Real-time web research | Market analysis, trend research, competitive intelligence |
| **💰 Xero** | Financial & accounting data | Revenue forecasting, expense analysis, financial reporting |
| **📄 Notion** | Document & workspace management | Report generation, knowledge management, documentation |
| **📧 Google Workspace** | Gmail, Calendar, Sheets, Drive | Email automation, scheduling, data management |
| **💬 Slack** | Team messaging & notifications | Alerts, team updates, workflow notifications |

### **40+ Built-in Tools**
- **Data Processing**: CSV handling, file operations, data transformations
- **Web Integration**: HTTP APIs, web scraping, data fetching  
- **Workflow Control**: Scheduling, delays, conditional logic
- **Communication**: Email sending, message posting, file sharing
- **Analysis**: Data aggregation, reporting, insights generation

### **Agent Patterns**
- **🔄 ReAct Agents**: Reasoning and action cycles
- **📋 Multi-Step Workflows**: Complex business processes
- **🧠 Memory-Enabled**: Conversation history and context
- **📚 RAG-Powered**: Document search and retrieval
- **🤝 Multi-Agent**: Coordinated agent teams

## 🆚 **Why Choose Braid?**

### **Traditional AI Development**
- ❌ Weeks learning LangGraph concepts
- ❌ Hours setting up project structure  
- ❌ Days configuring integrations
- ❌ Complex deployment processes
- ❌ Manual testing and debugging

### **Braid + Claude Code**
- ✅ **Minutes** to production-ready agents
- ✅ **Natural language** requirements
- ✅ **Built-in** integrations and tools
- ✅ **Automatic** testing and deployment
- ✅ **Enterprise-grade** from day one

## 🏢 **Enterprise Ready**

**Security & Compliance**
- Non-root containers, secret management, network isolation
- Audit logging, access controls, data encryption

**Monitoring & Observability**  
- Health checks, metrics collection, error tracking
- LangSmith integration, detailed tracing, performance monitoring

**Scalability & Reliability**
- Kubernetes support, auto-scaling, resource optimization
- Circuit breakers, retry logic, graceful degradation

## 📚 **Need Help?**

- **📖 [Complete Documentation](docs/README.md)** - Comprehensive guides and references
- **🎓 [Tutorials](docs/tutorials/)** - Step-by-step learning paths
- **⚡ [Quick Reference](docs/reference/AGENT_DEVELOPMENT_COMMANDS.md)** - Essential commands

---

## 🚀 **Ready to Start?**

**No complex setup. No templates. No learning curve.**

Just tell Claude Code what you want:

```
"Please prepare to create a LangGraph agent by reviewing the docs and examples"
```

Then describe your agent and watch it come to life. **It's that simple.**