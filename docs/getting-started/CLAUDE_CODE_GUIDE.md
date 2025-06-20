# Claude Code Guide: Braid Agent Development

**🎯 Purpose**: Complete reference for Claude Code sessions to quickly understand this codebase and build sophisticated LangGraph agents.

## 🚀 Quick Start (< 5 minutes)

### 1. Environment Setup
```bash
# From project root (/braid-ink/braid)
source .venv/bin/activate
pip install -e .
braid --help  # Verify installation
```

### 2. Create Your First Agent
```bash
# Production-ready agent (recommended)
braid new my-agent --production \
  --tools slack,gworkspace,files \
  --description "Your agent description"

cd my-agent
pip install -e '.[dev]'
cp .env.example .env
# Add API keys to .env
make test
python src/my_agent/graph.py
```

### 3. Add Direct Integrations
```bash
# Direct integrations provide simple API access to external services
braid new my-agent --production \
  --tools slack,files \
  --integrations notion,perplexity \
  --description "Agent with Notion and Perplexity integration"

# IMPORTANT: For complex agents, ALWAYS read CLAUDE.md first
# It contains the complete direct integration workflow and patterns
```

## 📁 Codebase Architecture

### Core Structure
```
braid/
├── braid/                    # CLI and templates
│   ├── cli/commands/         # CLI commands (new, package)
│   └── templates/            # Agent templates
├── core/                     # Core functionality
│   ├── tools/                # In-house tools (files, http, transform)
│   ├── integrations/         # External services (slack, gworkspace)
│   ├── integrations/         # Direct API integrations (xero, notion, perplexity)
│   ├── memory.py             # Memory management
│   └── rag_resource.py       # RAG capabilities
└── langgraph_agent_guide/    # Comprehensive LangGraph docs
```

### Agent Structure (Production)
```
my-agent/
├── src/my_agent/
│   ├── graph.py              # Main agent logic (START HERE)
│   ├── tools.py              # Tool orchestration
│   ├── prompts.py            # System prompts
│   ├── state.py              # Agent state management
│   └── configuration.py      # Settings
├── tests/                    # Test suite
├── Makefile                  # make test, make lint, etc.
└── pyproject.toml            # Dependencies
```

## 🛠️ Tools & Capabilities

### Available Tools (Use TOOL_REFERENCE.md for details)
- **gworkspace**: Gmail, Calendar, Sheets, Drive
- **slack**: Team messaging, notifications (12 tools)
- **files**: File operations (3 tools)
- **csv**: Data processing (1 tool)
- **transform**: ETL operations (5 tools)
- **http**: API integration, web scraping (2 tools)
- **execution**: Workflow control (3 tools)
- **code**: Python/JS execution (2 tools)

### Direct API Integrations (5 Production-Ready)
- **perplexity**: Real-time web research and search
- **xero**: Financial accounting and business data
- **notion**: Workspace and knowledge management
- **gworkspace**: Gmail, Calendar, Sheets, Drive
- **slack**: Team messaging and notifications

> **🎯 Simple Integration**: Direct API integrations with Python imports. Just configure API keys and start building. See `CLAUDE.md` for integration patterns.

### Common Tool Combinations
```bash
# Data processing
braid new data-agent --tools transform,csv,files,http

# Team automation
braid new team-bot --tools slack,gworkspace,files

# Complex workflows
braid new workflow-agent --tools execution,code,http,files,transform
```

**📋 For detailed tool selection**: See [TOOL_SELECTION_GUIDE.md](./TOOL_SELECTION_GUIDE.md) for comprehensive decision trees and workflow patterns.

## 🏗️ Agent Development Patterns

### 1. Simple ReAct Agent (Start Here)
```python
# graph.py - Basic agent pattern
from langgraph.graph import StateGraph
from .state import AgentState

def create_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    return workflow.compile()
```

### 2. Multi-Step Complex Agent
```python
# For complex workflows with multiple processing steps
workflow = StateGraph(AgentState)
workflow.add_node("initialize", initialize_task)
workflow.add_node("process_data", process_data)
workflow.add_node("generate_insights", generate_insights)
workflow.add_node("notify_team", notify_team)
# Add conditional routing between steps
```

### 3. Memory-Enabled Agent
```python
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Use with thread_id for persistent conversations
config = {"configurable": {"thread_id": "user_123"}}
result = graph.invoke(input, config=config)
```

### 4. RAG-Enabled Agent
```python
from core.rag_resource import create_rag_tool_from_directory

# Add document search capability
rag_tool = create_rag_tool_from_directory(
    directory_path="data/documents/",
    name="DocumentSearch",
    description="Search user documents for information"
)
tools.append(rag_tool)
```

## 🔧 Development Workflow

