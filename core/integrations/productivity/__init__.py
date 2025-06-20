"""Productivity Integrations"""

def get_all_productivity_tools():
    """Get all productivity tools from all services."""
    tools = []
    
    try:
        from .notion import create_notion_page, get_notion_page, update_notion_page
        tools.extend([create_notion_page, get_notion_page, update_notion_page])
    except ImportError:
        pass
    
    try:
        from .gworkspace import get_gworkspace_tools
        tools.extend(get_gworkspace_tools())
    except ImportError:
        pass
    
    try:
        from .perplexity import perplexity_search, perplexity_market_research, perplexity_ask
        tools.extend([perplexity_search, perplexity_market_research, perplexity_ask])
    except ImportError:
        pass
    
    return tools

def get_documentation_tools():
    """Get documentation and note-taking tools."""
    tools = []
    
    try:
        from .notion import create_notion_page, get_notion_page, update_notion_page
        tools.extend([create_notion_page, get_notion_page, update_notion_page])
    except ImportError:
        pass
    
    return tools

def get_research_tools():
    """Get research and information gathering tools."""
    tools = []
    
    try:
        from .perplexity import perplexity_search, perplexity_market_research, perplexity_ask
        tools.extend([perplexity_search, perplexity_market_research, perplexity_ask])
    except ImportError:
        pass
    
    return tools

def get_workspace_tools():
    """Get workspace and collaboration tools."""
    tools = []
    
    try:
        from .gworkspace import get_gworkspace_tools
        tools.extend(get_gworkspace_tools())
    except ImportError:
        pass
    
    try:
        from .notion import create_notion_page, update_notion_page
        tools.extend([create_notion_page, update_notion_page])
    except ImportError:
        pass
    
    return tools