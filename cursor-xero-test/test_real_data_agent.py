#!/usr/bin/env python3
"""
Test Financial Forecasting Agent with Fresh Real Demo Company Data
"""

import sys
sys.path.append('src')

import os
from dotenv import load_dotenv

# Force reload environment
load_dotenv(override=True)

from src.agent import FinancialForecastAgent

def test_with_fresh_env():
    """Test the agent with fresh environment."""
    
    print("🧪 TESTING AGENT WITH FRESH REAL DEMO COMPANY DATA")
    print("=" * 70)
    
    # Verify tokens are fresh
    access_token = os.getenv('XERO_ACCESS_TOKEN')
    tenant_id = os.getenv('XERO_TENANT_ID')
    
    print(f"🔑 Token: {access_token[:20] if access_token else 'NOT_SET'}...")
    print(f"🏢 Tenant: {tenant_id}")
    
    if not access_token or not tenant_id:
        print("❌ Missing Xero credentials")
        return
    
    print("\n🤖 Initializing agent with fresh environment...")
    
    # Create fresh agent instance
    agent = FinancialForecastAgent()
    
    # Test user
    test_user_id = "test_user_123"
    
    print(f"🎯 Running forecast for user: {test_user_id}")
    print("-" * 50)
    
    try:
        # Run the workflow
        result = agent.run_forecast(test_user_id)
        
        print(f"\n✅ WORKFLOW COMPLETED")
        print("=" * 50)
        
        # Check the results
        if result and 'xero_data' in result and result['xero_data']:
            xero_data = result['xero_data'][0]
            data_source = xero_data.get('data_source', 'Unknown')
            
            print(f"📊 Xero Data Source: {data_source}")
            
            if "Real Xero Data" in data_source:
                print("\n🎉 SUCCESS: USING REAL DEMO COMPANY DATA!")
                print("-" * 50)
                print(f"💰 Revenue (YTD):     ${xero_data.get('revenue', 0):>10,.2f}")
                print(f"💰 Gross Profit:      ${xero_data.get('gross_profit', 0):>10,.2f}")
                print(f"📈 Net Income:        ${xero_data.get('net_income', 0):>10,.2f}")
                print("\n✅ Real data integration working!")
            else:
                print(f"⚠️ Still using fallback data: {data_source}")
        
        if result and 'market_research' in result:
            research_len = len(result['market_research']) if result['market_research'] else 0
            print(f"🔍 Market Research: {research_len} characters (real Perplexity data)")
        
        if result and 'workflow_complete' in result:
            print(f"🏁 Workflow Complete: {result['workflow_complete']}")
        
        if result and 'notion_report_url' in result:
            print(f"📄 Notion Report: {result['notion_report_url']}")
            print(f"🔗 View your financial forecast report at the URL above!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_fresh_env()