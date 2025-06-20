"""
Xero API integration for Braid.

Quick Setup:
    python -m core.integrations.xero.setup

Usage:
    from core.integrations.xero import get_xero_profit_and_loss
    
    # Get Year-to-Date P&L data
    pl_data = get_xero_profit_and_loss.invoke({})
"""

from .tools import (
    get_xero_profit_and_loss,
    get_xero_balance_sheet,
    get_xero_trial_balance,
    get_xero_tools
)

from .setup import (
    setup_xero_integration,
    test_xero_connection
)

__all__ = [
    "get_xero_profit_and_loss",
    "get_xero_balance_sheet", 
    "get_xero_trial_balance",
    "get_xero_tools",
    "setup_xero_integration",
    "test_xero_connection"
]