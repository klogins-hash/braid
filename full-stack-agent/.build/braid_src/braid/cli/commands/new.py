import click
import os
import shutil
import sys
from pathlib import Path

# Add core modules to path for MCP integration
braid_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(braid_root))

try:
    from core.mcp.discovery import MCPDiscovery
    from core.mcp.registry import MCPRegistry
    from core.mcp.integration import MCPIntegrator
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False

# Tool Registry - Organized with clear separation between in-house tools and integrations
# 
# Structure:
# core/tools/: In-house built tool libraries
#   - data/: Data handling (files, CSV, databases)
#   - network/: Network operations (HTTP, webhooks, FTP)
#   - workflow/: Workflow control (execution, code, forms)  
#   - utilities/: General utilities (debug, transform)
# core/integrations/: External service integrations
#   - gworkspace/: Google Workspace integration
#   - slack/: Slack integration
#   - ms365/: Microsoft 365 integration (future)

TOOL_REGISTRY = {
    # === EXTERNAL INTEGRATIONS ===
    "gworkspace": {
        "source_path": "core/integrations/gworkspace/tools.py",
        "dependencies": [
            "# Google Workspace Integration",
            "google-api-python-client>=2.0.0",
            "google-auth-httplib2>=0.1.0",
            "google-auth-oauthlib>=0.7.0",
        ],
        "category": "integrations",
        "description": "Google Workspace tools (Gmail, Calendar, Sheets, Drive)"
    },
    "slack": {
        "source_path": "core/integrations/slack/tools.py",
        "dependencies": [
            "# Slack Integration",
            "slack_sdk>=3.0.0",
        ],
        "category": "integrations",
        "description": "Slack messaging and workspace tools"
    },
    
    # === IN-HOUSE DATA TOOLS ===
    "files": {
        "source_path": "core/tools/data/files/tools.py",
        "dependencies": [
            "# File System Operations",
            "# (uses standard library only)",
        ],
        "category": "data",
        "description": "File read/write operations and directory management"
    },
    "csv": {
        "source_path": "core/tools/data/csv/tools.py",
        "dependencies": [
            "# CSV Data Processing",
            "# (uses standard library only)",
        ],
        "category": "data",
        "description": "CSV file processing and analysis tools"
    },
    "transform": {
        "source_path": "core/tools/data/transform/tools.py",
        "dependencies": [
            "# Data Transformation",
            "# (uses standard library only)",
        ],
        "category": "data",
        "description": "Data transformation tools: edit fields, filter, sort, dates"
    },
    
    # === IN-HOUSE NETWORK TOOLS ===
    "http": {
        "source_path": "core/tools/network/http/tools.py", 
        "dependencies": [
            "# HTTP/Web Operations",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
        ],
        "category": "network",
        "description": "HTTP requests and web scraping tools"
    },
    
    # === IN-HOUSE WORKFLOW TOOLS ===
    "execution": {
        "source_path": "core/tools/workflow/execution/tools.py",
        "dependencies": [
            "# Workflow Execution Control",
            "# (uses standard library only)",
        ],
        "category": "workflow", 
        "description": "Workflow control: wait, sub-workflows, execution data"
    },
    "code": {
        "source_path": "core/tools/workflow/code/tools.py",
        "dependencies": [
            "# Code Execution",
            "# (uses standard library only)",
            "# Note: JavaScript execution requires Node.js to be installed",
        ],
        "category": "workflow",
        "description": "Python and JavaScript code execution tools"
    },
    
    # === LEGACY COMPATIBILITY (for backward compatibility) ===
    "web": {
        "source_path": "core/tools/network/http/tools.py",  # Redirect to new location
        "dependencies": [
            "# HTTP/Web Operations (legacy name)",
            "requests>=2.28.0", 
            "beautifulsoup4>=4.11.0",
        ],
        "category": "network",
        "description": "HTTP requests and web scraping tools (legacy name, use 'http' instead)"
    },
}


