# Braid CLI Usage Guide

The Braid CLI provides powerful commands for creating, developing, and deploying LangGraph agents.

## Commands Overview

### `braid new` - Create New Agents

Create new agents with either simple or production-ready structures.

#### Basic Usage
```bash
braid new <agent-name> [OPTIONS]
```

#### Options
- `--tools`, `-t`: Comma-separated list of tools to include
- `--production`, `-p`: Create production-ready structure (recommended)
- `--description`, `-d`: Brief description of the agent's purpose

#### Available Tools
- `gworkspace`: Google Workspace (Gmail, Calendar, Sheets, Drive)
- `slack`: Slack messaging and workspace tools
- `csv`: CSV file processing and analysis
- `files`: File read/write operations and directory management
- `http`: HTTP requests and web scraping
- `transform`: Data transformation and manipulation
- `execution`: Workflow control and automation

## Agent Creation Examples

### Simple Agent (Quick Prototyping)
```bash
# Basic agent for quick testing
braid new my-bot --tools slack,files

# Creates:
my-bot/
├── agent.py
├── requirements.txt
└── tools/
    ├── slack_tools.py
    └── files_tools.py
```

### Production-Ready Agent (Recommended)
```bash
# Professional agent ready for development and deployment
braid new sales-intelligence-agent --production \
  --tools csv,files,http,slack,gworkspace \
  --description "Sales intelligence agent that analyzes data and provides insights"

# Creates complete production structure:
sales-intelligence-agent/
├── README.md                 # Documentation
├── pyproject.toml           # Modern Python packaging
├── Makefile                 # Development commands
├── langgraph.json          # LangGraph Studio integration
├── .env.example            # Environment template
├── LICENSE                 # MIT license
├── src/
│   └── sales_intelligence_agent/
│       ├── __init__.py
│       ├── configuration.py # Settings management
│       ├── graph.py        # Main agent logic
│       ├── prompts.py      # System prompts
│       ├── state.py        # Agent state
│       ├── tools.py        # Tool orchestration
│       ├── utils.py        # Utilities
│       └── [tool_files].py # Individual tools
└── tests/
    ├── unit_tests/         # Unit tests
    └── integration_tests/  # Integration tests
```

## Development Workflow

### Production Agent Development
```bash
# 1. Create production agent
braid new my-agent --production --tools slack,gworkspace --description "Team coordination bot"

# 2. Set up development environment
cd my-agent
pip install -e '.[dev]'
cp .env.example .env

# 3. Add your API keys to .env file
# 4. Verify setup
make test

# 5. Run your agent
python src/my_agent/graph.py

# 6. Development commands
make test              # Run unit tests
make integration_tests # Run integration tests
make lint             # Code quality checks
make format           # Auto-format code
make help             # See all available commands
```

### Simple Agent Development
```bash
# 1. Create simple agent
braid new my-bot --tools slack

# 2. Install dependencies
cd my-bot
pip install -r requirements.txt

# 3. Add API keys to .env file
# 4. Run directly
python agent.py
```

## Packaging for Deployment

### `braid package` - Package for Deployment

Packages agents into production-ready Docker containers (works with both simple and production structures).

```bash
# Run from agent directory
cd my-agent
braid package

# Creates .build/ directory with:
# - Dockerfile
# - docker-compose.yml (in agent root)
# - Complete build context

# Test locally
docker compose up --build
```

## CLI Command Reference

### Global Options
All commands support standard help:
```bash
braid --help
braid new --help
braid package --help
```

### Tool Selection Guide

**For Data Processing:**
- `csv` + `transform` + `files`

**For Communication:**
- `slack` + `gworkspace`

**For Web Integration:**
- `http` + `transform` + `files`

**For Automation:**
- `execution` + `files` + [other tools as needed]

**Complex Workflows:**
- Combine multiple tools based on your needs
- Example: `csv,transform,slack,gworkspace,files,execution` for comprehensive data processing and reporting

## Best Practices

### Choose Production Mode
- Always use `--production` flag for serious development
- Provides proper project structure, testing, and deployment readiness
- Minimal overhead compared to massive long-term benefits

### Tool Selection
- Start with the minimum viable set of tools
- Add more tools as your agent requirements evolve
- Refer to `TOOL_REFERENCE.md` for detailed tool capabilities

### Environment Management
- Always use virtual environments
- Copy and customize `.env.example`
- Never commit secrets to version control

### Development Process
1. Create with `--production` flag
2. Set up development environment
3. Use `make test` early and often
4. Leverage LangGraph Studio for visual debugging
5. Package with `braid package` when ready to deploy

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure you've installed the package: `pip install -e '.[dev]'`
- Check that your Python path is correct

**Missing Dependencies:**
- Run `pip install -r requirements.txt` (simple) or `pip install -e '.[dev]'` (production)

**Tool Import Failures:**
- Verify tool names are correct (see available tools list above)
- Check that all required environment variables are set

**Test Failures:**
- Ensure all API keys are configured in `.env`
- Some integration tests require valid API credentials

### Getting Help
- Use `braid --help` for command reference
- Check `README.md` in generated agents for specific instructions
- Review `TOOL_REFERENCE.md` for tool capabilities
- Use `make help` in production agents for development commands