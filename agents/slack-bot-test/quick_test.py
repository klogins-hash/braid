"""Quick test of the generated agent"""
from agent import graph
from langchain_core.messages import HumanMessage

def test():
    try:
        result = graph.invoke({"messages": [HumanMessage(content="Hello! What tools do you have?")]})
        response = result["messages"][-1]
        print(f"✅ Agent Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing newly generated agent...")
    success = test()
    print("🎉 Success!" if success else "💥 Failed!")