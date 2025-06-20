"""
Xero Direct API Integration for Braid

Provides real financial data from Xero accounting system
with authentication caching fixes and transparent data sourcing.
"""

from .tools import (
    get_xero_profit_and_loss,
    get_xero_balance_sheet,
    get_xero_trial_balance
)

__all__ = [
    'get_xero_profit_and_loss',
    'get_xero_balance_sheet', 
    'get_xero_trial_balance'
]

__version__ = "1.0.0"
__author__ = "Braid"
__description__ = "Direct Xero API integration for accounting data"