#!/usr/bin/env python3
"""
Test script for Project Kickoff Coordinator Agent
"""
import os
from dotenv import load_dotenv
from agent import build_graph
from langchain_core.messages import HumanMessage

def test_agent():
    """Test the agent with a sample project kickoff request."""
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "PROJECT_SPREADSHEET_ID"]
    if any(var not in os.environ for var in required_vars):
        print("Error: Missing one or more required environment variables.")
        print("Please ensure .env file has: OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_USER_TOKEN, PROJECT_SPREADSHEET_ID")
        return

    print("✅ All environment variables found.")
    print("🤖 Testing Project Kickoff Coordinator...")
    print("---")
    
    # Build the graph
    graph = build_graph()
    
    # Test message
    test_message = "kick off project 'Phoenix' with @alice and @bob. Schedule a 1-hour meeting for next Wednesday at 2 PM PST."
    
    print(f"📝 Test Input: {test_message}")
    print("🤖 Assistant is processing...")
    
    # Create the initial state
    initial_state = {"messages": [HumanMessage(content=test_message)]}
    
    try:
        # Run the agent
        result = graph.invoke(initial_state)
        
        # Get the final response
        final_response = result["messages"][-1]
        print(f"🤖 Assistant Response: {final_response.content}")
        
        # Print all tool calls if any
        if hasattr(final_response, 'tool_calls') and final_response.tool_calls:
            print("\n🔧 Tool calls made:")
            for i, tool_call in enumerate(final_response.tool_calls, 1):
                print(f"  {i}. {tool_call['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might be due to missing API keys or tool configuration issues.")

if __name__ == "__main__":
    test_agent()