### 1. Agent Creation
```bash
# Use production template with specific tools
braid new my-agent --production --tools [tools] --description "Description"

# With direct integrations for external services
braid new my-agent --production --tools [tools] --integrations [integrations] --description "Description"
```

### 2. Core Development Files
1. **src/my_agent/graph.py** - Main agent logic (edit this first)
2. **src/my_agent/prompts.py** - System prompts and instructions
3. **src/my_agent/tools.py** - Tool orchestration and configuration
4. **src/my_agent/state.py** - Agent state schema (for complex agents)

### 3. Development Commands
```bash
make test                     # Run tests
make lint                     # Code quality
make format                   # Auto-format
python src/my_agent/graph.py  # Run agent
```

### 4. Packaging & Deployment
```bash
# Basic packaging
braid package

# Production with security and monitoring
braid package --production

# Deploy locally
docker compose up --build
```

## 💡 Common Agent Scenarios

### Scenario 1: Data Processing Agent
```bash
braid new data-processor --production \
  --tools transform,csv,files,http \
  --description "Process CSV data and generate reports"
```
**Pattern**: Fetch → Transform → Analyze → Output

### Scenario 2: Team Communication Agent
```bash
braid new team-assistant --production \
  --tools slack,gworkspace,files \
  --integrations notion \
  --description "Team coordination with Slack and Google Workspace"
```
**Pattern**: Monitor → Process → Notify → Archive

### Scenario 3: Research & Analysis Agent
```bash
braid new research-agent --production \
  --tools http,transform,files \
  --integrations perplexity \
  --description "Research topics and generate analysis reports"
```
**Pattern**: Search → Analyze → Synthesize → Report

### Scenario 4: Workflow Automation Agent
```bash
braid new workflow-agent --production \
  --tools execution,code,http,files,slack \
  --description "Complex workflow automation with notifications"
```
**Pattern**: Schedule → Execute → Monitor → Notify

## 🐛 Debugging & Troubleshooting

### Common Issues & Solutions

1. **Import Errors**
   ```bash
   pip install -e '.[dev]'  # From agent directory
   ```

2. **Tool Not Working**
   - Check .env file has required API keys
   - Verify tool is included in --tools list

3. **Agent Not Responding**
   - Check system prompt in prompts.py
   - Add logging to see agent's decision process
   - Use LangSmith for detailed tracing

4. **Integration Issues**
   - Verify API keys in .env file
   - Test direct API calls with `.invoke()` method

### Debugging Tools
```python
# Add to agent code for debugging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In agent nodes
logger.info(f"Agent state: {state}")
logger.info(f"Tool inputs: {tool_inputs}")
```

## 🚢 Deployment Patterns

### Local Development
```bash
python src/my_agent/graph.py  # Direct execution
```

### Docker Deployment
```bash
braid package --production
docker compose up --build
```

### Production Deployment
```bash
braid package --production --platform kubernetes
kubectl apply -f k8s/
```

## 📖 Deep Dive References

**Essential References**:
- **[TOOL_SELECTION_GUIDE.md](./TOOL_SELECTION_GUIDE.md)** - Detailed decision trees for optimal tool combinations
- **[TOOL_REFERENCE.md](./TOOL_REFERENCE.md)** - Complete tool capabilities and examples
- **[agent-creator-template.md](./agent-creator-template.md)** - Requirements gathering template

**Advanced Topics**:
- **`core/integrations/`** - Direct API integration examples and patterns
- **`langgraph_agent_guide/`** - Comprehensive LangGraph concepts (15 detailed guides)
- **[CLI_USAGE.md](./CLI_USAGE.md)** - Complete CLI command reference

## 🎯 Success Patterns

### 1. Start Simple
- Begin with basic ReAct agent
- Add complexity incrementally
- Use production template from start

### 2. Tool Selection Strategy
1. Read requirements carefully
2. Consult TOOL_REFERENCE.md
3. Start with minimum viable set
4. Add tools as needed

### 3. Prompt Engineering
- Be specific in system prompts
- Include examples for complex tasks
- Test with edge cases early

### 4. Testing Strategy
- Use `make test` frequently
- Add integration tests for critical paths
- Test with real API credentials

## 🏁 Next Steps for Complex Agents

1. **Multi-Agent Systems**: Use supervisor patterns from langgraph_agent_guide/
2. **Memory Integration**: Combine persistent memory with RAG
3. **Integration Orchestration**: Combine multiple direct integrations for comprehensive capabilities
4. **Performance Optimization**: Use deployment profiles for production scaling

---

**🤖 For Claude Code**: This guide provides everything needed to understand the codebase and build sophisticated agents. Start with the Quick Start section, then dive into specific patterns based on requirements.