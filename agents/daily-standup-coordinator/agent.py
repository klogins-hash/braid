"""
Daily Team Standup Coordinator Agent
Automatically checks calendar for today's meetings and posts summaries to Slack
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
from tools.gworkspace_tools import get_gworkspace_tools
from tools.slack_tools import get_slack_tools

# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# --- Tool Setup ---
all_tools = get_gworkspace_tools() + get_slack_tools()
tool_node = ToolNode(all_tools)

# --- Model and Prompt Setup ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""
You are the Daily Team Standup Coordinator, an autonomous agent that helps teams stay organized.

**Your Primary Task Today ({current_date}):**
1. When asked to check today's meetings, look for team meetings scheduled for today
2. For each meeting found, gather the attendee information  
3. Post a summary to the #team-updates Slack channel (use channel ID: {os.environ.get('TEAM_UPDATES_CHANNEL_ID', 'C024BE91L')})

**Available Tools:**
- Google Calendar: google_calendar_list_events (READ existing events), google_calendar_create_event (CREATE new events)
- Gmail: gmail_send_email
- Google Sheets: gsheets_append_row
- Slack: slack_post_message, slack_find_user_by_name, slack_get_user_profile, and others

**Enhanced Workflow:**
1. Use google_calendar_list_events to find today's meetings
2. For each meeting, gather attendee information
3. Create a formatted summary including meeting titles, times, and attendees
4. Post the summary to the team Slack channel

**Rules:**
- Before posting to Slack, always confirm the message content with the user
- Be helpful and explain what you CAN do, even when limitations exist
- Suggest workarounds when tools are missing
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(all_tools)

# --- Graph Definition ---
def agent_node(state: AgentState):
    """The assistant node: invokes the LLM to decide the next action."""
    # Extract messages from state and format with system prompt
    messages = prompt.format_messages(messages=state["messages"])
    response = llm_with_tools.invoke(messages)
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
    """Interactive conversation loop for testing the agent."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return

    print("✅ Daily Team Standup Coordinator is ready!")
    print(f"📅 Today's date: {current_date}")
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