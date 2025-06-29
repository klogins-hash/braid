"""
Simple setup test for Mural Content Assistant
Tests each component individually to identify any issues
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment
load_dotenv(override=True)

def test_environment():
    """Test environment variable setup."""
    print("🔧 Testing Environment Setup")
    print("=" * 40)
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API access",
        "MURAL_ACCESS_TOKEN": "Mural API access", 
        "MURAL_CLIENT_ID": "Mural OAuth client ID",
        "MURAL_CLIENT_SECRET": "Mural OAuth client secret"
    }
    
    optional_vars = {
        "MURAL_DEFAULT_WORKSPACE_ID": "Default workspace for murals",
        "MURAL_DEFAULT_ROOM_ID": "Default room for murals"
    }
    
    print("Required Variables:")
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            masked = f"{'*' * 8}...{value[-4:]}" if len(value) > 8 else "****"
            print(f"  ✅ {var}: {masked} ({description})")
        else:
            print(f"  ❌ {var}: Not set ({description})")
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked = f"{'*' * 8}...{value[-4:]}" if len(value) > 8 else "****"
            print(f"  ✅ {var}: {masked} ({description})")
        else:
            print(f"  ⚠️  {var}: Not set ({description})")
    
    return bool(os.environ.get("MURAL_ACCESS_TOKEN"))

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing Module Imports")
    print("=" * 40)
    
    imports_to_test = [
        ("langchain_core.messages", "LangChain core"),
        ("langchain_openai", "OpenAI integration"),
        ("langgraph.graph", "LangGraph"),
        ("requests", "HTTP requests"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment loading")
    ]
    
    all_good = True
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"  ❌ {module_name}: Failed - {e}")
            all_good = False
    
    return all_good

def test_mural_tools():
    """Test Mural tools import and basic functionality."""
    print("\n🛠️  Testing Mural Tools")
    print("=" * 40)
    
    try:
        # Add current directory to path
        sys.path.append(os.path.dirname(__file__))
        from mural_tools import get_mural_tools
        
        tools = get_mural_tools()
        print(f"✅ Successfully imported {len(tools)} Mural tools:")
        
        for tool in tools:
            print(f"  • {tool.name}: {tool.description[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import Mural tools: {e}")
        return False

def test_mural_api():
    """Test actual Mural API connectivity."""
    print("\n🎨 Testing Mural API Connectivity")
    print("=" * 40)
    
    if not os.environ.get("MURAL_ACCESS_TOKEN"):
        print("⚠️  No MURAL_ACCESS_TOKEN found - skipping API test")
        print("💡 Run oauth_setup.py to get your access token")
        return False
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from mural_tools import get_workspaces
        
        result = get_workspaces.invoke({})
        result_data = json.loads(result)
        
        if 'error' in result_data:
            print(f"❌ Mural API error: {result_data['message']}")
            print(f"🔍 Data source: {result_data.get('data_source', 'unknown')}")
            
            if "scope" in result_data['message'].lower():
                print("💡 Solution: Your access token needs these scopes:")
                print("   - murals:read")
                print("   - murals:write") 
                print("   - users:read")
                print("   Re-run oauth_setup.py to get a token with correct scopes")
            
            return False
        else:
            print(f"✅ Mural API working! Data source: {result_data.get('data_source', 'unknown')}")
            
            if 'value' in result_data:
                workspaces = result_data['value']
                print(f"📊 Found {len(workspaces)} workspaces")
                for ws in workspaces[:2]:
                    print(f"  • {ws.get('name', 'Unknown')} (ID: {ws.get('id', 'unknown')[:8]}...)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing Mural API: {e}")
        return False

def test_openai():
    """Test OpenAI API connectivity."""
    print("\n🤖 Testing OpenAI API")
    print("=" * 40)
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  No OPENAI_API_KEY found - skipping OpenAI test")
        return False
    
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Simple test message
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content="Hello! Just say 'API working' to confirm.")])
        
        print(f"✅ OpenAI API working! Response: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        if "invalid_api_key" in str(e):
            print("💡 Check your OPENAI_API_KEY in the .env file")
        return False

def main():
    """Run all tests and provide recommendations."""
    print("🎨 Mural Content Assistant - Setup Test")
    print("=" * 50)
    
    # Run tests
    env_ok = test_environment()
    imports_ok = test_imports()
    tools_ok = test_mural_tools()
    mural_api_ok = test_mural_api()
    openai_ok = test_openai()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 40)
    
    results = [
        ("Environment", env_ok),
        ("Imports", imports_ok), 
        ("Mural Tools", tools_ok),
        ("Mural API", mural_api_ok),
        ("OpenAI API", openai_ok)
    ]
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Recommendations
    print("\n💡 Next Steps:")
    if not env_ok:
        print("1. Configure your .env file with required credentials")
    if not mural_api_ok:
        print("2. Run: python oauth_setup.py (for Mural API access)")
    if not openai_ok:
        print("3. Add valid OPENAI_API_KEY to .env")
    
    if all([imports_ok, tools_ok]):
        if mural_api_ok and openai_ok:
            print("🎉 Everything looks good! Try: python agent.py")
        else:
            print("🔧 Fix the API issues above, then try: python agent.py")
    else:
        print("🔧 Fix import/tool issues first")
    
    print("\n📚 Helpful Commands:")
    print("  python oauth_setup.py        # Get Mural access token")
    print("  python get_workspace_info.py # Set default workspace/room")
    print("  python agent.py              # Run the agent")

if __name__ == "__main__":
    main()