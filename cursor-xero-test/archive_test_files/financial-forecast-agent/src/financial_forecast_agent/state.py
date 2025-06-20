"""State definition for the financial_forecast_agent agent."""

from typing import Annotated, List, TypedDict, Optional, Dict, Any

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state of the agent conversation."""
    
    messages: Annotated[List[AnyMessage], add_messages]
    
    # Workflow tracking
    current_step: str
    user_id: str
    
    # Data storage
    xero_data: Optional[Dict[str, Any]]
    client_info: Optional[Dict[str, Any]]
    historical_data: Optional[List[Dict[str, Any]]]
    market_research: Optional[str]
    forecast_assumptions: Optional[Dict[str, Any]]
    forecast_results: Optional[Dict[str, Any]]
    validation_feedback: Optional[Dict[str, Any]]
    
    # Final outputs
    notion_report_url: Optional[str]
    forecast_id: Optional[str]


class InputState(TypedDict):
    """Input state for the agent."""
    
    messages: Annotated[List[AnyMessage], add_messages]
    user_id: str