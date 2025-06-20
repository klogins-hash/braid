"""Finance Integrations"""

def get_all_finance_tools():
    """Get all financial tools from all services."""
    tools = []
    
    try:
        from .xero import get_xero_profit_and_loss, get_xero_balance_sheet, get_xero_trial_balance
        tools.extend([get_xero_profit_and_loss, get_xero_balance_sheet, get_xero_trial_balance])
    except ImportError:
        pass
    
    try:
        from .alphavantage import get_alphavantage_tools
        tools.extend(get_alphavantage_tools())
    except ImportError:
        pass
    
    return tools

def get_accounting_tools():
    """Get accounting and bookkeeping tools."""
    tools = []
    
    try:
        from .xero import get_xero_profit_and_loss, get_xero_balance_sheet, get_xero_trial_balance
        tools.extend([get_xero_profit_and_loss, get_xero_balance_sheet, get_xero_trial_balance])
    except ImportError:
        pass
    
    return tools

def get_market_data_tools():
    """Get market data and analysis tools."""
    tools = []
    
    try:
        from .alphavantage import get_alphavantage_tools
        tools.extend(get_alphavantage_tools())
    except ImportError:
        pass
    
    return tools