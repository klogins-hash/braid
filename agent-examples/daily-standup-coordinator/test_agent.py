"""
Test script for the Daily Standup Coordinator Agent
"""
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Import the agent components
from agent import graph

def test_basic_functionality():
    """Test basic agent functionality with a simple query."""
    print("🧪 Testing Daily Standup Coordinator Agent...")
    print("=" * 50)
    
    # Test 1: Ask about today's meetings
    print("\n📋 Test 1: Ask about today's meetings")
    test_message = "Can you check what meetings I have today and post a summary to the team channel?"
    
    try:
        print(f"📤 Sending: {test_message}")
        initial_state = {"messages": [HumanMessage(content=test_message)]}
        print(f"🔍 Initial state: {initial_state}")
        result = graph.invoke(initial_state)
        print(f"📥 Full result: {result}")
        response = result["messages"][-1]
        print(f"✅ Agent Response: {response.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Check available tools
    print("\n🔧 Test 2: Check available tools")
    test_message2 = "What tools do you have available?"
    
    try:
        result = graph.invoke({"messages": [HumanMessage(content=test_message2)]})
        response = result["messages"][-1]
        print(f"✅ Agent Response: {response.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
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
    
    if missing_vars:
        print(f"❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    return True

if __name__ == "__main__":
    if not check_environment():
        print("❌ Environment check failed. Please set up your .env file.")
        sys.exit(1)
    
    print("✅ Environment check passed!")
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)