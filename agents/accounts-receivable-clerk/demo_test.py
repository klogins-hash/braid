"""
Demo test for the Autonomous Accounts Receivable Clerk
Tests the complete workflow with a sample contract.
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_complete_workflow():
    """Test the complete AR workflow with a sample contract."""
    print("🧪 TESTING COMPLETE AR WORKFLOW")
    print("=" * 50)
    
    # Import the standalone agent
    from standalone_agent import create_ar_clerk_agent, ARClerkState
    from langchain_core.messages import HumanMessage
    
    # Create the agent graph
    try:
        graph = create_ar_clerk_agent()
        print("✅ Agent graph created successfully")
    except Exception as e:
        print(f"❌ Failed to create agent graph: {e}")
        return False
    
    # Sample contract for testing
    sample_contract = """
    New Service Agreement for TechCorp Solutions
    
    Client: ABC Manufacturing Inc.
    Contact: billing@abcmanufacturing.com
    Service: Custom inventory management system development
    Total Contract Value: $45,000
    Payment Terms: 50% upfront ($22,500), 50% upon completion ($22,500)
    Start Date: January 15, 2025
    Expected Completion: March 30, 2025
    
    Please process this contract and set up billing.
    """
    
    print("\n📄 TESTING CONTRACT:")
    print(sample_contract.strip())
    
    try:
        # Create initial state
        initial_state = ARClerkState(
            messages=[HumanMessage(content=sample_contract)],
            contract_data={},
            client_info={},
            invoice_schedule=[],
            collection_status={},
            processed_files=[],
            current_action="processing",
            error_messages=[]
        )
        
        print("\n🤖 RUNNING AR WORKFLOW...")
        print("-" * 30)
        
        # Run the workflow
        result = graph.invoke(initial_state, {"recursion_limit": 10})
        
        # Display results
        print("\n📊 WORKFLOW RESULTS:")
        print("-" * 30)
        
        final_message = result["messages"][-1]
        print(f"🤖 Final Response: {final_message.content}")
        
        # Count tool executions
        tool_messages = [msg for msg in result["messages"] if hasattr(msg, 'tool_call_id')]
        print(f"\n📈 Workflow Statistics:")
        print(f"   - Total messages: {len(result['messages'])}")
        print(f"   - Tool executions: {len(tool_messages)}")
        print(f"   - Error messages: {len(result.get('error_messages', []))}")
        
        if result.get("error_messages"):
            print("\n⚠️ Issues encountered:")
            for error in result["error_messages"]:
                print(f"  - {error}")
        
        print("\n✅ Workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        return False

def test_payment_monitoring():
    """Test payment monitoring and collections workflow."""
    print("\n\n🧪 TESTING PAYMENT MONITORING")
    print("=" * 50)
    
    from standalone_agent import create_ar_clerk_agent, ARClerkState
    from langchain_core.messages import HumanMessage
    
    graph = create_ar_clerk_agent()
    
    payment_request = """
    Check payment status for all outstanding invoices and initiate collections 
    for any accounts that are overdue.
    """
    
    print(f"📋 Request: {payment_request.strip()}")
    
    try:
        initial_state = ARClerkState(
            messages=[HumanMessage(content=payment_request)],
            contract_data={},
            client_info={},
            invoice_schedule=[],
            collection_status={},
            processed_files=[],
            current_action="monitoring",
            error_messages=[]
        )
        
        print("\n🤖 RUNNING PAYMENT MONITORING...")
        print("-" * 30)
        
        result = graph.invoke(initial_state, {"recursion_limit": 8})
        
        final_message = result["messages"][-1]
        print(f"\n💰 Payment Status: {final_message.content}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Payment monitoring failed: {e}")
        return False

def main():
    """Run all demo tests."""
    print(f"🚀 AR CLERK DEMO STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please configure your .env file.")
        return
    
    tests = [
        ("Complete AR Workflow", test_complete_workflow),
        ("Payment Monitoring", test_payment_monitoring),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} demos passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All demos passed! The AR Clerk is working correctly.")
    else:
        print("\n⚠️ Some demos failed. Check the output above for details.")
    
    print(f"\nDemo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()