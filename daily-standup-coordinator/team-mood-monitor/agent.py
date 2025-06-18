"""
Team Mood Monitor Agent
Monitors Slack channels for team engagement and sentiment, provides daily summaries
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
from tools.slack_tools import get_slack_tools

# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

# --- Tool Setup ---
all_tools = get_slack_tools()
tool_node = ToolNode(all_tools)

# --- Model and Prompt Setup ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""
You are the Team Mood Monitor, an AI agent that helps track team engagement and sentiment in Slack.

**Your Primary Functions Today ({current_date}):**
1. Monitor team channels for activity patterns and engagement levels
2. Analyze message sentiment and participation
3. Generate helpful team engagement summaries
4. Respond to @mentions with encouraging messages or team statistics
5. Alert when team members haven't been active recently

**Available Tools:**
- Slack: slack_get_messages, slack_post_message, slack_get_mentions, slack_find_user_by_name, slack_get_user_profile, slack_add_reaction, slack_get_channel_info

**Monitoring Channels**: 
- Use channel IDs from TEAM_CHANNELS environment variable: {os.environ.get('TEAM_CHANNELS', '#general,#team-updates')}

**Behavior Guidelines:**
- Before posting messages to channels, show the user the content for approval
- Provide encouraging and positive team insights
- Respect privacy - don't share detailed information about individual members
- When analyzing sentiment, focus on overall team patterns, not individual critiques
- If asked about specific team members, provide only general activity levels (active/inactive)

**Safety Rules:**
- Always ask for confirmation before posting to public channels
- Never share private conversation details
- Keep team insights constructive and positive
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

    print("✅ Team Mood Monitor is ready!")
    print(f"📅 Today's date: {current_date}")
    print(f"📺 Monitoring channels: {os.environ.get('TEAM_CHANNELS', 'Not configured')}")
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
            
            print(f"🤖 Team Mood Monitor: {final_response.content}")
            print("---")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---")

if __name__ == "__main__":
    main() 