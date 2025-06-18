"""
Test if the existing working agent actually works
"""
import sys
import os

# Add the parent directory to path to access agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage

def test_existing_agent():
    """Test the existing recreated_kickoff_agent to see if it works."""
    try:
        # Import the working agent
        from agents.recreated_kickoff_agent.agent import graph
        
        print("🧪 Testing existing working agent...")
        
        test_message = "Hello, what can you do?"
        result = graph.invoke({"messages": [HumanMessage(content=test_message)]})
        response = result["messages"][-1]
        print(f"✅ Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_existing_agent()