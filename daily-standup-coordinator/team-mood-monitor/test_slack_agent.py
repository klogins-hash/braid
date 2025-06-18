"""
Test script for the Team Mood Monitor Agent
"""
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Import the agent components
from agent import graph

def test_slack_functionality():
    """Test Slack agent functionality with various queries."""
    print("🧪 Testing Team Mood Monitor Agent...")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Basic Agent Response",
            "message": "Hello! What can you help me with?"
        },
        {
            "name": "Check Available Tools",
            "message": "What Slack tools do you have available?"
        },
        {
            "name": "Channel Monitoring Request",
            "message": "Can you check the recent activity in our team channels?"
        },
        {
            "name": "Team Engagement Analysis",
            "message": "Analyze the team engagement level from recent Slack messages and give me a summary."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"📤 Sending: {test_case['message']}")
        
        try:
            initial_state = {"messages": [HumanMessage(content=test_case['message'])]}
            result = graph.invoke(initial_state)
            response = result["messages"][-1]
            
            print(f"✅ Response: {response.content}")
            
            # Check if agent used any tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Tools used: {[tool_call['name'] for tool_call in response.tool_calls]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("-" * 40)
    
    print("\n✨ All tests completed!")
    return True

def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = ["OPENAI_API_KEY", "SLACK_BOT_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    # Check optional vars
    optional_vars = ["SLACK_USER_TOKEN", "TEAM_CHANNELS"]
    for var in optional_vars:
        if var in os.environ:
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    if missing_vars:
        print(f"❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    return True

if __name__ == "__main__":
    if not check_environment():
        print("❌ Environment check failed. Please set up your .env file.")
        sys.exit(1)
    
    print("✅ Environment check passed!")
    success = test_slack_functionality()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)