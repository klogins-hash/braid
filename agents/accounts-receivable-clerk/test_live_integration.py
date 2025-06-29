#!/usr/bin/env python3
"""
Test script for live Xero integration in the Accounts Receivable Clerk.
This tests the actual API connections before running the full agent.
"""
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_xero_connection():
    """Test Xero API connection with live credentials."""
    print("🧪 Testing Xero API connection...")
    
    try:
        from xero_tools import check_xero_contact
        
        # Test with a simple contact search
        result = check_xero_contact.invoke({"name": "Test"})
        result_data = json.loads(result)
        
        if "data_source" in result_data and "REAL Xero API" in result_data["data_source"]:
            print("✅ Xero API connection successful!")
            print(f"   Response: {result_data.get('message', 'Contact search completed')}")
            return True
        else:
            print("⚠️ Xero API using fallback mode")
            return False
            
    except Exception as e:
        print(f"❌ Xero API test failed: {e}")
        return False

def test_contract_parsing():
    """Test contract data extraction with sample data."""
    print("🧪 Testing contract data extraction...")
    
    try:
        from contract_tools import extract_contract_data
        
        sample_contract = """
        Service Agreement between Acme Corp and Tech Solutions Inc.
        
        Services: Web development and consulting services
        Total contract value: $15,000
        Payment terms: Net 30 days
        Client contact: john@acmecorp.com
        
        This agreement is effective as of January 15, 2025.
        """
        
        result = extract_contract_data.invoke({
            "contract_text": sample_contract,
            "client_context": "Acme Corp"
        })
        
        result_data = json.loads(result)
        
        if result_data.get("confidence_score", 0) > 50:
            print("✅ Contract parsing successful!")
            print(f"   Client: {result_data.get('client_name')}")
            print(f"   Value: ${result_data.get('total_value', 0):,.2f}")
            print(f"   Confidence: {result_data.get('confidence_score')}%")
            return True
        else:
            print("⚠️ Contract parsing had low confidence")
            return False
            
    except Exception as e:
        print(f"❌ Contract parsing test failed: {e}")
        return False

def test_environment_setup():
    """Test that all required environment variables are set."""
    print("🧪 Testing environment configuration...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "XERO_ACCESS_TOKEN", 
        "XERO_TENANT_ID",
        "SLACK_BOT_TOKEN",
        "TWILIO_ACCOUNT_SID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables configured!")
        return True

def run_simple_agent_test():
    """Run a simple end-to-end test of the agent."""
    print("🧪 Testing basic agent functionality...")
    
    try:
        # Import agent components
        from agent import graph, ARClerkState
        from langchain_core.messages import HumanMessage
        
        if graph is None:
            print("❌ Agent graph not initialized")
            return False
        
        # Create a simple test state
        test_input = "Process new contract for Demo Client, $5,000 consulting services, Net 30 terms, contact: demo@client.com"
        
        initial_state = ARClerkState(
            messages=[HumanMessage(content=test_input)],
            contract_data={},
            client_info={},
            invoice_schedule=[],
            collection_status={},
            processed_files=[],
            current_action="monitoring",
            error_messages=[]
        )
        
        print(f"📝 Test input: {test_input}")
        
        # Run the agent with higher limit for demo testing
        result = graph.invoke(initial_state, {"recursion_limit": 20})
        
        # Check if we got contract data
        if result.get("contract_data") and result["contract_data"].get("client_name"):
            print("✅ Agent successfully processed contract!")
            print(f"   Client: {result['contract_data'].get('client_name')}")
            print(f"   Value: ${result['contract_data'].get('total_value', 0):,.2f}")
            
            # Check for errors
            if result.get("error_messages"):
                print(f"⚠️ Warnings: {len(result['error_messages'])} issues")
                for error in result["error_messages"][:3]:  # Show first 3
                    print(f"     - {error}")
            
            return True
        else:
            print("❌ Agent did not process contract successfully")
            if result.get("error_messages"):
                for error in result["error_messages"][:3]:
                    print(f"     Error: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting Accounts Receivable Clerk Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Contract Parsing", test_contract_parsing),
        ("Xero API Connection", test_xero_connection),
        ("Basic Agent Workflow", run_simple_agent_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent is ready for live demo.")
    elif passed >= total - 1:
        print("⚠️ Most tests passed. Agent should work with minor issues.")
    else:
        print("❌ Multiple test failures. Agent needs configuration fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)