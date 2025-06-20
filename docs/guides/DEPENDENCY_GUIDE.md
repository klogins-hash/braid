# Braid Dependency Management Guide

## Overview

Braid now uses selective dependency installation to avoid "dependency hell" and ensure reproducible builds. Instead of installing all possible dependencies, you only install what you need for your specific agent.

## Core Dependencies

The base installation includes only essential dependencies:
- `langchain>=0.2.14` - Core LangChain framework
- `langgraph>=0.2.6` - LangGraph for agent graphs
- `python-dotenv>=1.0.1` - Environment variable management
- `click>=8.0.0` - CLI framework
- `toml>=0.10.2` - Configuration parsing
- `requests>=2.25.0` - HTTP requests

## Optional Dependencies

### Integration Dependencies
- `braid[xero]` - Xero financial data integration
- `braid[notion]` - Notion documentation tools  
- `braid[perplexity]` - Perplexity research tools
- `braid[gworkspace]` - Google Workspace (Gmail, Calendar, Sheets)
- `braid[slack]` - Slack messaging tools
- `braid[ms365]` - Microsoft 365 integration

### Agent Type Dependencies
- `braid[financial]` - Financial analysis tools (yfinance, pandas, numpy)
- `braid[research]` - Research tools (tavily-python, langchain-tavily)
- `braid[retrieval]` - RAG and document processing (llama-index, pypdf, vector databases)
- `braid[memory]` - Advanced memory capabilities (langgraph-sdk)

### Complete Agent Bundles
- `braid[complete-financial]` - Financial agent with Xero, Notion, and Perplexity
- `braid[complete-research]` - Research agent with Notion and Perplexity
- `braid[complete-retrieval]` - Retrieval agent with Notion integration

### Development Dependencies
- `braid[dev]` - Development tools (mypy, ruff, pytest)

## Installation Examples

### Basic Agent Creation
```bash
# Create a basic agent (minimal dependencies)
braid new my-agent
cd my-agent
pip install -r requirements.txt

# Or install with selective dependencies
pip install 'braid[research,notion]'
```

### Financial Agent
```bash
# Create financial agent with automatic dependency selection
braid new financial-bot --agent-type financial
cd financial-bot
pip install -e '.[financial,xero,notion]'
```

### Research Agent
```bash
# Create research agent with specific integrations
braid new research-agent --tools perplexity --agent-type research
cd research-agent
pip install -e '.[research,perplexity,notion]'
```

### Production Agent
```bash
# Create production-ready agent with full dependencies
braid new my-prod-agent --production --agent-type financial --tools xero,notion
cd my-prod-agent
pip install -e '.[financial,xero,notion,dev]'
```

## Migration Guide

### From Old pyproject.toml
If you have an existing installation with all dependencies, you can selectively reinstall:

```bash
# Uninstall current braid
pip uninstall braid

# Reinstall with only what you need
pip install 'braid[financial,xero,notion]'  # Example for financial agent
```

### Updating Existing Agents
For existing agent projects, update your `requirements.txt` or use selective installation:

```bash
# Instead of installing everything
pip install -r requirements.txt

# Install selectively based on your agent's needs
pip install 'braid[research,notion,perplexity]'
```

## Reproducible Builds

A `requirements.lock` file is provided for exact version pinning:

```bash
# For exact reproducibility
pip install -r requirements.lock
```

## Benefits

1. **Faster Installation** - Only install what you need
2. **Fewer Conflicts** - Reduced dependency version conflicts  
3. **Cleaner Environments** - No unused packages
4. **Reproducible** - Lock file ensures consistent builds
5. **Selective Updates** - Update only relevant dependencies

## Troubleshooting

### Missing Dependencies
If you get import errors, install the missing integration:
```bash
pip install 'braid[missing-integration]'
```

### Version Conflicts
Use the lock file for exact versions:
```bash
pip install -r requirements.lock
```

### Unknown Agent Type
Check available agent types:
```bash
braid new --help
```

Available types: `financial`, `research`, `retrieval`, `memory`