@click.command()
@click.argument('project_name')
@click.option('--tools', '-t', help='A comma-separated list of tool packages to include (e.g., "slack,gworkspace").')
@click.option('--mcps', '-m', help='A comma-separated list of MCP servers to include (e.g., "notion,github").')
@click.option('--production', '-p', is_flag=True, help='Create a production-ready agent with full project structure.')
@click.option('--description', '-d', default='AI assistant', help='Brief description of what the agent does.')
@click.option('--no-mcp-discovery', is_flag=True, help='Skip interactive MCP discovery and suggestions.')
def new_command(project_name, tools, mcps, production, description, no_mcp_discovery):
    """
    Creates a new Braid agent project from a template.
    You can specify foundational tools to include with --tools and MCPs with --mcps.
    Use --production to create a full production-ready structure.
    
    Examples: 
      braid new my_agent --tools slack,gworkspace
      braid new my_agent --mcps notion --description "Knowledge management assistant"
      braid new my_agent --production --tools slack --mcps notion,github --description "DevOps assistant"
      braid new my_agent --description "Customer support bot" --no-mcp-discovery
    """
    tool_list = [tool.strip() for tool in tools.split(',')] if tools else []
    for tool_name in tool_list:
        if tool_name not in TOOL_REGISTRY:
            click.echo(f"Error: Unknown tool '{tool_name}'. Available tools are: {', '.join(TOOL_REGISTRY.keys())}", err=True)
            return

    # Process MCPs
    mcp_list = [mcp.strip() for mcp in mcps.split(',')] if mcps else []
    suggested_mcps = []
    
    # Validate explicitly requested MCPs
    if MCP_AVAILABLE and mcp_list:
        registry = MCPRegistry()
        for mcp_name in mcp_list:
            mcp_data = registry.get_mcp_by_id(mcp_name)
            if not mcp_data:
                available_mcps = [mcp_id for mcp_id in registry.list_mcps()]
                click.echo(f"Error: Unknown MCP '{mcp_name}'. Available MCPs are: {', '.join(available_mcps)}", err=True)
                return
    
    # Intelligent MCP discovery based on description
    if MCP_AVAILABLE and not no_mcp_discovery and description != 'AI assistant':
        discovery = MCPDiscovery()
        analysis = discovery.analyze_task_description(description)
        
        # Get high-confidence suggestions (>70%)
        high_confidence_mcps = [
            mcp for mcp in analysis.get('suggested_mcps', [])
            if mcp.get('confidence', 0) > 0.7
        ]
        
        if high_confidence_mcps:
            suggested_mcps = _interactive_mcp_selection(high_confidence_mcps, description, mcp_list)
            mcp_list.extend(suggested_mcps)

    # Path to the base template directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    template_type = 'production' if production else 'default'
    template_dir = os.path.join(project_root, 'braid', 'templates', template_type)
    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        click.echo(f"Error: Directory '{project_name}' already exists.", err=True)
        return

    try:
        if production:
            _create_production_agent(project_root, project_path, project_name, tool_list, mcp_list, description)
        else:
            _create_basic_agent(template_dir, project_path, project_name, tool_list, mcp_list, project_root)

        success_message = f"✨ Agent '{project_name}' created successfully"
        if production:
            success_message += " (production-ready)"
        
        integrations = []
        if tool_list:
            integrations.append(f"tools: {', '.join(tool_list)}")
        if mcp_list:
            integrations.append(f"MCPs: {', '.join(mcp_list)}")
        if integrations:
            success_message += f" with {', '.join(integrations)}"
        
        click.echo(success_message)
        
        # Show MCP-specific information
        if mcp_list:
            click.echo(f"   🔧 MCP servers configured: {len(mcp_list)}")
            if suggested_mcps:
                click.echo(f"   🤖 AI-suggested MCPs: {', '.join(suggested_mcps)}")
            click.echo(f"   📋 Next: Configure MCP environment variables in .env file")
        
        click.echo(f"   To get started, run:")
        click.echo(f"   cd {project_name}")
        if production:
            click.echo(f"   pip install -e '.[dev]'")
            click.echo(f"   cp .env.example .env")
            click.echo(f"   # Fill in your .env file")
            click.echo(f"   python src/{project_name}/graph.py")
            click.echo(f"   # Or run tests with: make test")
        else:
            click.echo(f"   pip install -r requirements.txt")
            click.echo(f"   # Fill in your .env file")
            click.echo(f"   python agent.py")

    except Exception as e:
        click.echo(f"Error creating project: {e}", err=True)
        # Clean up failed project creation
        if os.path.exists(project_path):
            shutil.rmtree(project_path) 


