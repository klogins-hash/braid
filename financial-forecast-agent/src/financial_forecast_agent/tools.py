"""Tool definitions for the financial_forecast_agent agent."""

# Import tools based on selected tool packages
from financial_forecast_agent.files_tools import get_files_tools
from financial_forecast_agent.http_tools import get_http_tools
from financial_forecast_agent.transform_tools import get_transform_tools
from financial_forecast_agent.forecast_toolkit.tools import forecast_tools

# Collect all tools
TOOLS = []
TOOLS.extend(get_files_tools())
TOOLS.extend(get_http_tools())
TOOLS.extend(get_transform_tools())
TOOLS.extend(forecast_tools)

def get_tools():
    """Get all available tools for the agent."""
    return TOOLS