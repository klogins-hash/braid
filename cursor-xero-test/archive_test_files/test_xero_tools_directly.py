#!/usr/bin/env python3
"""
Test XeroTools directly to debug
"""

import sys
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv(override=True)

from src.tools.xero_tools import XeroTools

def test_xero_tools():
    print("🔧 Testing XeroTools directly...")
    
    xero = XeroTools()
    
    print(f"Access token: {xero.access_token[:20] if xero.access_token else 'NOT_SET'}...")
    print(f"Tenant ID: {xero.tenant_id}")
    print(f"Headers: {xero.headers}")
    
    # Test get_profit_and_loss
    print("\n📊 Testing get_profit_and_loss...")
    result = xero.get_profit_and_loss()
    
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result) if result else 0}")
    
    if result and len(result) > 0:
        record = result[0]
        print(f"Data source: {record.get('data_source', 'Unknown')}")
        print(f"Revenue: ${record.get('revenue', 0):,.2f}")
        print(f"Net Income: ${record.get('net_income', 0):,.2f}")
        
        if "Real Xero Data" in record.get('data_source', ''):
            print("🎉 SUCCESS: Using REAL Demo Company data!")
        else:
            print("⚠️ Using mock/fallback data")

if __name__ == "__main__":
    test_xero_tools()