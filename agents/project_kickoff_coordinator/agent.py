"""
Project Kickoff Coordinator Agent

This agent orchestrates the project kickoff process by coordinating actions
across Slack and Google Workspace.

**Workflow:**
1.  **Trigger:** A user mentions the bot in a designated Slack channel (C091GV5GBV2) with a kickoff request.
    Example: "@Braid kick off project 'Phoenix' with @alice and @bob. Schedule a 1-hour meeting for next Wednesday at 2 PM PST."
2.  **Information Gathering (Slack):**
    - Finds the user IDs for mentioned team members.
    - Retrieves their profiles to get their email addresses.
3.  **Scheduling (Google Calendar):**
    - Creates a calendar event for the kickoff meeting.
    - Adds the team members as attendees.
4.  **Logging (Google Sheets):**
    - Appends a new row to a project tracking spreadsheet with kickoff details.
5.  **Confirmation (Gmail & Slack):**
    - Sends a confirmation email to all participants with the meeting details.
    - Posts a confirmation message in the originating Slack channel.
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

# Import all the tools from our contrib modules
from core.contrib.slack.slack_tools import get_slack_tools
from core.contrib.gworkspace.google_calendar_tools import get_google_calendar_tools, get_current_date_context
from core.contrib.gworkspace.gmail_tools import get_gmail_tools
from core.contrib.gworkspace.gsheets_tools import get_gsheets_tools

# Load environment variables from .env file before anything else
load_dotenv()

# --- Agent State ---
# MessagesState is a pre-built class that automatically handles
# appending messages to the state.
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# --- Tool Setup ---
# Aggregate all tools from different modules into a single list.
# This makes them all available to the agent's LLM.
slack_tools = get_slack_tools()
gcal_tools = get_google_calendar_tools()
gmail_tools = get_gmail_tools()
gsheets_tools = get_gsheets_tools()

all_tools = slack_tools + gcal_tools + gmail_tools + gsheets_tools

# A pre-built LangGraph node that executes the tools based on the
# LLM's `tool_calls` attribute.
tool_node = ToolNode(all_tools)

# --- Model and Prompt Setup ---
# We use a system prompt to give the agent its persona, instructions,
# and any contextual information it needs, like the current date.
# This is crucial for tools that rely on accurate date/time information.
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

# Create the ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Initialize the LLM and bind the tools to it.
# Binding tools makes the LLM "tool-aware," allowing it to decide when to call them.
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(all_tools)

# --- Graph Nodes ---
# Each node in the graph is a function that takes the current state
# and returns a dictionary with updates to that state.

def assistant_node(state: AgentState):
    """The 'assistant' node: invokes the LLM to decide the next action."""
    chain = prompt | llm_with_tools
    response = chain.invoke(state)
    return {"messages": [response]}

# --- Graph Definition ---
def build_graph():
    """Builds and compiles the agent's graph."""
    builder = StateGraph(AgentState)

    # Add the assistant and tool nodes to the graph
    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tool_node)

    # The graph starts with the assistant node
    builder.add_edge(START, "assistant")

    # The conditional edge decides the next step after the assistant runs.
    # - If the LLM output contains `tool_calls`, it routes to the `tools` node.
    # - Otherwise, it means the agent is done, and it routes to `END`.
    builder.add_conditional_edges("assistant", tools_condition)

    # After the tools are executed, the graph loops back to the assistant node
    # so the LLM can process the tool results and decide the next step.
    builder.add_edge("tools", "assistant")

    # Compile the graph into a runnable object
    return builder.compile()

# --- Main Execution Loop ---
def main():
    """
    Sets up and runs the Project Kickoff Coordinator agent.
    
    This function initializes the agent and enters a loop to process user input.
    It simulates a conversation, where each user input is a new kickoff request.
    """
    # Configure logging to show info-level messages
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "PROJECT_SPREADSHEET_ID"]
    if any(var not in os.environ for var in required_vars):
        print("Error: Missing one or more required environment variables.")
        print("Please create a .env file with: OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_USER_TOKEN, PROJECT_SPREADSHEET_ID")
        return

    print("✅ All environment variables found.")
    print("🤖 Project Kickoff Coordinator is ready.")
    print("---")
    
    graph = build_graph()
    
    # The conversation history is stored in a list of messages.
    conversation: List[BaseMessage] = []

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        # Add the user's message to the conversation history
        conversation.append(HumanMessage(content=user_input))

        # Invoke the graph with the current conversation state
        print("🤖 Assistant is thinking...")
        result = graph.invoke({"messages": conversation})
        
        # The final response from the agent is the last message in the state
        final_response = result["messages"][-1]
        
        # Add the agent's final response to the conversation history
        conversation.append(final_response)
        
        print(f"🤖 Assistant: {final_response.content}")
        print("---")

if __name__ == "__main__":
    # To run this agent, you'll need a .env file in the root directory
    # with your API keys and the Google Sheet ID.
    main() 