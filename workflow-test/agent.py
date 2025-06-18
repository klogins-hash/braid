"""
LangGraph Agent Template
Basic LangGraph agent structure for tool-enabled AI assistants
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment variables FIRST
load_dotenv()

# Import tools
from tools.execution_tools import get_execution_tools
from tools.code_tools import get_code_tools
from tools.files_tools import get_files_tools
from tools.csv_tools import get_csv_tools

# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# --- Tool Setup ---
# TODO: Uncomment and modify based on your selected tools
all_tools = get_execution_tools() + get_code_tools() + get_files_tools() + get_csv_tools()
tool_node = ToolNode(all_tools) if all_tools else None

# --- Model and Prompt Setup ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""
You are a helpful AI assistant powered by LangGraph.

**Today's Date**: {current_date}

**Available Tools**: 
{len(all_tools)} tools available for various tasks.

**Instructions**:
- Help users with their requests using available tools when appropriate
- Be helpful, accurate, and concise
- If you need to use tools, explain what you're doing
- Ask for clarification when needed

**Safety**:
- Always confirm before taking actions that modify data
- Respect user privacy and data protection
- Be transparent about your capabilities and limitations
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(all_tools) if all_tools else llm

# --- Graph Definition ---
def agent_node(state: AgentState):
    """The assistant node: invokes the LLM to decide the next action."""
    # Format messages with system prompt
    messages = prompt.format_messages(messages=state["messages"])
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("assistant", agent_node)

if tool_node:
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
else:
    # Simple graph without tools
    builder.add_edge(START, "assistant")

graph = builder.compile()

# --- Main Execution Loop ---
def main():
    """Interactive conversation loop for testing the agent."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return

    print("✅ LangGraph Agent is ready!")
    print(f"📅 Today's date: {current_date}")
    print(f"🔧 Tools available: {len(all_tools)}")
    print("💬 Type 'quit' to exit\n")
    
    conversation: List[BaseMessage] = []
    
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
            
        conversation.append(HumanMessage(content=user_input))
        print("🤖 Processing...")
        
        try:
            result = graph.invoke({"messages": conversation})
            final_response = result["messages"][-1]
            conversation.append(final_response)
            
            print(f"🤖 Assistant: {final_response.content}")
            print("---")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---")

if __name__ == "__main__":
    main() 