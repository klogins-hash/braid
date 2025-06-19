# financial_forecast_agent

Financial forecasting agent that integrates Xero data with market research to generate comprehensive forecasts

## Getting Started

1. Create a `.env` file:

```bash
cp .env.example .env
```

2. Add your API keys to the `.env` file:

```
OPENAI_API_KEY=your-api-key-here
# Add other required API keys based on your tools
```

3. Install dependencies:

```bash
pip install -e .
# Or for development:
pip install -e ".[dev]"
```

4. Run the agent:

```bash
python src/financial_forecast_agent/graph.py
```

## Development

### Running Tests

```bash
# Run unit tests
make test

# Run integration tests  
make integration_tests

# Run tests in watch mode
make test_watch
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint
```

### LangGraph Studio

This project is configured for [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio). Open this directory in LangGraph Studio to visually edit and debug your agent.

## Project Structure

```
financial_forecast_agent/
├── src/financial_forecast_agent/          # Main agent code
│   ├── __init__.py
│   ├── configuration.py       # Agent configuration
│   ├── graph.py              # Main graph definition
│   ├── prompts.py            # System prompts
│   ├── state.py              # Agent state definition
│   ├── tools.py              # Tool definitions
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
│   ├── integration_tests/    # Integration tests
│   └── unit_tests/          # Unit tests
├── pyproject.toml           # Project configuration
├── langgraph.json           # LangGraph Studio config
├── Makefile                 # Development commands
└── README.md               # This file
```

## Built with Braid

This agent was generated using [Braid](https://github.com/braid-ink/braid), a toolkit for creating production-ready LangGraph agents.

## MCP Integration

This agent uses the following Model Context Protocol (MCP) servers:

- **Notion MCP Server**: Connect to Notion workspaces for reading, creating, and updating pages and databases
- **Perplexity MCP Server**: Real-time web search and research capabilities using Perplexity's Sonar API for live information retrieval

MCPs extend your agent's capabilities with external services. They run as separate processes and communicate via the Model Context Protocol.

### MCP Setup

1. Configure environment variables in `.env` file
2. MCPs are automatically dockerized during packaging (`braid package --production`)
3. Use `docker compose up --build` to run with MCP services

See `mcp/` directory for individual MCP configurations.
