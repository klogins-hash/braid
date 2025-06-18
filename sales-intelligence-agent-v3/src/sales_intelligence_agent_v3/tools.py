"""Tool definitions for the sales_intelligence_agent_v3 agent."""

# Import tools based on selected tool packages
from sales_intelligence_agent_v3.csv_tools import get_csv_tools
from sales_intelligence_agent_v3.files_tools import get_files_tools
from sales_intelligence_agent_v3.http_tools import get_http_tools

# Collect all tools
TOOLS = []
TOOLS.extend(get_csv_tools())
TOOLS.extend(get_files_tools())
TOOLS.extend(get_http_tools())

def get_tools():
    """Get all available tools for the agent."""
    return TOOLS