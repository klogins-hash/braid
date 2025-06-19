import click
import os
import shutil
import toml

# --- pyproject.toml Template ---
PYPROJECT_TEMPLATE = """
[tool.poetry]
name = "{agent_name}"
version = "0.1.0"
description = "A Braid-generated agent."
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
# Core dependencies will be added here

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.2"
ruff = "^0.5.5"

[tool.pytest.ini_options]
pythonpath = [
    "src"
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

# --- Makefile Template ---
MAKEFILE_TEMPLATE = """
# Makefile for {agent_name}

# Ensure poetry is installed
.PHONY: check-poetry
check-poetry:
	@command -v poetry >/dev/null 2>&1 || (echo "Poetry not found. Please install it: https://python-poetry.org/docs/#installation" && exit 1)

# Install dependencies
.PHONY: install
install: check-poetry
	@echo "Installing dependencies..."
	@poetry install

# Run the agent
.PHONY: run
run: check-poetry
	@echo "Running the agent..."
	@poetry run python -m {agent_name}.agent

# Run tests
.PHONY: test
test: check-poetry
	@echo "Running tests..."
	@poetry run pytest

# Lint the code
.PHONY: lint
lint: check-poetry
	@echo "Linting code..."
	@poetry run ruff check src tests

# Format the code
.PHONY: format
format: check-poetry
	@echo "Formatting code..."
	@poetry run ruff format src tests

.PHONY: all
all: install lint test
"""

# --- CI/CD Template ---
CI_TEMPLATE = """
name: Python application

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install Poetry
      uses: snok/install-poetry@v1
    - name: Install dependencies
      run: poetry install
    - name: Lint with ruff
      run: poetry run ruff check src tests
    - name: Test with pytest
      run: poetry run pytest
"""

# --- Placeholder Test Template ---
TEST_TEMPLATE = """
import pytest
from {agent_name}.agent import main # A basic import test

def test_agent_runs():
    \"\"\"
    A basic placeholder test.
    In a real scenario, you would mock inputs and assert outputs.
    \"\"\"
    # This is not a real test, just a placeholder to ensure the test suite runs.
    # For a real test, you would need to refactor agent.py to be more testable.
    assert True
"""

@click.command()
def add_pro_pack_command():
    """
    Upgrades a simple agent to a professional Python project structure.
    This includes adding a src/ layout, pyproject.toml, tests, and CI/CD boilerplate.
    This command should be run from the root of an agent's directory.
    """
    agent_root = os.getcwd()
    agent_name = os.path.basename(agent_root).replace("-", "_") # Make it a valid python package name
    
    click.echo(f"🚀 Upgrading '{agent_name}' to a professional project...")

    # --- 1. Pre-flight Checks ---
    if not os.path.exists(os.path.join(agent_root, "agent.py")):
        click.echo("Error: 'agent.py' not found. Command must be run from an agent's root directory.", err=True)
        return
    if not os.path.exists(os.path.join(agent_root, "requirements.txt")):
        click.echo("Error: 'requirements.txt' not found. Cannot upgrade project.", err=True)
        return
        
    # --- 2. Create src/ layout and move files ---
    click.echo("   - Creating src layout...")
    src_dir = os.path.join(agent_root, "src")
    package_dir = os.path.join(src_dir, agent_name)
    os.makedirs(package_dir, exist_ok=True)
    
    # Create __init__.py files
    open(os.path.join(src_dir, "__init__.py"), 'a').close()
    open(os.path.join(package_dir, "__init__.py"), 'a').close()
    
    shutil.move(os.path.join(agent_root, "agent.py"), package_dir)
    if os.path.exists(os.path.join(agent_root, "tools")):
        shutil.move(os.path.join(agent_root, "tools"), package_dir)
        
    # --- 3. Create pyproject.toml ---
    click.echo("   - Generating pyproject.toml...")
    
    # Parse dependencies from requirements.txt
    with open(os.path.join(agent_root, "requirements.txt"), 'r') as f:
        deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Create the pyproject.toml content
    pyproject_content = PYPROJECT_TEMPLATE.format(agent_name=agent_name)
    pyproject_data = toml.loads(pyproject_content)
    
    # Add dependencies
    for dep in deps:
        package, version_spec = dep.split('>=', 1) if '>=' in dep else (dep, '*')
        
        # Use more specific, known-good versions for the core LangChain stack
        if package == 'langchain':
            version = ">=0.2.10,<0.3.0"
        elif package == 'langgraph':
            version = ">=0.1.8,<0.2.0"
        elif package == 'langchain-openai':
            version = ">=0.1.16,<0.2.0"
        elif version_spec != '*':
            version = f">={version_spec}"
        else:
            version = '*'
            
        pyproject_data["tool"]["poetry"]["dependencies"][package] = version

    with open(os.path.join(agent_root, "pyproject.toml"), 'w') as f:
        toml.dump(pyproject_data, f)
        
    # --- 4. Create tests/ directory ---
    click.echo("   - Creating tests directory...")
    tests_dir = os.path.join(agent_root, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    with open(os.path.join(tests_dir, "test_agent.py"), 'w') as f:
        f.write(TEST_TEMPLATE.format(agent_name=agent_name))

    # --- 5. Create Makefile ---
    click.echo("   - Creating Makefile...")
    with open(os.path.join(agent_root, "Makefile"), 'w') as f:
        f.write(MAKEFILE_TEMPLATE.format(agent_name=agent_name))
        
    # --- 5b. Create README.md ---
    click.echo("   - Creating README.md...")
    with open(os.path.join(agent_root, "README.md"), 'w') as f:
        f.write(f"# {agent_name}\\n\\nThis is a Braid-generated agent.\\n")

    # --- 6. Create .github/workflows/ci.yml ---
    click.echo("   - Creating GitHub CI workflow...")
    github_dir = os.path.join(agent_root, ".github", "workflows")
    os.makedirs(github_dir, exist_ok=True)
    with open(os.path.join(github_dir, "ci.yml"), 'w') as f:
        f.write(CI_TEMPLATE)

    # --- 7. Delete old requirements.txt ---
    click.echo("   - Cleaning up old files...")
    os.remove(os.path.join(agent_root, "requirements.txt"))

    # Placeholder for the logic to come
    # 1. Pre-flight checks
    # 2. Create src/ layout and move files
    # 3. Create pyproject.toml
    # 4. Create tests/ directory
    # 5. Create Makefile
    # 6. Create .github/workflows/ci.yml
    # 7. Delete old requirements.txt
    
    click.echo(f"✅ '{agent_name}' has been successfully upgraded.")
    click.echo("   Please review the new files and update them as needed.")
    click.echo("   Next steps: Run 'poetry install' to create a lock file and install dependencies.") 