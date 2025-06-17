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

## Workflow: Building Your First Agent with the Braid CLI

Here is the recommended workflow for building a new agent with Braid. This process is designed to be automated by an AI assistant like Cursor, but can also be performed manually.

### Step 1: Scaffold Your Agent with the CLI

The fastest way to start is with the `braid new` command. It creates a new, structured agent project directory with all the necessary boilerplate.

Provide the name of your agent and specify which toolsets it needs using the `--tools` flag.

```bash
# Example: Create an agent that uses Google Workspace and Slack
braid new sales-prep-agent --tools gworkspace,slack

# Example: Create an agent with no pre-built tools for fully custom logic
braid new custom-logic-agent
```

The CLI will create a new folder (`sales-prep-agent/`) containing:
- A placeholder `agent.py` to house your agent's logic.
- A `tools/` directory containing the Python files for the requested tools (`gworkspace_tools.py`, `slack_tools.py`).
- A `requirements.txt` file with all the necessary dependencies for the agent and its tools.

### Step 2: Implement Your Agent's Logic

This is where you (or an AI assistant) bring your agent to life.
1.  Navigate into your new agent's directory: `cd sales-prep-agent`.
2.  Open `agent.py`.
3.  Implement your agent's core logic using LangGraph. You can import the tools from the local `tools/` directory and any helper functions directly from the core Braid library (e.g., `from core.contrib.slack.utils import post_message`).

The `agent-creator-template.md` file is a great resource for planning out your agent's tasks, tools, and rules before you start writing code.

### Step 3: Run and Debug

With the agent code implemented, it's time to test it.

1.  **Install Dependencies:** Run `pip install -r requirements.txt` from within your agent's directory.
2.  **Set Credentials:** Create a `.env` file in your agent's directory and add the necessary API keys.
3.  **Execute the Agent:** Run your agent directly with `python agent.py`.

This iterative "inner loop" of coding in `agent.py` and running it in the terminal is the fastest way to identify and fix issues, test edge cases, and refine your agent's logic.

### Step 4: Deploy and Observe

Once you are satisfied with your agent's performance in local testing, you are ready for the final step.

1.  **LangSmith:** Ensure your agent is configured to connect to LangSmith for full observability. This will allow you to see traces of your agent's tool use and reasoning processes.
2.  **Deploy:** Deploy your agent to your desired environment. Braid agents are standard Python applications and can be containerized with Docker or deployed to any modern cloud platform.
