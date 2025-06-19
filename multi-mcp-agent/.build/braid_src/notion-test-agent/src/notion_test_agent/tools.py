"""Tool definitions for the notion_test_agent agent."""

# Import tools based on selected tool packages
from notion_test_agent.files_tools import get_files_tools
from notion_test_agent.csv_tools import get_csv_tools

# Collect all tools
TOOLS = []
TOOLS.extend(get_files_tools())
TOOLS.extend(get_csv_tools())

def get_tools():
    """Get all available tools for the agent."""
    return TOOLS