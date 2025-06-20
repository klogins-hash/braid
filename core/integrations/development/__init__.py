"""Development Integrations"""

def get_all_development_tools():
    """Get all development tools from all services."""
    tools = []
    
    try:
        from .agentql import get_agentql_tools
        tools.extend(get_agentql_tools())
    except ImportError:
        pass
    
    return tools

def get_web_scraping_tools():
    """Get web scraping and data extraction tools."""
    tools = []
    
    try:
        from .agentql import get_extraction_tools
        tools.extend(get_extraction_tools())
    except ImportError:
        pass
    
    return tools

def get_automation_tools():
    """Get automation and workflow tools."""
    return get_all_development_tools()