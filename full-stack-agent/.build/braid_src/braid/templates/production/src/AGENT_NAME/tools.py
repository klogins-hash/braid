"""Tool definitions for the {AGENT_NAME} agent."""

# Import tools based on selected tool packages
{TOOL_IMPORTS}

# Collect all tools
TOOLS = []
{TOOL_COLLECTION}

def get_tools():
    """Get all available tools for the agent."""
    return TOOLS