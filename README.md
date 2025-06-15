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

### 1. Installation

First, clone the repository. Then, install the necessary dependencies.

**Core Dependencies:**

To get the essential packages for the agent builder to run, execute the following command in your terminal:

```bash
pip install -e .
```

This will install the packages listed under `dependencies` in the `pyproject.toml` file.

**Extended Dependencies (Tool-specific):**

For agents that require specific integrations like Google Workspace, Slack, or Microsoft 365, you can install the necessary optional dependencies.

```bash
# Install all optional dependencies
pip install -e .[gworkspace,slack,ms365]

# Or install them individually (recommended)
pip install -e .[gworkspace]
pip install -e .[slack]
pip install -e .[ms365]
```

### 2. Configuration

Ensure you have the necessary API keys and credentials for the services your agent will use. Place them in a `.env` file at the root of the project or manage them via your preferred secrets management tool. The `credentials/` directory can be used to store OAuth tokens.


## Workflow: Creating Your Agent

Here is the recommended workflow for building a new agent with Braid.

### Step 1: Define Your Agent's Task

Open the `agent-creator-template.md` file. In this file, clearly describe what you want your agent to do. Be specific about the tasks, tools, and any rules the agent must follow.

-   **Core Tasks and Sequences:** What is the primary goal? (e.g., *For every upcoming sales meeting on my Google Calendar, search the prospect in Perplexity and return a concise summary in the #sales-prep Slack channel.*)
-   **Tools:** What tools will it need? (e.g., *Slack, Salesforce, Google Calendar, Perplexity*)
-   **Rules:** What are the safety constraints? (e.g., *Before sending POST, PUT, or PATCH requests, confirm the request body and parameters with me.*)

### Step 2: Build the Agent with an AI Assistant

Now, you will use an AI coding assistant (like Claude in your IDE or a custom script) to generate the agent's scaffold.

Provide the following prompt to the assistant:

> 1.  We are preparing a LangGraph agent. Please review the `langgraph_agent_guide` directory to understand how to do this.
> 2.  When you have reviewed the guide, use the filled-out `agent-creator-template.md` to prepare the agent's code.

The assistant will use the guide's best practices and your specifications to generate the Python code for your agent.

### Step 3: Execute and Debug

With the agent code generated, it's time to test it. Use the terminal in your IDE to execute the agent script.

This iterative "inner loop" of running and debugging in the terminal is the fastest way to identify and fix issues, test edge cases, and refine your agent's logic. This provides a level of pre-LangSmith traceability that is invaluable for hardening your agent.

### Step 4: Deploy and Observe

Once you are satisfied with your agent's performance in local testing, you are ready for the final step.

1.  **LangSmith:** Ensure your agent is configured to connect to LangSmith for full observability. This will allow you to see traces of your agent's tool use and reasoning processes.
2.  **Deploy:** Deploy your agent to your desired environment.
