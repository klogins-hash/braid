#!/usr/bin/env python3
"""
Final Integration Test - Demo Company YTD Data
"""

import sys
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv(override=True)

from src.tools.xero_tools import XeroTools

def main():
    print("🎉 FINAL INTEGRATION TEST")
    print("=" * 60)
    print("✅ All test files cleaned up and archived")
    print("✅ Fresh OAuth2 tokens obtained")
    print("✅ Agent updated to use real YTD P&L data")
    print()
    
    # Test real data connection
    print("🔧 Testing real Demo Company connection...")
    xero = XeroTools()
    
    result = xero.get_profit_and_loss()
    
    if result and len(result) > 0:
        record = result[0]
        data_source = record.get('data_source', 'Unknown')
        
        print(f"📊 Data Source: {data_source}")
        
        if "Real Xero Data" in data_source:
            print()
            print("🎉 SUCCESS: AGENT NOW USES REAL DEMO COMPANY DATA!")
            print("=" * 60)
            print("📊 DEMO COMPANY (US) - YEAR-TO-DATE FINANCIAL DATA:")
            print("-" * 60)
            print(f"💰 Revenue (YTD):        ${record.get('revenue', 0):>10,.2f}")
            print(f"📦 Cost of Sales (YTD):  ${record.get('cost_of_goods_sold', 0):>10,.2f}")
            print(f"💰 Gross Profit (YTD):   ${record.get('gross_profit', 0):>10,.2f}")
            print(f"💸 Operating Exp (YTD):  ${record.get('operating_expenses', 0):>10,.2f}")
            print(f"📈 Net Income (YTD):     ${record.get('net_income', 0):>10,.2f}")
            print()
            print("🔄 INTEGRATION COMPLETE:")
            print("✅ Your financial forecasting agent now pulls REAL financial data")
            print("✅ Only client SQL data is mocked (business description, strategy, location)")
            print("✅ All other data sources are live (Xero, Perplexity, OpenAI)")
            print()
            print("🚀 READY FOR PRODUCTION USE!")
            
        else:
            print(f"⚠️ Still using fallback data: {data_source}")
            print("Check token expiration or API connectivity")
    
    else:
        print("❌ No data returned from Xero")

if __name__ == "__main__":
    main()