"""Type definitions for the financial forecasting agent."""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class ForecastState(TypedDict):
    """State for the financial forecasting agent."""
    messages: List[BaseMessage]
    current_step: str
    user_id: str
    xero_data: Optional[List[Dict[str, Any]]]
    client_info: Optional[Dict[str, Any]]
    market_research: Optional[str]
    forecast_assumptions: Optional[Dict[str, Any]]
    forecast_results: Optional[Dict[str, Dict[str, float]]]
    notion_report_url: Optional[str]
    workflow_complete: bool 