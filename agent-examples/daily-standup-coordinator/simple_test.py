"""
Very simple test to isolate the LangGraph issue
"""
import os
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment
load_dotenv()

# Simple state
class SimpleState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# Create a basic LLM without tools for now
llm = ChatOpenAI(model="gpt-4o")

def simple_agent_node(state: SimpleState):
    """Simple agent that just responds without tools."""
    # Add a system message if none exists
    messages = state["messages"]
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_msg = SystemMessage(content="You are a helpful assistant.")
        messages = [system_msg] + messages
    
    response = llm.invoke(messages)
    return {"messages": [response]}

# Build the simplest possible graph
builder = StateGraph(SimpleState)
builder.add_node("assistant", simple_agent_node)
builder.add_edge(START, "assistant")
simple_graph = builder.compile()

def test_simple():
    """Test the simplest possible graph."""
    print("🧪 Testing simple graph...")
    
    try:
        result = simple_graph.invoke({"messages": [HumanMessage(content="Hello!")]})
        response = result["messages"][-1]
        print(f"✅ Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple()