from typing import TypedDict, Annotated, Literal
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from .tools import screen_stocks
from core.memory import get_checkpointer
from core.user_profile import get_user_preferences, save_user_preferences

# TODO: Swap with a persistent backend like Redis or Postgres for production.

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_id: str
    # TODO: Replace with a proper user profile store (e.g., a DB).
    user_preferences: dict

tools = [screen_stocks, get_user_preferences, save_user_preferences]
tool_node = ToolNode(tools)

# Use a model that supports tools. gpt-4o is a good choice.
model = ChatOpenAI(temperature=0, model="gpt-4o")
model = model.bind_tools(tools)

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Conditional edge to decide whether to call a tool or end the conversation."""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

def call_model(state: AgentState) -> dict:
    """The primary node for the agent's logic."""
    user_id = state['user_id']
    system_message = SystemMessage(content=f"""
You are an expert stock recommender agent. Your goal is to help users find stocks based on their preferences.
- When the user provides their preferences, your first step is to save them using the `save_user_preferences` tool.
- The `user_id` for this user is '{user_id}'. You MUST use this exact ID when calling any user profile tool.
- After saving, proceed to call the `screen_stocks` tool to find recommendations.
- Do not ask the user for their user_id.
""")
    
    # Prepend the system message to the message history.
    # This guides the model without permanently altering the state's message list.
    messages = [system_message] + state["messages"]
    
    response = model.invoke(messages)
    return {"messages": [response]}

def build_agent():
    """Builds the LangGraph agent."""
    builder = StateGraph(AgentState)

    builder.add_node("agent", call_model)
    builder.add_node("tools", tool_node)

    builder.set_entry_point("agent")

    builder.add_conditional_edges(
        "agent",
        should_continue,
    )
    builder.add_edge("tools", "agent")
    
    # Use the factory to get the appropriate checkpointer.
    graph = builder.compile(checkpointer=get_checkpointer())
    return graph 