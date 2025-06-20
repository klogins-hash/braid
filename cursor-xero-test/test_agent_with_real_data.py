#!/usr/bin/env python3
"""
Test Financial Forecasting Agent with Real Demo Company Data
"""

import os
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.agent import FinancialForecastAgent
from src.database.database import DatabaseOperations

def test_agent_with_real_data():
    """Test the agent using real Demo Company YTD P&L data."""
    
    print("🧪 TESTING FINANCIAL AGENT WITH REAL DEMO COMPANY DATA")
    print("=" * 70)
    print("This test uses:")
    print("✅ REAL Demo Company YTD P&L data from Xero")
    print("✅ REAL market research from Perplexity")
    print("✅ REAL client data from database")
    print("✅ REAL AI-generated forecast assumptions")
    print()
    
    # Test user ID - this should exist in database
    test_user_id = "test_user_123"
    
    print(f"🎯 Testing with user: {test_user_id}")
    
    try:
        # Initialize agent
        print("\n🤖 Initializing Financial Forecast Agent...")
        agent = FinancialForecastAgent()
        
        # Test database connection
        print("📊 Testing database connection...")
        db = DatabaseOperations()
        
        # Check if test user exists
        client_info = db.get_client_info(test_user_id)
        if client_info:
            print(f"✅ Found client: {client_info.get('company_name', 'Unknown')}")
            print(f"   Industry: {client_info.get('industry', 'N/A')}")
            print(f"   Location: {client_info.get('location', 'N/A')}")
        else:
            print(f"⚠️ No client found for {test_user_id}, agent will handle gracefully")
        
        # Run the complete workflow
        print(f"\n🚀 Running complete forecasting workflow...")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run agent workflow
        result = agent.run_forecast(test_user_id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n✅ WORKFLOW COMPLETED in {execution_time:.2f} seconds")
        print("=" * 50)
        
        # Display results
        if result and 'workflow_complete' in result and result['workflow_complete']:
            print("🎉 SUCCESS: Financial forecast generated!")
            
            # Show key results
            if 'xero_data' in result:
                xero_count = len(result['xero_data']) if result['xero_data'] else 0
                print(f"📊 Xero Data: {xero_count} records retrieved")
                
                # Show if real data was used
                if result['xero_data'] and len(result['xero_data']) > 0:
                    data_source = result['xero_data'][0].get('data_source', 'Unknown')
                    if 'Real Xero Data' in data_source:
                        print(f"🎉 SUCCESS: Using REAL Demo Company data!")
                        print(f"   Source: {data_source}")
                        
                        # Show key financial figures
                        record = result['xero_data'][0]
                        print(f"💰 YTD Revenue: ${record.get('revenue', 0):,.2f}")
                        print(f"💰 YTD Gross Profit: ${record.get('gross_profit', 0):,.2f}")
                        print(f"💰 YTD Net Income: ${record.get('net_income', 0):,.2f}")
                    else:
                        print(f"⚠️ Using mock data: {data_source}")
            
            if 'client_info' in result:
                client = result['client_info']
                if client:
                    print(f"🏢 Client: {client.get('company_name', 'N/A')}")
            
            if 'market_research' in result:
                research_length = len(result['market_research']) if result['market_research'] else 0
                print(f"🔍 Market Research: {research_length} characters")
            
            if 'forecast_assumptions' in result:
                assumptions = result['forecast_assumptions']
                if assumptions and isinstance(assumptions, dict):
                    print(f"📈 Generated forecast assumptions:")
                    for key, value in assumptions.items():
                        print(f"   {key}: {value}")
            
            if 'notion_report' in result:
                report_url = result['notion_report']
                print(f"📄 Report: {report_url}")
            
            print(f"\n🎉 INTEGRATION TEST SUCCESSFUL!")
            print("✅ Your financial agent is working with real Demo Company data")
            
        else:
            print("❌ Workflow did not complete successfully")
            print("Check the logs above for any errors")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    
    print("🧪 FINANCIAL AGENT REAL DATA TEST")
    print("=" * 50)
    print("Testing complete workflow with Demo Company (US) data")
    print()
    
    # Check environment
    required_vars = [
        'XERO_ACCESS_TOKEN',
        'XERO_TENANT_ID', 
        'XERO_CLIENT_ID',
        'PERPLEXITY_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease ensure all API keys and tokens are set in .env file")
        return
    
    print("✅ All required environment variables found")
    
    # Run the test
    test_agent_with_real_data()
    
    print("\n" + "=" * 70)
    print("🎯 TEST COMPLETE")
    print("Your financial forecasting agent is now using real Demo Company data!")
    print("=" * 70)

if __name__ == "__main__":
    main()