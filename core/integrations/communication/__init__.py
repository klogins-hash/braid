"""Communication Integrations"""

def get_all_communication_tools():
    """Get all communication tools from all services."""
    tools = []
    
    try:
        from .twilio import get_twilio_tools
        tools.extend(get_twilio_tools())
    except ImportError:
        pass
    
    try:
        from .slack import get_slack_tools
        tools.extend(get_slack_tools())
    except ImportError:
        pass
    
    return tools

def get_messaging_tools():
    """Get messaging-specific tools."""
    tools = []
    
    try:
        from .twilio import get_messaging_tools
        tools.extend(get_messaging_tools())
    except ImportError:
        pass
    
    try:
        from .slack import get_slack_tools
        tools.extend(get_slack_tools())
    except ImportError:
        pass
    
    return tools