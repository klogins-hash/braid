"""
Test script for the Autonomous Accounts Receivable Clerk
Verifies core functionality and integration points.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tool_imports():
    """Test that all specialized tools can be imported."""
    print("🔧 Testing tool imports...")
    
    try:
        from xero_tools import get_xero_ar_tools
        xero_tools = get_xero_ar_tools()
        print(f"✅ Xero AR tools: {len(xero_tools)} tools loaded")
        
        from contract_tools import get_contract_tools
        contract_tools = get_contract_tools()
        print(f"✅ Contract tools: {len(contract_tools)} tools loaded")
        
        from collections_tools import get_collections_tools
        collections_tools = get_collections_tools()
        print(f"✅ Collections tools: {len(collections_tools)} tools loaded")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_contract_extraction():
    """Test contract data extraction functionality."""
    print("\n📄 Testing contract extraction...")
    
    try:
        from contract_tools import extract_contract_data
        
        sample_contract = """
        Service Agreement between TechCorp Solutions and ABC Consulting.
        
        Services: Custom web application development including frontend, backend, and database design.
        Total Contract Value: $25,000
        Payment Terms: 50% upfront ($12,500), 50% upon completion ($12,500)
        Contact: billing@techcorp.com
        Start Date: January 15, 2025
        """
        
        result = extract_contract_data.invoke({
            "contract_text": sample_contract,
            "client_context": "TechCorp Solutions"
        })
        
        print("✅ Contract extraction completed")
        print(f"   Result length: {len(result)} characters")
        
        # Parse and validate result
        import json
        parsed_result = json.loads(result)
        
        if parsed_result.get("client_name") and parsed_result.get("total_value") > 0:
            print(f"   Client: {parsed_result['client_name']}")
            print(f"   Value: ${parsed_result['total_value']:,.2f}")
            print(f"   Terms: {parsed_result['billing_terms']}")
            return True
        else:
            print("⚠️ Contract extraction returned incomplete data")
            return False
            
    except Exception as e:
        print(f"❌ Contract extraction error: {e}")
        return False

def test_xero_connectivity():
    """Test Xero API connectivity (with fallback)."""
    print("\n🏦 Testing Xero connectivity...")
    
    try:
        from xero_tools import check_xero_contact
        
        # Test with a sample contact search
        result = check_xero_contact.invoke({"name": "Test Client"})
        
        print("✅ Xero contact check completed")
        
        # Parse result
        import json
        parsed_result = json.loads(result)
        
        if "data_source" in parsed_result:
            data_source = parsed_result["data_source"]
            if "REAL Xero API" in data_source:
                print("   🟢 Real Xero API connection verified")
            else:
                print("   🟡 Using Xero API fallback (normal for testing)")
            return True
        else:
            print("⚠️ Unexpected Xero response format")
            return False
            
    except Exception as e:
        print(f"❌ Xero connectivity error: {e}")
        return False

def test_collections_tools():
    """Test collections and communication tools."""
    print("\n📧 Testing collections tools...")
    
    try:
        from collections_tools import send_collection_email
        
        # Test email generation
        result = send_collection_email.invoke({
            "client_name": "Test Client Corp",
            "contact_email": "test@example.com",
            "invoice_number": "INV-TEST-001",
            "amount_due": 5000.00,
            "days_overdue": 15,
            "stage": "stage_1"
        })
        
        print("✅ Collection email tool completed")
        
        # Parse result
        import json
        parsed_result = json.loads(result)
        
        if parsed_result.get("status") and parsed_result.get("subject"):
            print(f"   Status: {parsed_result['status']}")
            print(f"   Subject: {parsed_result['subject'][:50]}...")
            return True
        else:
            print("⚠️ Collection email returned incomplete data")
            return False
            
    except Exception as e:
        print(f"❌ Collections tools error: {e}")
        return False

def test_agent_initialization():
    """Test that the main agent can be initialized."""
    print("\n🤖 Testing agent initialization...")
    
    try:
        # Add current directory to path for imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from agent import create_ar_clerk_agent, ARClerkState
        
        # Create the agent graph
        graph = create_ar_clerk_agent()
        
        print("✅ AR Clerk agent initialized successfully")
        print(f"   Graph type: {type(graph)}")
        
        # Test state structure
        sample_state = ARClerkState(
            messages=[],
            contract_data={},
            client_info={},
            invoice_schedule=[],
            collection_status={},
            processed_files=[],
            current_action="monitoring",
            error_messages=[]
        )
        
        print("✅ Agent state structure validated")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False

def test_environment_setup():
    """Test environment variable configuration."""
    print("\n⚙️ Testing environment setup...")
    
    required_vars = ["OPENAI_API_KEY"]
    recommended_vars = ["XERO_ACCESS_TOKEN", "XERO_TENANT_ID", "PERPLEXITY_API_KEY"]
    optional_vars = ["SLACK_BOT_TOKEN", "TWILIO_ACCOUNT_SID"]
    
    missing_required = []
    missing_recommended = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} configured")
    
    for var in recommended_vars:
        if not os.getenv(var):
            missing_recommended.append(var)
        else:
            print(f"✅ {var} configured")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} configured (optional)")
        else:
            print(f"⚪ {var} not configured (optional)")
    
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    if missing_recommended:
        print(f"⚠️ Missing recommended variables: {', '.join(missing_recommended)}")
        print("   Agent will use fallback modes for missing integrations")
    
    return True

def main():
    """Run all tests and provide summary."""
    print("🧪 AUTONOMOUS ACCOUNTS RECEIVABLE CLERK - TEST SUITE")
    print("=" * 60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Tool Imports", test_tool_imports),
        ("Contract Extraction", test_contract_extraction),
        ("Xero Connectivity", test_xero_connectivity),
        ("Collections Tools", test_collections_tools),
        ("Agent Initialization", test_agent_initialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The AR Clerk is ready for use.")
        print("\nTo start the agent:")
        print("   python agent.py")
    elif passed >= total * 0.8:
        print("\n⚠️ Most tests passed. Agent should work with some limitations.")
        print("   Check failed tests and configure missing environment variables.")
    else:
        print("\n❌ Multiple test failures. Please review configuration and dependencies.")
        print("   Check .env.template for required environment variables.")
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()