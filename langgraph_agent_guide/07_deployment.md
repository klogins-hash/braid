# Deploying Your LangGraph Agent

Once you have built and tested your agent, the final step is to deploy it. This guide covers multiple deployment approaches: LangGraph's native deployment tools and Braid's simplified Docker-based deployment for custom agents.

## Method 1: Local Development Server with LangGraph Studio

For local development and testing, the easiest way to deploy your agent is with the `langgraph dev` command. This starts a local server that you can connect to with LangGraph Studio.

### Steps:

1.  **Organize Your Code**: Your agent's code needs to be in a specific structure. Typically, you have a directory (e.g., `my_agent/`) containing:
    *   `graph.py`: The file containing your compiled LangGraph instance (e.g., `graph = builder.compile()`).
    *   `__init__.py`: An empty file to make the directory a Python package.

2.  **Expose the Graph**: In your `graph.py` or a similar file, your compiled graph instance must be exposed.

3.  **Run the Server**: From the parent directory of your agent code, run the following command:

    ```bash
    langgraph dev my_agent/
    ```

    This will start a local server, usually at `http://127.0.0.1:2024`.

4.  **Connect with Studio**: You can then open [LangGraph Studio](https://smith.langchain.com/studio/) and point it to your local server's URL (`http://127.0.0.1:2024`) to interact with your agent.

## Method 2: Self-Hosted Production Deployment with LangGraph CLI

For production, LangGraph provides tools to build a Docker image for your agent, which can then be deployed anywhere Docker is supported.

This method requires a `PostgreSQL` database for persistence and `Redis` for managing the task queue.

### Steps:

1.  **Application Structure**: Your deployment code should be organized in a directory with the following files:
    *   `langgraph.json`: A configuration file that defines your graphs.
    *   A Python file for your graph (e.g., `my_agent.py`): This contains the graph logic.
    *   `requirements.txt`: Specifies the Python dependencies.
    *   `.env`: Contains environment variables (like API keys).
    *   `docker-compose.yml`: (Optional but recommended) to orchestrate the agent, database, and Redis containers.

2.  **Build the Docker Image**: Use the `langgraph build` command to package your application into a Docker image.

    ```bash
    # From within your application directory
    langgraph build -t my-agent-image
    ```

3.  **Run with Docker Compose**: The easiest way to run the full stack (agent, Postgres, Redis) is with Docker Compose. A `docker-compose.yml` file will define the services.

    ```yaml
    # Example docker-compose.yml
    services:
      langgraph-api:
        image: my-agent-image # The image you just built
        ports:
          - "8000:8000"
        env_file: .env
        depends_on:
          - langgraph-postgres
          - langgraph-redis
      langgraph-postgres:
        image: postgres:16
        # ... postgres config ...
      langgraph-redis:
        image: redis:7
        # ... redis config ...
    ```

4.  **Launch**: Run `docker compose up` to start all the services. Your agent is now deployed and accessible via its API.

## Method 3: Braid Agent Deployment (Simplified Docker)

For Braid-built agents with custom tools and simpler deployment needs, use the Braid CLI packaging system.

### Prerequisites

- Docker and Docker Compose installed
- Braid CLI installed (`pip install -e .`)
- Agent source code with required files

### Agent Structure

Your agent directory should contain:
```
agent_name/
├── agent.py              # Main agent code
├── requirements.txt      # Python dependencies
├── tools/               # Custom tools (optional)
│   ├── __init__.py
│   └── *.py
├── credentials/         # API credentials
│   ├── gworkspace_credentials.json
│   ├── gworkspace_token.json
│   └── ms365_credentials.json
└── .env                # Environment variables
```

### Packaging Process

1. Navigate to your agent directory:
   ```bash
   cd path/to/your/agent
   ```

2. Run the package command:
   ```bash
   braid package
   ```

The CLI will:
- Search for tools in multiple locations
- Validate your agent code for common issues
- Create a `.build` directory with Docker configuration
- Generate a `docker-compose.yml` file

### Credential File Naming

**Important**: Use consistent credential file names:

#### Google Workspace
- `gworkspace_credentials.json` - OAuth2 client secrets from Google Console
- `gworkspace_token.json` - Generated after first OAuth flow

#### Microsoft 365
- `ms365_credentials.json` - Application credentials

### Environment Variables

Create a `.env` file with required variables:
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_TOKEN=xoxp-your-user-token

# Google Sheets
PROJECT_SPREADSHEET_ID=your_google_sheets_id

# Other service-specific variables...
```

### Deployment Options

#### Local Interactive Mode
For agents that need user input:
```bash
docker compose run --rm agent
```

#### Background Mode
For autonomous agents:
```bash
docker compose up -d
```

#### Development Mode with Rebuild
```bash
docker compose up --build
```

## Common Issues & Solutions

### 1. Module Import Errors
**Problem**: `ModuleNotFoundError: No module named 'tools'`

**Solution**: 
- Ensure tools directory exists in your agent folder
- Run `braid package` from the correct directory
- Check the packaging output for tools location messages

### 2. LangGraph State Errors
**Problem**: `Invalid input type <class 'dict'>. Must be a PromptValue, str, or list of BaseMessages.`

**Solution**: 
- Change `llm_with_tools.invoke(state)` to `llm_with_tools.invoke(state["messages"])`
- The Braid packaging command will warn you about this issue

### 3. Google Credentials Issues
**Problem**: Permission errors or credential not found

**Solutions**:
- Ensure credential files use correct naming (`gworkspace_*`)
- Complete OAuth flow locally first to generate token file  
- Verify Google Cloud Console API enablement
- Check volume mounts in docker-compose.yml

### 4. Interactive Mode Not Working
**Problem**: `EOFError: EOF when reading a line`

**Solution**: 
- Use `docker compose run --rm agent` instead of `docker compose up`
- Ensure docker-compose.yml has `stdin_open: true` and `tty: true`

## Production Deployment

For production environments:

1. **Use service accounts** instead of OAuth2 for Google services
2. **Store secrets securely** (e.g., Docker secrets, Kubernetes secrets)
3. **Remove debugging output** from Dockerfile
4. **Use multi-stage builds** for smaller images
5. **Implement health checks** and monitoring
6. **Choose the right method**: Use LangGraph CLI for full-stack deployments with databases, Braid packaging for simpler single-container agents

## Troubleshooting

### Debug Container Contents
Add to your Dockerfile temporarily:
```dockerfile
RUN echo "--- Debugging Info ---"
RUN ls -R /app
RUN echo "PYTHONPATH: $PYTHONPATH"
```

### Check Logs
```bash
docker compose logs agent
```

### Access Running Container
```bash
docker exec -it your_agent_container bash
```

## Choosing the Right Deployment Method

- **LangGraph Studio**: Best for development and testing
- **LangGraph CLI**: Best for production API deployments with persistence
- **Braid Packaging**: Best for simple custom agents with tools, interactive agents, or standalone deployments

This comprehensive approach provides scalable and reliable ways to run your LangGraph agents in various environments. 