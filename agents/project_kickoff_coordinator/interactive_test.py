#!/usr/bin/env python3
"""
Interactive test script for Project Kickoff Coordinator Agent
This script allows you to test the agent with real Slack users and workspace.
"""
import os
from dotenv import load_dotenv
from agent import build_graph
from langchain_core.messages import HumanMessage

def interactive_test():
    """Interactive test of the agent with real workspace integration."""
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "PROJECT_SPREADSHEET_ID"]
    if any(var not in os.environ for var in required_vars):
        print("❌ Error: Missing one or more required environment variables.")
        print("Please ensure .env file has: OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_USER_TOKEN, PROJECT_SPREADSHEET_ID")
        return

    print("✅ All environment variables found.")
    print("🤖 Project Kickoff Coordinator - Interactive Test")
    print("=" * 50)
    print("This will test the agent with your real Slack workspace and Google services.")
    print("Make sure you have:")
    print("- Valid Slack bot and user tokens")
    print("- Google credentials configured")
    print("- A valid Google Sheets ID for project tracking")
    print("=" * 50)
    
    # Build the graph
    graph = build_graph()
    
    print("\n📝 Example requests you can try:")
    print("1. 'kick off project Phoenix with @username1 and @username2. Schedule a 1-hour meeting for tomorrow at 2 PM PST.'")
    print("2. 'start project Alpha with the marketing team. Set up kickoff meeting for next Monday at 10 AM.'")
    print("3. Type 'quit' to exit")
    print()
    
    conversation = []
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            print("🤖 Assistant is processing...")
            
            # Add user message to conversation
            conversation.append(HumanMessage(content=user_input))
            
            # Create state with full conversation
            state = {"messages": conversation}
            
            # Run the agent
            result = graph.invoke(state)
            
            # Get the final response
            final_response = result["messages"][-1]
            
            # Update conversation with all new messages
            conversation = result["messages"]
            
            print(f"🤖 Assistant: {final_response.content}")
            
            # Show tool calls if any were made
            if hasattr(final_response, 'tool_calls') and final_response.tool_calls:
                print("\n🔧 Tools used in this response:")
                for i, tool_call in enumerate(final_response.tool_calls, 1):
                    print(f"  {i}. {tool_call['name']}: {tool_call.get('args', {})}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("This might be due to API connectivity or configuration issues.")
            print("-" * 50)

if __name__ == "__main__":
    interactive_test()