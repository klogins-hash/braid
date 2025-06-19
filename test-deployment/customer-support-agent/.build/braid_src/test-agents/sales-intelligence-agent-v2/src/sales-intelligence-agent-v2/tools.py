"""Tool definitions for the sales-intelligence-agent-v2 agent."""

# Import tools based on selected tool packages
from sales-intelligence-agent-v2.csv_tools import get_csv_tools
from sales-intelligence-agent-v2.files_tools import get_files_tools
from sales-intelligence-agent-v2.http_tools import get_http_tools
from sales-intelligence-agent-v2.slack_tools import get_slack_tools
from sales-intelligence-agent-v2.gworkspace_tools import get_gworkspace_tools

# Collect all tools
TOOLS = []
TOOLS.extend(get_csv_tools())
TOOLS.extend(get_files_tools())
TOOLS.extend(get_http_tools())
TOOLS.extend(get_slack_tools())
TOOLS.extend(get_gworkspace_tools())

def get_tools():
    """Get all available tools for the agent."""
    return TOOLS