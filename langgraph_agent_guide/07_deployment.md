# Deploying Your LangGraph Agent

Once you have built and tested your agent, the final step is to deploy it. LangGraph provides tools for both local testing and production-grade, self-hosted deployments.

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

## Method 2: Self-Hosted Production Deployment with Docker

For production, you need a more robust and scalable solution. The `langgraph-cli` provides tools to build a Docker image for your agent, which can then be deployed anywhere Docker is supported.

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

This self-hosted approach provides a scalable and reliable way to run your LangGraph agents in a production environment. 