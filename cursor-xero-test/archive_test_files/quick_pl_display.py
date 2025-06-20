#!/usr/bin/env python3
"""
Quick P&L Display - Using existing Xero integration
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add the src directory to the path so we can import our tools
sys.path.append('src')

try:
    from tools.xero_tools import XeroIntegration
    print("✅ Using existing Xero integration")
except ImportError:
    print("❌ Could not import XeroIntegration, will use direct API")
    XeroIntegration = None

def format_currency(value_str):
    """Format currency value for display."""
    try:
        if not value_str or value_str == "":
            return "$0.00"
        clean_value = str(value_str).replace(',', '').replace('$', '')
        if clean_value == "0" or clean_value == "0.00":
            return "$0.00"
        
        value = float(clean_value)
        if value < 0:
            return f"-${abs(value):,.2f}"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return str(value_str)

def display_pl_structure(pl_data):
    """Display P&L data structure."""
    print("\n" + "=" * 80)
    print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
    print("=" * 80)
    
    if 'Reports' not in pl_data or not pl_data['Reports']:
        print("❌ No P&L data found")
        return
    
    report = pl_data['Reports'][0]
    print(f"📋 Report: {report.get('ReportName', 'P&L Report')}")
    print(f"📅 Report Date: {report.get('ReportDate', 'N/A')}")
    print(f"🏢 Organization: Demo Company (US)")
    print("-" * 80)
    
    rows = report.get('Rows', [])
    print(f"📊 Total data rows: {len(rows)}")
    
    # Display key financial sections
    for row in rows:
        title = row.get('Title', '')
        cells = row.get('Cells', [])
        
        if title and cells and len(cells) > 1:
            value = cells[1].get('Value', '')
            formatted_value = format_currency(value)
            
            # Show main categories
            if any(keyword in title.lower() for keyword in ['revenue', 'income', 'sales', 'total', 'gross', 'net']):
                print(f"💰 {title:<50} {formatted_value:>15}")
            
            # Show sub-items if they exist
            if 'Rows' in row:
                sub_rows = row.get('Rows', [])
                for sub_row in sub_rows[:3]:  # Show first 3 sub-items
                    sub_title = sub_row.get('Title', '')
                    sub_cells = sub_row.get('Cells', [])
                    if sub_title and sub_cells and len(sub_cells) > 1:
                        sub_value = sub_cells[1].get('Value', '')
                        formatted_sub_value = format_currency(sub_value)
                        print(f"   • {sub_title:<46} {formatted_sub_value:>15}")

def test_direct_api():
    """Test direct API call to get P&L data."""
    load_dotenv()
    
    access_token = os.getenv('XERO_ACCESS_TOKEN')
    tenant_id = os.getenv('XERO_TENANT_ID')
    
    if not access_token or not tenant_id:
        print("❌ Missing Xero tokens in .env file")
        print("   Run: python test_new_xero.py to get fresh tokens")
        return None
    
    print("🔍 Testing direct Xero API call...")
    print(f"   Token: {access_token[:30]}...")
    print(f"   Tenant: {tenant_id}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'xero-tenant-id': tenant_id,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
            headers=headers,
            timeout=30
        )
        
        print(f"📡 API Response: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS: Retrieved P&L data!")
            return response.json()
        elif response.status_code == 401:
            print("❌ Token expired - run: python test_new_xero.py")
            return None
        else:
            print(f"❌ API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def main():
    print("📊 DEMO COMPANY (US) P&L DATA VIEWER")
    print("=" * 60)
    
    # Method 1: Try using our existing Xero integration
    if XeroIntegration:
        try:
            print("🔧 Method 1: Using XeroIntegration class...")
            xero = XeroIntegration()
            result = xero.get_profit_and_loss()
            
            if "SUCCESS" in result:
                print("✅ Retrieved P&L via XeroIntegration")
                # Parse the result if it contains JSON
                if "Reports" in result:
                    import json
                    # Extract JSON from the result string
                    json_start = result.find('{"Reports"')
                    if json_start != -1:
                        json_data = result[json_start:]
                        try:
                            pl_data = json.loads(json_data)
                            display_pl_structure(pl_data)
                            return
                        except json.JSONDecodeError:
                            pass
                
                print("📋 Raw result from XeroIntegration:")
                print(result[:500] + "..." if len(result) > 500 else result)
                return
            else:
                print(f"⚠️ XeroIntegration result: {result}")
        except Exception as e:
            print(f"⚠️ XeroIntegration failed: {e}")
    
    # Method 2: Direct API call
    print("\n🔧 Method 2: Direct API call...")
    pl_data = test_direct_api()
    
    if pl_data:
        display_pl_structure(pl_data)
        
        print("\n" + "=" * 80)
        print("🎉 REAL XERO DATA INTEGRATION VERIFIED!")
        print("✅ Successfully retrieved Demo Company (US) financial data")
        print("✅ Your agent can access live P&L reports")
        print("✅ Ready for production financial forecasting")
        print("=" * 80)
    else:
        print("\n❌ Could not retrieve P&L data")
        print("💡 Try running: python test_new_xero.py to get fresh tokens")

if __name__ == "__main__":
    main()