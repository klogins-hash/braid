# sales_intelligence_agent_v3

Sales intelligence agent with data analysis capabilities

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
python src/sales_intelligence_agent_v3/graph.py
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
sales_intelligence_agent_v3/
├── src/sales_intelligence_agent_v3/          # Main agent code
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