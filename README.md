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

First, clone the repository. It is highly recommended to use a Python virtual environment to manage dependencies.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate it (on macOS/Linux)
source .venv/bin/activate
```

### 2. Install Braid

With your virtual environment active, install the Braid toolkit in editable mode. This will also install the `braid` CLI.

```bash
# Install the core package and CLI
pip install -e .
```

The core library includes pre-built, tested tool integrations for common platforms. The available tools are:
- `gworkspace`: For Google Workspace (Calendar, Gmail, Sheets).
- `slack`: For Slack messaging and channel operations.
- `ms365`: For Microsoft 365 (Outlook, etc.).

### 3. Configure Credentials

Ensure you have the necessary API keys and credentials for the services your agent will use. The `credentials/` directory can be used to store OAuth tokens (like `gworkspace_token.json`). API keys and other secrets should be managed in a `.env` file within your agent's project directory.

## Workflow: The Braid Agent Lifecycle

Here is the recommended workflow for building a new agent with Braid. This process is designed to be a rapid, three-stage lifecycle: from a simple prototype to a professional, deployable application.

### Stage 1: Prototype with `braid new`

The fastest way to start is by scaffolding a simple agent. This is ideal for quickly testing an idea or building a basic automation.

```bash
# Example: Create an agent that uses Google Workspace and Slack
braid new sales-prep-agent --tools gworkspace,slack
```

This command creates a new folder (`sales-prep-agent/`) with a simple structure:
- `agent.py`: A single file to house your agent's logic.
- `tools/`: A directory containing the Python files for the requested tools.
- `requirements.txt`: A file with all necessary dependencies.

At this stage, you can implement your logic in `agent.py` and run it directly with `python agent.py` for a tight, fast debugging loop.

### Stage 2 (Optional): Professionalize with `braid add-pro-pack`

Once you are satisfied with your agent's core logic, you can upgrade it to a professional, production-grade project structure.

Navigate into your agent's directory and run:
```bash
cd sales-prep-agent
braid add-pro-pack
```

This powerful command transforms your project by:
1.  **Creating a `src/` layout:** The standard for robust Python applications.
2.  **Generating `pyproject.toml`:** Migrates your dependencies to the modern standard.
3.  **Adding a Test Suite:** Creates a `tests/` directory and, using AI, generates a set of meaningful unit tests for your agent's specific logic, complete with mocks.
4.  **Creating a `Makefile`:** Provides simple commands like `make install`, `make test`, and `make run`.
5.  **Adding CI/CD:** Generates a `.github/workflows/ci.yml` file to automatically run tests on every push.

After running this, you should install the new dependencies using the Makefile:
```bash
# This uses poetry to install dependencies from pyproject.toml
make install

# Now you can run your AI-generated tests!
make test
```

### Stage 3: Package for Deployment with `braid package`

When you are ready to ship, run the `package` command from your agent's directory. It intelligently handles both simple and "pro" layouts.

```bash
braid package
```

This creates a `.build/` directory containing a production-ready `Dockerfile`, and a `docker-compose.yml` in your agent's root. This self-contained build kit can be deployed to any platform that supports Docker.

To test your production container locally, simply run:
```bash
docker compose up --build
```
