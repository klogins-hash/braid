"""
AlphaVantage Direct API Integration for Braid

Provides comprehensive financial market data including real-time stock quotes,
historical time series, forex rates, cryptocurrency data, and technical indicators
with direct API integration to avoid MCP server dependencies.

Features:
- Real-time stock quotes and company fundamentals
- Historical time series data (daily, intraday)
- Foreign exchange rates
- Cryptocurrency market data
- Technical analysis indicators (30+ indicators)
- Market research and portfolio analysis tools
"""

from .tools import (
    # Core stock data
    get_stock_quote,
    get_time_series_daily,
    get_time_series_intraday,
    get_company_overview,
    
    # Forex and crypto
    get_forex_rate,
    get_crypto_quote,
    
    # Technical analysis
    get_technical_indicator,
    get_sma,
    get_ema,
    get_rsi,
    get_macd,
    
    # Market analysis
    get_market_movers,
    get_sector_performance,
    
    # Tool collections
    get_alphavantage_tools,
    get_stock_tools,
    get_forex_tools,
    get_crypto_tools,
    get_technical_analysis_tools
)

__all__ = [
    # Core stock tools
    'get_stock_quote',
    'get_time_series_daily',
    'get_time_series_intraday',
    'get_company_overview',
    
    # Forex and crypto
    'get_forex_rate',
    'get_crypto_quote',
    
    # Technical analysis
    'get_technical_indicator',
    'get_sma',
    'get_ema', 
    'get_rsi',
    'get_macd',
    
    # Market analysis
    'get_market_movers',
    'get_sector_performance',
    
    # Tool collections
    'get_alphavantage_tools',
    'get_stock_tools',
    'get_forex_tools',
    'get_crypto_tools',
    'get_technical_analysis_tools'
]

__version__ = "1.0.0"
__author__ = "Braid"
__description__ = "Direct AlphaVantage API integration for financial market data"