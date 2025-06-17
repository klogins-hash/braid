import click
import os
import shutil

# A dictionary mapping tool names to their source paths and dependencies.
# This makes the CLI easily extensible.
TOOL_REGISTRY = {
    "gworkspace": {
        "source_path": "core/contrib/gworkspace/tools.py",
        "dependencies": [
            "# For Google Workspace Tools",
            "google-api-python-client>=2.0.0",
            "google-auth-httplib2>=0.1.0",
            "google-auth-oauthlib>=0.7.0",
        ],
    },
    "slack": {
        "source_path": "core/contrib/slack/tools.py",
        "dependencies": [
            "# For Slack Tools",
            "slack_sdk>=3.0.0",
        ],
    },
    # Add other tools here in the future
}


@click.command()
@click.argument('project_name')
@click.option('--tools', '-t', help='A comma-separated list of tool packages to include (e.g., "slack,gworkspace").')
def new_command(project_name, tools):
    """
    Creates a new Braid agent project from a template.
    You can specify foundational tools to include with --tools.
    Example: braid new my_agent --tools slack,gworkspace
    """
    tool_list = [tool.strip() for tool in tools.split(',')] if tools else []
    for tool_name in tool_list:
        if tool_name not in TOOL_REGISTRY:
            click.echo(f"Error: Unknown tool '{tool_name}'. Available tools are: {', '.join(TOOL_REGISTRY.keys())}", err=True)
            return

    # Path to the base template directory
    # The project root is the parent of the directory containing this script's package
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    template_dir = os.path.join(project_root, 'braid', 'templates', 'default')
    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        click.echo(f"Error: Directory '{project_name}' already exists.", err=True)
        return

    try:
        # 1. Copy the base template
        shutil.copytree(template_dir, project_path)
        
        # 2. If tools are specified, create a tools directory and copy them
        if tool_list:
            tools_dest_dir = os.path.join(project_path, 'tools')
            os.makedirs(tools_dest_dir, exist_ok=True)
            
            # Create an __init__.py to make it a package
            with open(os.path.join(tools_dest_dir, '__init__.py'), 'w') as f:
                pass

            for tool_name in tool_list:
                tool_info = TOOL_REGISTRY[tool_name]
                source_file_path = os.path.join(project_root, tool_info["source_path"])
                
                # Copy the specific tools file, renaming it for clarity
                dest_file_path = os.path.join(tools_dest_dir, f"{tool_name}_tools.py")
                shutil.copy2(source_file_path, dest_file_path)
        
        # 3. Aggregate and write dependencies to requirements.txt
        base_deps = [
            "# Core Agent & LLM Dependencies",
            "langchain>=0.2.10,<0.3.0",
            "langgraph>=0.1.8,<0.2.0",
            "langchain-openai>=0.1.16,<0.2.0",
            "python-dotenv>=1.0.0",
            "typing-extensions>=4.0.0",
            ""
        ]
        
        tool_deps = []
        for tool_name in tool_list:
            tool_deps.extend(TOOL_REGISTRY[tool_name]["dependencies"])
            tool_deps.append("") # Add a blank line for readability

        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(base_deps + tool_deps))

        click.echo(f"✨ Agent '{project_name}' created successfully with tools: {', '.join(tool_list) if tool_list else 'None'}")
        click.echo(f"   To get started, run:")
        click.echo(f"   cd {project_name}")
        click.echo(f"   pip install -r requirements.txt")
        click.echo(f"   # Fill in your .env file")
        click.echo(f"   python agent.py")

    except Exception as e:
        click.echo(f"Error creating project: {e}", err=True)
        # Clean up failed project creation
        if os.path.exists(project_path):
            shutil.rmtree(project_path) 