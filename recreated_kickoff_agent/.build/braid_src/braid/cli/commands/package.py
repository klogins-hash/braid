import click
import os
import shutil

# --- Dockerfile Template ---
# This template defines a multi-stage Docker build.
# Stage 1: Builds and installs the Braid toolkit from the local source.
# Stage 2: Creates a clean final image, copying the installed toolkit and the agent's code.
DOCKERFILE_TEMPLATE = """
# Stage 1: Build the braid library
FROM python:3.11-slim as builder

WORKDIR /app

# Copy the entire braid library source
COPY ./braid_src /app/braid_src

# Install the braid library from the local source
RUN pip install --no-cache-dir ./braid_src

# Stage 2: Final application image
FROM python:3.11-slim

WORKDIR /app

# Copy the installed braid library from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy the agent's requirements and code
COPY ./agent_code/requirements.txt .
COPY ./agent_code/ .

# Install the agent's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add the app directory to the python path to allow local imports
ENV PYTHONPATH="/app"

# Debugging steps to verify container state
RUN echo "--- Debugging Info ---"
RUN echo "Listing contents of /app:" && ls -R /app
RUN echo "PYTHONPATH is set to: $PYTHONPATH"
RUN echo "--- End Debugging Info ---"

# Command to run the agent
CMD ["python", "agent.py"]
"""

# --- Docker Compose Template ---
DOCKER_COMPOSE_TEMPLATE = """
services:
  agent:
    build:
      context: ./.build
      dockerfile: Dockerfile
    env_file:
      - .env
    volumes:
      - ./credentials:/app/credentials
    # Uncomment the following lines if your agent needs to be interactive
    # stdin_open: true
    # tty: true
"""

@click.command()
def package_command():
    """
    Packages the agent into a deployable build kit.
    This command should be run from the root of an agent's directory.
    """
    agent_root = os.getcwd()
    build_dir = os.path.join(agent_root, ".build")
    
    # --- Pre-flight Checks ---
    if not os.path.exists(os.path.join(agent_root, "agent.py")):
        click.echo("Error: 'agent.py' not found. This command must be run from an agent's root directory.", err=True)
        return

    # --- Setup Build Directory ---
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    agent_code_dir = os.path.join(build_dir, "agent_code")
    os.makedirs(agent_code_dir)
    
    braid_src_dir = os.path.join(build_dir, "braid_src")
    
    try:
        click.echo("🚀 Starting agent packaging process...")
        
        # --- 1. Copy Agent Code ---
        click.echo("   - Copying agent source code...")
        shutil.copy2(os.path.join(agent_root, "agent.py"), agent_code_dir)
        shutil.copy2(os.path.join(agent_root, "requirements.txt"), agent_code_dir)
        
        # Look for tools directory in both current location and agents subdirectory
        tools_paths = [
            os.path.join(agent_root, "tools"),
            os.path.join(agent_root, "..", "agents", os.path.basename(agent_root), "tools")
        ]
        
        tools_copied = False
        for tools_path in tools_paths:
            if os.path.exists(tools_path):
                shutil.copytree(tools_path, os.path.join(agent_code_dir, "tools"))
                tools_copied = True
                break
        
        if not tools_copied:
            click.echo("   Warning: No tools directory found - agent may not have custom tools")
            
        # --- 2. Copy Braid Library Source ---
        click.echo("   - Copying Braid toolkit source...")
        # Find the root of the braid project (where pyproject.toml is)
        braid_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        shutil.copytree(braid_project_root, braid_src_dir, ignore=shutil.ignore_patterns('.git', '.venv', '.build', 'agents', '*.egg-info'))

        # --- 3. Generate Dockerfile ---
        click.echo("   - Generating Dockerfile...")
        with open(os.path.join(build_dir, "Dockerfile"), "w") as f:
            f.write(DOCKERFILE_TEMPLATE)
            
        # --- 4. Generate docker-compose.yml ---
        click.echo("   - Generating docker-compose.yml...")
        with open(os.path.join(agent_root, "docker-compose.yml"), "w") as f:
            f.write(DOCKER_COMPOSE_TEMPLATE)
            
        click.echo("\n✅ Packaging complete!")
        click.echo("   A '.build' directory has been created with a Dockerfile.")
        click.echo("   A 'docker-compose.yml' file has been created in your agent's root.")
        click.echo("\n   To build and run your agent locally, use:")
        click.echo("   docker compose up --build")
        
    except Exception as e:
        click.echo(f"\nAn error occurred during packaging: {e}", err=True)
        # Clean up failed build
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir) 