def _create_basic_agent(template_dir, project_path, project_name, tool_list, mcp_list, project_root):
    """Create a basic agent using the default template."""
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
    
    # 3. Update agent.py with proper tool imports
    if tool_list:
        agent_file_path = os.path.join(project_path, 'agent.py')
        with open(agent_file_path, 'r') as f:
            agent_content = f.read()
        
        # Generate tool import statements
        tool_imports = []
        tool_getters = []
        
        for tool_name in tool_list:
            tool_imports.append(f"from tools.{tool_name}_tools import get_{tool_name}_tools")
            tool_getters.append(f"get_{tool_name}_tools()")
        
        # Replace the commented imports and empty tool list
        import_lines = '\n'.join(tool_imports)
        tool_aggregation = ' + '.join(tool_getters)
        
        # Update the agent content
        agent_content = agent_content.replace(
            "# Import tools - these will be populated by the CLI based on --tools selection\n# from tools.slack_tools import get_slack_tools\n# from tools.gworkspace_tools import get_gworkspace_tools",
            f"# Import tools\n{import_lines}"
        )
        
        agent_content = agent_content.replace(
            "all_tools = []  # get_slack_tools() + get_gworkspace_tools()",
            f"all_tools = {tool_aggregation}"
        )
        
        # Write back the updated agent content
        with open(agent_file_path, 'w') as f:
            f.write(agent_content)
    
    # 4. Aggregate and write dependencies to requirements.txt
    base_deps = [
        "# Core Agent & LLM Dependencies",
        "langchain>=0.2.10,<0.3.0",
        "langgraph>=0.1.19,<0.2.0",
        "langchain-openai>=0.1.16,<0.2.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.0.0",
        ""
    ]
    
    tool_deps = []
    for tool_name in tool_list:
        tool_deps.extend(TOOL_REGISTRY[tool_name]["dependencies"])
        tool_deps.append("")

    with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
        f.write('\n'.join(base_deps + tool_deps))
    
    # 5. Add MCP integration if MCPs are specified
    if MCP_AVAILABLE and mcp_list:
        _integrate_mcps_basic(project_path, mcp_list, project_root)


