# Introduction to Building Agents with LangGraph

This guide provides a comprehensive, synthesized overview of how to build powerful and reliable agents using LangGraph. It is designed to be a direct, practical resource for developers and AI agents to quickly understand the core concepts and best practices for creating LangGraph applications.

## What is LangGraph?

LangGraph is a library for building stateful, multi-actor applications with LLMs. It extends the LangChain Expression Language (LCEL) with the ability to coordinate multiple chains (or actors) across many steps of computation in a cyclical, graph-based manner.

The core philosophy of LangGraph is to provide developers with maximum control and precision in their agent workflows, which is essential for building production-ready systems.

## Why this Guide?

This guide distills the key learnings from the LangChain Academy's "Intro to LangGraph" course into a set of concise, easy-to-digest documents and code examples. While the original course uses Jupyter notebooks, this guide uses Markdown and standalone Python scripts, making the content more accessible for automated systems and future AI-driven development.

## Structure

The guide is structured as follows:

-   **01_core_concepts.md**: The fundamental building blocks: State, Nodes, Edges, and Graph construction.
-   **02_building_an_agent.md**: Building a basic agent with tools and routing (the ReAct pattern).
-   **03_adding_memory.md**: Making your agent conversational with memory and persistence.
-   **04_advanced_state_management.md**: Techniques for managing complex state.
-   **05_advanced_graph_patterns.md**: Modularizing your graph and running steps in parallel.
-   **06_debugging_and_control.md**: Debugging, interrupting, and human-in-the-loop workflows.
-   **07_deployment.md**: Deploying your LangGraph agent.
-   **08_production_best_practices.md**: A guide to observability, evaluation, and robustness with LangSmith.
-   **09_advanced_agent_architectures.md**: Design patterns for building complex, multi-step agents.
-   **10_environment_and_secrets.md**: Best practices for loading secrets and running your agent.
-   **11_agent_development_playbook.md**: The complete, step-by-step process for building robust agents.
-   **12_core_memory_components.md**: A guide to the persistent memory system.
-   **13_rag_with_llamaindex.md**: How to build agents that can reason over user-uploaded documents.
-   **14_core_tool_toolkit.md**: A guide to the core tool toolkit.
-   **code_examples/**: Runnable Python scripts for key concepts.

## Choosing Your Path: Templates vs. Building From Scratch

Before diving in, it's important to decide on your development path. This repository offers two primary modes of working:

1.  **Using Templates**: For common use cases, we provide pre-built templates in the `/templates` directory. This is the fastest way to get started.
2.  **Building From Scratch**: For unique or complex agents, this guide provides the first principles to build any agent architecture you can imagine.

### When to Use a Template

Using a template is **highly recommended** when you are:

-   **New to LangGraph**: Templates handle the boilerplate setup, allowing you to focus on the core logic of your agent.
-   **Building a Standard Agent**: If your agent fits a common pattern, a template is the most efficient starting point.
-   **Prototyping Quickly**: Get a working agent up and running in minutes.

Our available templates cover the following use cases:

-   `react-agent`: A general-purpose agent that can reason and act using tools. **Start here** if you're not sure which to choose.
-   `memory-agent`: An agent that can remember past conversations.
-   `retrieval-agent-template`: An agent that can retrieve information from a knowledge base to answer questions.
-   `data-enrichment`: A pipeline for processing and enriching data.
-   `new-langgraph-project`: A barebones project structure with dependencies, for when you want to build the graph logic yourself but don't want to set up the project from scratch.

You can also **combine templates**. For example, you can start with the `react-agent` and then integrate the memory components from the `memory-agent` by reviewing its `state.py` and `graph.py` files.

### When to Build From Scratch

Building from scratch is the right choice when:

-   **Your Agent has Custom Needs**: If your agent requires a complex, non-linear flow, multiple LLM nodes, or dynamic routing logic that doesn't fit a standard ReAct loop, building from scratch gives you maximum control.
-   **You Want to Master LangGraph**: The best way to deeply understand the mechanics of LangGraph is to build an agent from its fundamental components, as detailed in this guide.
-   **You are extending a template** with functionality not included in any other template.

**Our Recommendation:** Start with a template if possible. When you hit the limits of what the template provides, use this guide to extend it or to build a new, custom agent from the ground up.

## The Guide's Structure

The rest of this guide is structured to take you from core concepts to production-ready agents, whether you are customizing a template or starting from a blank file.

By the end of this guide, you will have a solid foundation for building, debugging, and deploying sophisticated agents with LangGraph.