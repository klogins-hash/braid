#!/usr/bin/env python3
"""
Comprehensive test script for the Financial Forecast Agent
Tests the complete 6-step workflow with real API integrations.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import FinancialForecastAgent
from src.database.database import DatabaseOperations

def setup_test_data():
    """Set up test client data in the database."""
    print("🔧 Setting up test data...")
    
    db = DatabaseOperations()
    
    # Create test client info
    test_client = {
        "user_id": "test_user_123",
        "company_name": "Test Tech Solutions",
        "industry": "Technology Services",
        "location": "San Francisco, CA",
        "founded_year": 2020,
        "employee_count": 25,
        "annual_revenue": 2500000,
        "business_model": "SaaS",
        "target_market": "Small to medium businesses",
        "competitive_advantages": ["AI-powered automation", "24/7 support", "Easy integration"]
    }
    
    try:
        # Store client info (this might fail if table doesn't exist, that's ok)
        db.store_client_info("test_user_123", test_client)
        print("✅ Test client data stored successfully")
    except Exception as e:
        print(f"⚠️ Could not store client data (database may not be initialized): {e}")
        print("   Agent will handle missing data gracefully")

def print_step_separator(step_num: int, step_name: str):
    """Print a visual separator for each step."""
    print(f"\n{'='*60}")
    print(f"🚀 STEP {step_num}: {step_name.upper()}")
    print(f"{'='*60}")

def test_agent_workflow():
    """Test the complete agent workflow."""
    print("🎯 Starting Full Agent Workflow Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup test data
    setup_test_data()
    
    print_step_separator(0, "Initializing Agent")
    
    try:
        # Initialize the agent
        agent = FinancialForecastAgent()
        print("✅ Agent initialized successfully")
        print(f"📊 Graph nodes: {list(agent.graph.get_graph().nodes)}")
        
        print_step_separator(1, "Running Complete Workflow")
        
        # Run the complete workflow
        user_id = "test_user_123"
        print(f"👤 Testing with user ID: {user_id}")
        
        start_time = time.time()
        result = agent.run_forecast(user_id)
        end_time = time.time()
        
        print_step_separator(2, "Workflow Results")
        
        print(f"⏱️ Total execution time: {end_time - start_time:.2f} seconds")
        print(f"📋 Final workflow state:")
        print(f"   Current Step: {result.get('current_step', 'unknown')}")
        print(f"   Workflow Complete: {result.get('workflow_complete', False)}")
        print(f"   Error: {result.get('error', 'None')}")
        
        # Print detailed results
        if result.get('xero_data'):
            print(f"💰 Xero Data: Retrieved {len(result['xero_data'])} records")
        
        if result.get('client_info'):
            print(f"🏢 Client Info: {result['client_info'].get('company_name', 'Unknown')}")
        
        if result.get('market_research'):
            research_length = len(result['market_research'])
            print(f"📈 Market Research: {research_length} characters of analysis")
        
        if result.get('forecast_assumptions'):
            assumptions = result['forecast_assumptions']
            print(f"📊 Forecast Assumptions:")
            for key, value in assumptions.items():
                if isinstance(value, str) and len(value) < 100:
                    print(f"   {key}: {value}")
        
        if result.get('forecast_results'):
            print(f"📈 Forecast Results: Generated successfully")
            
        if result.get('notion_report_url'):
            print(f"📄 Notion Report: {result['notion_report_url']}")
        
        # Print messages from the workflow
        if result.get('messages'):
            print_step_separator(3, "Workflow Messages")
            for i, msg in enumerate(result['messages'], 1):
                print(f"  {i}. {msg.content}")
        
        # Success/failure summary
        print_step_separator(4, "Test Summary")
        
        if result.get('workflow_complete'):
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("✅ All 6 steps executed without critical errors")
        else:
            print("⚠️ WORKFLOW INCOMPLETE")
            print(f"❌ Stopped at step: {result.get('current_step', 'unknown')}")
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
        
        return result
        
    except Exception as e:
        print_step_separator(99, "Critical Error")
        print(f"❌ Critical error during workflow execution:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        import traceback
        print(f"   Stack Trace:\n{traceback.format_exc()}")
        return None

def test_individual_components():
    """Test individual agent components."""
    print_step_separator(5, "Component Tests")
    
    try:
        agent = FinancialForecastAgent()
        
        # Test 1: Xero Tools
        print("🔧 Testing Xero integration...")
        try:
            xero_data = agent.xero.get_profit_and_loss()
            print(f"✅ Xero test: Retrieved {len(xero_data) if xero_data else 0} records")
        except Exception as e:
            print(f"❌ Xero test failed: {e}")
        
        # Test 2: Perplexity Tools
        print("🔧 Testing Perplexity integration...")
        try:
            research = agent.perplexity.conduct_market_research("Technology", "San Francisco")
            print(f"✅ Perplexity test: Retrieved {len(research)} characters")
        except Exception as e:
            print(f"❌ Perplexity test failed: {e}")
        
        # Test 3: Database
        print("🔧 Testing Database operations...")
        try:
            client_info = agent.db.get_client_info("test_user_123")
            print(f"✅ Database test: Retrieved client info: {bool(client_info)}")
        except Exception as e:
            print(f"❌ Database test failed: {e}")
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")

def main():
    """Main test execution."""
    print("🎯 FINANCIAL FORECAST AGENT - FULL TEST SUITE")
    print("=" * 60)
    
    # Test the complete workflow
    result = test_agent_workflow()
    
    # Test individual components
    test_individual_components()
    
    print_step_separator(99, "Final Summary")
    print(f"🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result and result.get('workflow_complete'):
        print("🎉 OVERALL TEST: SUCCESS")
        exit_code = 0
    else:
        print("⚠️ OVERALL TEST: PARTIAL SUCCESS OR FAILURE")
        exit_code = 1
    
    print("=" * 60)
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)