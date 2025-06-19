# Braid - Agent Builder

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Braid is a toolkit designed for agentic coding tools (E.g. Cursor, Claude Code) to accelerate the creation, debugging, and deployment of sophisticated LangGraph agents. It bridges the gap between no-code platforms and from-scratch coding, providing a structured yet fully customizable environment for building powerful AI agents.

The purpose of this tool is to address the limitations of existing agent-building solutions:
1.  **Beyond No-Code:** While no-code tools are accessible, they are often slow, have limited observability and human-in-the-loop capabiltiies, require significant human oversight, will become increasingly suboptimal compared to increasingly advanced LLMs, and lack flexibility needed for complex integrations. Braid empowers developers to build more advanced agents by leveraging AI coding tools (E.g. Claude Code, Cursor)  enabling features like voice-to-text creation and dynamic debugging.
2.  **Simplified Configuration:** We automate the tedious manual API configuration required for advanced agent flows, saving coding agents time and applying more energy on agent architecture, prompt design, and evaluation.
3.  **Rapid Iteration:** Braid is built for speed. It provides a tight feedback loop for testing, autonomous fixing, and benchmarking. Direct terminal access and pre-built LangSmith traceability allow for efficient debugging and resolution of errors.
4.  **Resource Efficiency:** By providing foundational components like memory stores and core tool integrations out-of-the-box, Braid lets you focus your resources on what matters: agent logic, prompt design, and tool selection.
5.  **Reliable Integrations:** We provide pre-defined, tested integrations for common tools like Slack, minimizing the "first-time-use" issues that often plague new agent setups.

## Why Braid?

| Dimension | Vertical Tools (SaaS Software) | No-code flow tools (n8n, Zapier) | Braid Agent Builder |
| :--- | :--- | :--- | :--- |
| **Time-to-first-response**| Minutes*, but only for that domain | Minutes if a connector exists | Minutes for any domain |
| **Code ownership** | Little / none | None (flows are JSON) | 100 % – pure Python in repo |
| **Custom logic** | Hard / unavailable | Limited to JS snippets | Full Python; edit scaffold |
| **Data residency** | Vendor cloud | Vendor cloud | Self-host or VPC |
| **Headless invocation** | Rare | Webhooks, but no memory | Native; expose as Tool or API |
| **Memory flexibility** | Fixed | Simple key/value | Vector, RAG, checkpoints |
| **Cost** | Subscription per seat / tenant | Subscription + task fees | Only infra + LLM usage |


## Foundation Structure

Braid provides a solid foundation for your agents, including:

-   **Agent Logic:** A clear structure for defining your agent's core behavior.
-   **Memory Store:** Support for various memory backends (Postgres, RAG, SQL).
-   **Chat Interface:** Pre-built integrations for Slack and Microsoft Teams.
-   **Core Tools:** Ready-to-use tools for Google Workspace and Microsoft 365.
-   **Custom APIs:** A simple process for integrating your own tools and APIs.

## Getting Started

### 1. Setup Your Environment

First, clone the repository and set up a Python virtual environment.

```bash
# Clone and navigate to the repository
git clone <repository-url>
cd braid

# Create a virtual environment
python3 -m venv .venv

# Activate it (on macOS/Linux)
source .venv/bin/activate
```

### 2. Install Braid

Install the Braid toolkit with the CLI:

```bash
# Install the core package and CLI
pip install -e .
```

### 3. Verify Installation

Check that the CLI is working:

```bash
braid --help
```

### 4. Available Tools

Braid includes pre-built, tested tool integrations:

| Tool | Purpose | Use Cases |
|------|---------|-----------|
| `gworkspace` | Google Workspace integration | Gmail, Calendar, Sheets, Drive automation |
| `slack` | Slack messaging and workspace | Team communication, notifications, bot interactions |
| `csv` | CSV file processing | Data analysis, reporting, file manipulation |
| `files` | File operations | Read/write files, directory management |
| `http` | Web requests and scraping | API integration, data fetching, web automation |
| `transform` | Data transformation | Data cleaning, formatting, analysis |
| `execution` | Workflow control | Scheduling, automation, process management |

### 5. Create Your First Agent

Get started with a production-ready agent:

```bash
# Create a comprehensive agent
braid new my-first-agent --production \
  --tools csv,files,slack \
  --description "Data processing agent with Slack notifications"

cd my-first-agent
pip install -e '.[dev]'
cp .env.example .env
# Add your API keys to .env
make test
python src/my_first_agent/graph.py
```

**📖 For detailed CLI usage, see [CLI_USAGE.md](CLI_USAGE.md)**  
**🚀 New to Braid? Start with [QUICK_START.md](QUICK_START.md)**

## Workflow: The Braid Agent Lifecycle

Braid offers two pathways for building agents: **rapid prototyping** or **production-ready development**. Choose the approach that best fits your needs.

### Quick Start: Simple Agents

For rapid prototyping and simple automations:

```bash
# Example: Create a basic agent for quick testing
braid new sales-prep-agent --tools gworkspace,slack
```

This creates a lightweight structure with:
- `agent.py`: Single file for your agent logic
- `tools/`: Tool implementations  
- `requirements.txt`: Dependencies

Perfect for fast iteration: `python agent.py` to test immediately.

### Recommended: Production-Ready Agents

For professional development and deployment-ready agents:

```bash
# Example: Create a production-ready agent
braid new sales-intelligence-agent --production --tools csv,files,http,slack,gworkspace --description "Sales intelligence agent that analyzes data and provides insights"
```

This creates a complete production structure:

```
sales-intelligence-agent/
├── README.md                  # Complete documentation
├── pyproject.toml            # Modern Python packaging
├── Makefile                  # Development commands
├── langgraph.json           # LangGraph Studio integration
├── .env.example             # Environment configuration
├── LICENSE                  # MIT license
├── src/
│   └── sales_intelligence_agent/
│       ├── __init__.py
│       ├── configuration.py  # Agent configuration
│       ├── graph.py         # Main LangGraph definition  
│       ├── prompts.py       # System prompts
│       ├── state.py         # Agent state management
│       ├── tools.py         # Tool orchestration
│       ├── utils.py         # Utility functions
│       └── [tool_files].py  # Individual tool implementations
└── tests/
    ├── unit_tests/          # Unit test suite
    └── integration_tests/   # Integration test suite
```

**Get started immediately:**
```bash
cd sales-intelligence-agent
pip install -e '.[dev]'
cp .env.example .env          # Add your API keys
make test                     # Verify everything works
python src/sales_intelligence_agent/graph.py  # Run your agent
```

**Development commands:**
```bash
make test                     # Run unit tests
make integration_tests        # Run integration tests  
make lint                     # Code quality checks
make format                   # Auto-format code
```

### Stage 2: Package for Deployment

When ready to deploy, package your agent with enhanced production features:

```bash
# Basic packaging (works with both simple and production structures)
braid package

# Production-optimized packaging with security and monitoring
braid package --production

# Include Kubernetes manifests for container orchestration
braid package --production --platform kubernetes
```

**What you get:**
- Multi-stage Docker builds for optimized images
- Security-hardened containers (non-root user, health checks)
- Production `docker-compose.yml` with monitoring setup
- Comprehensive deployment documentation (`DEPLOYMENT.md`)
- Optional Kubernetes manifests for scalable deployment

**Test locally:**
```bash
docker compose up --build
```

**Deploy to production:**
```bash
# Build and push to registry
docker build -t your-registry.com/agent:latest .build/
docker push your-registry.com/agent:latest

# Deploy with Kubernetes (if using K8s option)
kubectl apply -f k8s/
```