def _create_production_agent(project_root, project_path, project_name, tool_list, mcp_list, description):
    """Create a production-ready agent using the production template."""
    template_dir = os.path.join(project_root, 'braid', 'templates', 'production')
    
    # Convert project name to valid Python module name (replace hyphens with underscores)
    module_name = project_name.replace('-', '_')
    
    # 1. Copy template and rename AGENT_NAME directories
    shutil.copytree(template_dir, project_path)
    
    # Rename the AGENT_NAME directory in src/
    src_agent_dir = os.path.join(project_path, 'src', 'AGENT_NAME')
    new_src_agent_dir = os.path.join(project_path, 'src', module_name)
    os.rename(src_agent_dir, new_src_agent_dir)
    
    # 2. Process template files with replacements
    replacements = {
        '{AGENT_NAME}': module_name,  # Use underscore version for Python imports
        '{AGENT_DESCRIPTION}': description,
        'AGENT_NAME': module_name,  # For file content replacements
    }
    
    # Add tool-specific replacements
    tool_imports = []
    tool_collection = []
    tool_dependencies = []
    tool_env_vars = []
    tool_config_vars = []
    tool_validation = []
    tool_descriptions = []
    
    for tool_name in tool_list:
        tool_info = TOOL_REGISTRY[tool_name]
        
        # Copy tool file to src directory
        source_file_path = os.path.join(project_root, tool_info["source_path"])
        dest_file_path = os.path.join(new_src_agent_dir, f"{tool_name}_tools.py")
        shutil.copy2(source_file_path, dest_file_path)
        
        # Generate imports and collections
        tool_imports.append(f"from {module_name}.{tool_name}_tools import get_{tool_name}_tools")
        tool_collection.append(f"TOOLS.extend(get_{tool_name}_tools())")
        
        # Add dependencies
        for dep in tool_info["dependencies"]:
            if not dep.startswith("#") and dep.strip():
                tool_dependencies.append(f'    "{dep}",')
        
        # Add tool-specific configurations (simplified)
        if tool_name == "slack":
            tool_env_vars.append("# SLACK_BOT_TOKEN=your-slack-bot-token")
            tool_config_vars.append("        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')")
            tool_validation.append("        if not self.slack_bot_token and 'slack' in tools: missing.append('SLACK_BOT_TOKEN')")
        elif tool_name == "gworkspace":
            tool_env_vars.append("# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json")
            
        tool_descriptions.append(f"- {tool_info['description']}")
    
    replacements.update({
        '{TOOL_IMPORTS}': '\n'.join(tool_imports),
        '{TOOL_COLLECTION}': '\n'.join(tool_collection),
        '{TOOL_DEPENDENCIES}': '\n'.join(tool_dependencies),
        '{TOOL_ENV_VARS}': '\n'.join(tool_env_vars),
        '{TOOL_CONFIG_VARS}': '\n'.join(tool_config_vars),
        '{TOOL_VALIDATION}': '\n'.join(tool_validation),
        '{TOOL_DESCRIPTIONS}': '\n'.join(tool_descriptions),
    })
    
    # 3. Process all files and replace placeholders
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(('.py', '.toml', '.json', '.md', '.txt', '.example')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for placeholder, replacement in replacements.items():
                    content = content.replace(placeholder, replacement)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    # 4. Add MCP integration if MCPs are specified
    if MCP_AVAILABLE and mcp_list:
        _integrate_mcps_production(project_path, mcp_list, project_root)


def _interactive_mcp_selection(suggested_mcps, description, existing_mcps):
    """Interactive MCP selection based on AI suggestions."""
    if not suggested_mcps:
        return []
    
    click.echo(f"\n🤖 Based on your description '{description}', I found relevant MCPs:")
    click.echo("   MCPs are external services that extend your agent's capabilities.")
    
    selected_mcps = []
    
    for mcp in suggested_mcps:
        if mcp['mcp_id'] in existing_mcps:
            continue  # Skip already selected MCPs
        
        confidence_indicator = "🔥" if mcp['confidence'] > 0.9 else "✨" if mcp['confidence'] > 0.8 else "💡"
        click.echo(f"\n   {confidence_indicator} {mcp['name']} (confidence: {mcp['confidence']:.0%})")
        click.echo(f"      Category: {mcp.get('category', 'unknown')}")
        click.echo(f"      Description: {mcp.get('description', 'No description available')}")
        
        if mcp.get('use_cases'):
            click.echo(f"      Use cases: {', '.join(mcp['use_cases'][:2])}")
        
        # Show why it was suggested
        if mcp.get('match_reasons'):
            reasons = ', '.join(mcp['match_reasons'][:2])
            click.echo(f"      Why suggested: {reasons}")
        
        choice = click.prompt(f"   Add {mcp['name']} to your agent?", 
                            type=click.Choice(['y', 'n', 's']), 
                            default='y' if mcp['confidence'] > 0.85 else 'n',
                            show_choices=True,
                            show_default=True)
        
        if choice == 'y':
            selected_mcps.append(mcp['mcp_id'])
            click.echo(f"   ✅ Added {mcp['name']}")
        elif choice == 's':
            break  # Skip remaining suggestions
    
    if selected_mcps:
        click.echo(f"\n🎯 Selected {len(selected_mcps)} MCP(s): {', '.join(selected_mcps)}")
    
    return selected_mcps


def _integrate_mcps_basic(project_path, mcp_list, project_root):
    """Integrate MCPs into a basic agent."""
    try:
        integrator = MCPIntegrator()
        integration_result = integrator.prepare_mcp_integration(project_path, mcp_list)
        
        if integration_result["success"]:
            # Create .env.example with MCP environment variables
            env_vars = set()
            for var_list in integration_result["environment_vars"]:
                if isinstance(var_list, list):
                    env_vars.update(var_list)
                else:
                    env_vars.add(var_list)
            
            if env_vars:
                env_example_path = os.path.join(project_path, ".env.example")
                
                # Read existing content if file exists
                existing_content = ""
                if os.path.exists(env_example_path):
                    with open(env_example_path, 'r') as f:
                        existing_content = f.read()
                
                # Add MCP environment variables
                with open(env_example_path, 'a') as f:
                    if existing_content and not existing_content.endswith('\n'):
                        f.write('\n')
                    f.write('\n# MCP Configuration\n')
                    for var in sorted(env_vars):
                        f.write(f'# {var}=your-{var.lower().replace("_", "-")}\n')
        
    except Exception as e:
        click.echo(f"Warning: Failed to integrate MCPs: {e}", err=True)


def _integrate_mcps_production(project_path, mcp_list, project_root):
    """Integrate MCPs into a production agent."""
    try:
        integrator = MCPIntegrator()
        integration_result = integrator.prepare_mcp_integration(project_path, mcp_list)
        
        if integration_result["success"]:
            # Update .env.example with MCP environment variables
            env_vars = set()
            for var_list in integration_result["environment_vars"]:
                if isinstance(var_list, list):
                    env_vars.update(var_list)
                else:
                    env_vars.add(var_list)
            
            if env_vars:
                env_example_path = os.path.join(project_path, ".env.example")
                
                # Read existing content
                existing_content = ""
                if os.path.exists(env_example_path):
                    with open(env_example_path, 'r') as f:
                        existing_content = f.read()
                
                # Add MCP environment variables
                with open(env_example_path, 'a') as f:
                    if existing_content and not existing_content.endswith('\n'):
                        f.write('\n')
                    f.write('\n# === MCP Server Configuration ===\n')
                    for var in sorted(env_vars):
                        f.write(f'# {var}=your-{var.lower().replace("_", "-")}\n')
            
            # Add MCP information to README
            readme_path = os.path.join(project_path, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    readme_content = f.read()
                
                # Add MCP section
                mcp_section = f"""

## MCP Integration

This agent uses the following Model Context Protocol (MCP) servers:

"""
                registry = MCPRegistry()
                for mcp_id in mcp_list:
                    mcp_data = registry.get_mcp_by_id(mcp_id)
                    if mcp_data:
                        mcp_section += f"- **{mcp_data.get('name', mcp_id)}**: {mcp_data.get('description', 'No description')}\n"
                
                mcp_section += """
MCPs extend your agent's capabilities with external services. They run as separate processes and communicate via the Model Context Protocol.

### MCP Setup

1. Configure environment variables in `.env` file
2. MCPs are automatically dockerized during packaging (`braid package --production`)
3. Use `docker compose up --build` to run with MCP services

See `mcp/` directory for individual MCP configurations.
"""
                
                # Append MCP section to README
                readme_content += mcp_section
                
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                    
    except Exception as e:
        click.echo(f"Warning: Failed to integrate MCPs: {e}", err=True)