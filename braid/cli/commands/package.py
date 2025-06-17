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
    It supports both simple and 'pro-pack' (src-based) layouts.
    """
    agent_root = os.getcwd()
    agent_name = os.path.basename(agent_root).replace("-", "_")
    build_dir = os.path.join(agent_root, ".build")
    
    # --- Pre-flight Checks & Layout Detection ---
    is_pro_layout = os.path.exists(os.path.join(agent_root, "src"))
    
    if is_pro_layout:
        click.echo("   - Detected 'pro-pack' layout (src-based).")
        agent_code_src_dir = os.path.join(agent_root, "src", agent_name)
    else:
        click.echo("   - Detected simple layout.")
        agent_code_src_dir = agent_root

    if not os.path.exists(os.path.join(agent_code_src_dir, "agent.py")):
        click.echo(f"Error: 'agent.py' not found in '{agent_code_src_dir}'.", err=True)
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
        if is_pro_layout:
            # For pro layout, copy the whole src directory
            shutil.copytree(os.path.join(agent_root, "src"), os.path.join(agent_code_dir, "src"))
            # We also need the pyproject.toml to install dependencies
            shutil.copy2(os.path.join(agent_root, "pyproject.toml"), agent_code_dir)
            shutil.copy2(os.path.join(agent_root, "poetry.lock"), agent_code_dir)
        else:
            # For simple layout, copy individual files
            shutil.copy2(os.path.join(agent_root, "agent.py"), agent_code_dir)
            shutil.copy2(os.path.join(agent_root, "requirements.txt"), agent_code_dir)
            if os.path.exists(os.path.join(agent_root, "tools")):
                shutil.copytree(os.path.join(agent_root, "tools"), os.path.join(agent_code_dir, "tools"))
        
        # --- 2. Copy Braid Library Source ---
        click.echo("   - Copying Braid toolkit source...")
        # Find the root of the braid project (where pyproject.toml is)
        braid_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        shutil.copytree(braid_project_root, braid_src_dir, ignore=shutil.ignore_patterns('.git', '.venv', '.build', 'agents', '*.egg-info'))

        # --- 3. Generate Dockerfile ---
        dockerfile_content = generate_dockerfile(is_pro_layout, agent_name)
        click.echo("   - Generating Dockerfile...")
        with open(os.path.join(build_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
            
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

def generate_dockerfile(is_pro_layout, agent_name):
    """This is a new helper function to generate the Dockerfile dynamically"""
    if is_pro_layout:
        # Dockerfile for the professional, src-based layout
        return f"""
# Stage 1: Build the braid library
FROM python:3.11-slim as builder
WORKDIR /app
COPY ./braid_src /app/braid_src
RUN pip install --no-cache-dir ./braid_src

# Stage 2: Final application image
FROM python:3.11-slim
WORKDIR /app

# Copy the installed braid library from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Install poetry and then the agent's dependencies
RUN pip install poetry
COPY ./agent_code/pyproject.toml ./agent_code/poetry.lock* /app/
RUN poetry install --no-root --no-dev

# Copy the agent's source code into the container
COPY ./agent_code/src/ /app/src

# Set the python path and run the agent as a module
ENV PYTHONPATH="/app"
CMD ["poetry", "run", "python", "-m", "{agent_name}.agent"]
"""
    else: # Simple layout
        # Return the original Dockerfile template for simple agents
        return DOCKERFILE_TEMPLATE

# We need to move the original template into a variable at the top
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