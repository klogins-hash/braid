"""Test tools module."""

from financial_forecast_agent.tools import get_tools


def test_get_tools():
    """Test that tools are properly loaded."""
    tools = get_tools()
    assert isinstance(tools, list)
    # Add specific tool tests based on selected tools