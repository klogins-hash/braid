"""
Project Kickoff Coordinator Agent

This agent orchestrates the project kickoff process by coordinating actions
across Slack and Google Workspace.
"""
import os
import json
import logging
from dotenv import load_dotenv
from typing import List, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.prebuilt import ToolNode, tools_condition

# Import all the tools from our local tool modules
# This is the key change for a standalone agent
from tools.slack_tools import get_slack_tools
from tools.google_calendar_tools import get_google_calendar_tools, get_current_date_context
from tools.gmail_tools import get_gmail_tools
from tools.gsheets_tools import get_gsheets_tools

# Load environment variables from .env file before anything else
load_dotenv()

# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# --- Tool Setup ---
slack_tools = get_slack_tools()
gcal_tools = get_google_calendar_tools()
gmail_tools = get_gmail_tools()
gsheets_tools = get_gsheets_tools()

all_tools = slack_tools + gcal_tools + gmail_tools + gsheets_tools
tool_node = ToolNode(all_tools)

# --- Model and Prompt Setup ---
system_prompt = f"""
You are an autonomous agent called the "Project Kickoff Coordinator."
Your job is to automate the entire kickoff process in a single, continuous workflow.

**Workflow:**
1.  **Find Users:** Use the `get_user_id_by_name` tool to find the Slack ID for every person mentioned.
2.  **Get Emails:** Use the `get_user_profile` tool with the user IDs to get their email addresses.
3.  **Create Event:** Use the `create_google_calendar_event` tool to schedule the meeting.
4.  **Log Project:** Use the `gsheets_append_row` tool to add a new row to the project tracker.
5.  **Notify:** Use `gmail_send_email` and `slack_post_message` to inform the team.

**CRITICAL INSTRUCTIONS:**
- Execute the workflow steps sequentially without asking for confirmation.
- If a tool fails, report the error and stop.
- Only provide a final summary message to the user after the entire workflow is complete. Do not output conversational messages between steps.

**IMPORTANT CONTEXT:**
- **Current Date/Time:** Use this information to correctly interpret dates like "next Tuesday".
{get_current_date_context()}
- **Google Sheets ID:** When logging a project, use this spreadsheet ID: {os.environ.get('PROJECT_SPREADSHEET_ID')}
- **Google Sheets Range:** When logging, you must use the range 'Sheet1!A1'.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(all_tools)

# --- Graph Nodes ---
def assistant_node(state: AgentState):
    """Invokes the LLM to decide the next action."""
    chain = prompt | llm_with_tools
    response = chain.invoke(state)
    return {"messages": [response]}

# --- Graph Definition ---
def build_graph():
    """Builds and compiles the agent's graph."""
    builder = StateGraph(AgentState)
    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile()

# --- Main Execution Loop ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "PROJECT_SPREADSHEET_ID"]
    if any(var not in os.environ for var in required_vars):
        print("Error: Missing one or more required environment variables.")
        print("Please create a .env file with: OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_USER_TOKEN, PROJECT_SPREADSHEET_ID")
        return

    print("✅ All environment variables found.")
    print("🤖 Project Kickoff Coordinator is ready.")
    print("---")
    
    graph = build_graph()
    conversation: List[BaseMessage] = []

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        conversation.append(HumanMessage(content=user_input))
        print("🤖 Assistant is thinking...")
        result = graph.invoke({"messages": conversation})
        final_response = result["messages"][-1]
        conversation.append(final_response)
        
        print(f"🤖 Assistant: {final_response.content}")
        print("---")

if __name__ == "__main__":
    main() 