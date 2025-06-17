"""
Recreated Project Kickoff Coordinator Agent
"""
import os
import logging
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# --- Local & Core Imports ---
# Import the tool aggregators that were copied locally by the CLI
from tools.gworkspace_tools import get_gworkspace_tools
from tools.slack_tools import get_slack_tools
# Import utility functions directly from the core library
from core.contrib.gworkspace.utils import get_current_date_context

# Load environment variables
load_dotenv()

# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# --- Tool Setup ---
# The CLI has already provided the tool files. Now we just aggregate them.
all_tools = get_gworkspace_tools() + get_slack_tools()
tool_node = ToolNode(all_tools)

# --- Model and Prompt Setup ---
system_prompt = f"""
You are an autonomous agent called the "Project Kickoff Coordinator."
Your job is to automate the entire kickoff process in a single, continuous workflow.

**Workflow:**
1.  **Find Users:** Use the `slack_find_user_by_name` tool to find the Slack ID for every person mentioned.
2.  **Get Emails:** Use the `slack_get_user_profile` tool with the user IDs to get their email addresses.
3.  **Create Event:** Use the `google_calendar_create_event` tool to schedule the meeting.
4.  **Log Project:** Use the `gsheets_append_row` tool to add a new row to the project tracker.
5.  **Notify:** Use `gmail_send_email` and `slack_post_message` to inform the team.

**CRITICAL INSTRUCTIONS:**
- Execute the workflow steps sequentially without asking for confirmation.
- If a tool fails, report the error and stop.
- Only provide a final summary message to the user after the entire workflow is complete.

**IMPORTANT CONTEXT:**
- **Current Date/Time:** {get_current_date_context()}
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

# --- Graph Definition ---
def agent_node(state: AgentState):
    """The 'assistant' node: invokes the LLM to decide the next action."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(AgentState)
builder.add_node("assistant", agent_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
graph = builder.compile()

# --- Main Execution Loop ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "PROJECT_SPREADSHEET_ID"]
    if any(var not in os.environ for var in required_vars):
        print("Error: Missing one or more required environment variables.")
        print("Please check your .env file.")
        return

    print("✅ All environment variables found.")
    print("🤖 Project Kickoff Coordinator is ready.")
    print("---")
    
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