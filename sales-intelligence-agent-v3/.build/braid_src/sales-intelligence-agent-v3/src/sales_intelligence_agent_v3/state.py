"""State definition for the sales_intelligence_agent_v3 agent."""

from typing import Annotated, List, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state of the agent conversation."""
    
    messages: Annotated[List[AnyMessage], add_messages]


class InputState(TypedDict):
    """Input state for the agent."""
    
    messages: Annotated[List[AnyMessage], add_messages]