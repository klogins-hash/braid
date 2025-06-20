"""Data Integrations"""

def get_all_data_tools():
    """Get all data tools from all services."""
    tools = []
    
    try:
        from .mongodb import get_mongodb_tools
        tools.extend(get_mongodb_tools())
    except ImportError:
        pass
    
    return tools

def get_database_tools():
    """Get database operation tools."""
    return get_all_data_tools()

def get_crud_tools():
    """Get CRUD operation tools only."""
    tools = []
    
    try:
        from .mongodb import get_mongodb_crud_tools
        tools.extend(get_mongodb_crud_tools())
    except ImportError:
        pass
    
    return tools