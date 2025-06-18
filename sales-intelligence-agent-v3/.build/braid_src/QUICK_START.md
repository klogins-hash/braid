# Braid Quick Start Guide

Get up and running with Braid in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- Basic familiarity with command line

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd braid

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Braid
pip install -e .

# Verify installation
braid --help
```

## Create Your First Agent

Choose your path:

### Option A: Production-Ready Agent (Recommended)

```bash
# Create a professional agent with full structure
braid new my-sales-bot --production \
  --tools csv,files,slack,gworkspace \
  --description "Sales data analyzer with team notifications"

# Set up development environment
cd my-sales-bot
pip install -e '.[dev]'
cp .env.example .env
```

**Add your API keys to `.env`:**
```bash
OPENAI_API_KEY=your-openai-key
SLACK_BOT_TOKEN=your-slack-token
# ... other keys as needed
```

**Test and run:**
```bash
make test                                    # Run tests
python src/my_sales_bot/graph.py           # Run your agent
```

### Option B: Simple Agent (Quick Prototyping)

```bash
# Create a lightweight agent for testing
braid new test-bot --tools slack,files

# Set up and run
cd test-bot
pip install -r requirements.txt
# Add API keys to .env file
python agent.py
```

## What You Get

### Production Agent Structure
```
my-sales-bot/
├── README.md              # Complete documentation
├── Makefile              # make test, make lint, etc.
├── pyproject.toml        # Modern Python packaging
├── langgraph.json        # LangGraph Studio integration
├── .env.example          # Environment template
├── src/my_sales_bot/     # Main source code
│   ├── graph.py          # Your agent logic
│   ├── tools.py          # Tool integration
│   └── [tool_files].py   # Individual tools
└── tests/                # Test suite
```

### Development Commands
```bash
make test              # Run unit tests
make lint              # Code quality
make format            # Auto-format
make integration_tests # Integration tests
make help              # See all commands
```

## Next Steps

1. **Customize your agent** - Edit `src/your_agent/graph.py` to define your agent's behavior
2. **Add prompts** - Modify `src/your_agent/prompts.py` to customize system prompts
3. **Configure tools** - Adjust tool settings in `src/your_agent/configuration.py`
4. **Test thoroughly** - Use `make test` frequently during development
5. **Package for deployment** - Use enhanced packaging when ready:
   ```bash
   # Basic packaging
   braid package
   
   # Production-ready with security and monitoring
   braid package --production
   
   # Include Kubernetes support
   braid package --production --platform kubernetes
   ```
6. **Deploy locally** - Test with `docker compose up --build`
7. **Deploy to production** - Follow instructions in generated `DEPLOYMENT.md`

## Common First Tasks

### Connect to Slack
```python
# Your agent can now send messages
from tools.slack_tools import send_slack_message
send_slack_message("#general", "Hello from my agent!")
```

### Process CSV Data
```python
# Analyze data files
from tools.csv_tools import read_csv, analyze_csv
data = read_csv("sales_data.csv")
insights = analyze_csv(data)
```

### Make HTTP Requests
```python
# Fetch data from APIs
from tools.http_tools import http_get
response = http_get("https://api.example.com/data")
```

## Deployment Quick Start

Once your agent is working locally, deploy it:

### 1. Package Your Agent
```bash
# From your agent directory
braid package --production

# This creates:
# - .build/ directory with optimized Dockerfile
# - docker-compose.yml for easy deployment
# - DEPLOYMENT.md with comprehensive instructions
```

### 2. Test Locally
```bash
# Ensure it works in production environment
docker compose up --build

# Check logs
docker compose logs -f agent
```

### 3. Deploy to Production
```bash
# Build for your registry
docker build -t your-registry.com/my-agent:latest .build/

# Push to registry
docker push your-registry.com/my-agent:latest

# Deploy (example for simple VPS)
docker run -d \
  --name my-agent \
  --env-file .env \
  --restart unless-stopped \
  your-registry.com/my-agent:latest
```

### 4. Kubernetes (Optional)
```bash
# Generate K8s manifests
braid package --production --platform kubernetes

# Deploy to cluster
kubectl apply -f k8s/
kubectl get pods -n default
```

## Getting Help

- **CLI Reference**: `braid --help`
- **Tool Documentation**: See `TOOL_REFERENCE.md`
- **Development Guide**: See `CLI_USAGE.md`
- **Agent Examples**: Check the `agents/` directory

## Troubleshooting

**Import errors?** Make sure you installed with `pip install -e '.[dev]'`

**Tool not working?** Check your `.env` file has the required API keys

**Tests failing?** Ensure all environment variables are set correctly

---

🎉 **You're ready to build powerful AI agents with Braid!**

Start with the production template, customize the prompts and logic, and deploy with confidence.