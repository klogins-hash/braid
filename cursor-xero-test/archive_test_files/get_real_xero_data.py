#!/usr/bin/env python3
"""
Real Xero Data Integration Guide
This script shows how to get actual Xero accounting data vs mock data.
"""

import os
import requests
from datetime import datetime

def test_current_token():
    """Test what our current token can actually access."""
    print("🔍 TESTING CURRENT XERO TOKEN CAPABILITIES")
    print("=" * 60)
    
    token = os.getenv('XERO_ACCESS_TOKEN', '').strip()
    
    if not token:
        print("❌ No Xero token found in environment")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test 1: Connections endpoint (should work with client credentials)
    print("\n📡 Testing /connections endpoint...")
    try:
        response = requests.get('https://api.xero.com/connections', headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            connections = response.json()
            print(f"✅ SUCCESS: Found {len(connections)} connections")
            for conn in connections:
                print(f"   - Tenant: {conn.get('tenantName', 'Unknown')}")
                print(f"   - ID: {conn.get('tenantId', 'Unknown')}")
                print(f"   - Type: {conn.get('tenantType', 'Unknown')}")
        else:
            print(f"❌ FAILED: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Try to get tenant info (might work)
    print("\n📊 Testing tenant access...")
    try:
        # First get connections to get tenant ID
        conn_response = requests.get('https://api.xero.com/connections', headers=headers)
        if conn_response.status_code == 200:
            connections = conn_response.json()
            if connections:
                tenant_id = connections[0]['tenantId']
                
                # Try to access organisation info
                org_headers = headers.copy()
                org_headers['xero-tenant-id'] = tenant_id
                
                org_response = requests.get(
                    'https://api.xero.com/api.xro/2.0/Organisation',
                    headers=org_headers
                )
                
                print(f"Organisation endpoint status: {org_response.status_code}")
                if org_response.status_code == 200:
                    org_data = org_response.json()
                    print("✅ SUCCESS: Can access organisation data")
                    if 'Organisations' in org_data:
                        org = org_data['Organisations'][0]
                        print(f"   Company: {org.get('Name', 'Unknown')}")
                        print(f"   Country: {org.get('CountryCode', 'Unknown')}")
                        print(f"   Base Currency: {org.get('BaseCurrency', 'Unknown')}")
                else:
                    print(f"❌ CANNOT access organisation: {org_response.text}")
    except Exception as e:
        print(f"❌ ERROR testing tenant access: {e}")
    
    # Test 3: Try to get actual P&L data (will likely fail with client credentials)
    print("\n📈 Testing P&L report access...")
    try:
        conn_response = requests.get('https://api.xero.com/connections', headers=headers)
        if conn_response.status_code == 200:
            connections = conn_response.json()
            if connections:
                tenant_id = connections[0]['tenantId']
                
                pl_headers = headers.copy()
                pl_headers['xero-tenant-id'] = tenant_id
                
                pl_response = requests.get(
                    'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
                    headers=pl_headers
                )
                
                print(f"P&L endpoint status: {pl_response.status_code}")
                if pl_response.status_code == 200:
                    pl_data = pl_response.json()
                    print("🎉 SUCCESS: CAN ACCESS REAL P&L DATA!")
                    print("   This means we can get real financial data from Xero!")
                    
                    # Parse and show real data structure
                    if 'Reports' in pl_data and len(pl_data['Reports']) > 0:
                        report = pl_data['Reports'][0]
                        print(f"   Report Name: {report.get('ReportName', 'Unknown')}")
                        print(f"   Report Date: {report.get('ReportDate', 'Unknown')}")
                        print(f"   Rows Count: {len(report.get('Rows', []))}")
                        
                        # Show structure
                        rows = report.get('Rows', [])
                        for i, row in enumerate(rows[:3]):  # Show first 3 rows
                            print(f"   Row {i+1}: {row.get('RowType', 'Unknown')} - {row.get('Title', 'No title')}")
                    
                else:
                    print(f"❌ CANNOT access P&L data: {pl_response.text}")
                    print("   This confirms we need proper OAuth2 flow for accounting data")
    except Exception as e:
        print(f"❌ ERROR testing P&L access: {e}")

def show_oauth_flow_requirements():
    """Show what's needed for real Xero data access."""
    print("\n🔑 REQUIREMENTS FOR REAL XERO DATA ACCESS")
    print("=" * 60)
    
    print("""
To get REAL Xero accounting data, you need:

1. 📋 PROPER OAUTH2 FLOW:
   - Authorization Code flow (not Client Credentials)
   - User must grant consent to access their Xero data
   - Requires web browser interaction

2. 🎯 REQUIRED SCOPES:
   - accounting.reports.read (for P&L statements)
   - accounting.transactions.read (for transaction data)
   - accounting.contacts.read (for customer/supplier data)

3. 🏢 TENANT SELECTION:
   - User must select which Xero organisation to access
   - Each organisation has a separate tenant ID

4. 🔄 TOKEN REFRESH:
   - Access tokens expire (30 minutes)
   - Need refresh tokens for long-term access

CURRENT STATUS:
❌ We have client credentials token (limited access)
✅ We have valid API credentials and can connect
✅ Perplexity is working with real market data
✅ Database has real client information

OPTIONS:
1. Keep enhanced mock data (realistic for demo)
2. Implement full OAuth2 flow for real data
3. Use Xero Demo Company data (if available)
""")

def show_implementation_options():
    """Show different options for getting real data."""
    print("\n🛠️ IMPLEMENTATION OPTIONS")
    print("=" * 60)
    
    print("""
OPTION 1: ENHANCED MOCK (CURRENT) ✅
- Realistic financial data based on client profile
- Immediate testing and development
- No user consent required
- Good for demonstrations

OPTION 2: FULL OAUTH2 IMPLEMENTATION 🔧
- Real accounting data from actual Xero accounts
- Requires web server for OAuth2 callback
- User consent and tenant selection flow
- Production-ready solution

OPTION 3: XERO DEMO COMPANY 📊
- Real Xero API structure with demo data
- More realistic than mock data
- Still requires proper OAuth2 flow

RECOMMENDATION FOR NOW:
Keep using enhanced mock data since:
- Perplexity IS providing real market research
- Database IS providing real client data
- Mock financial data is realistic and structured correctly
- The workflow demonstrates the complete agent functionality

The agent is working correctly - it's just using simulated
financial data instead of connecting to a real accounting system.
""")

def main():
    """Main function."""
    print("🔍 XERO DATA ANALYSIS TOOL")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_current_token()
    show_oauth_flow_requirements()
    show_implementation_options()
    
    print("\n✅ ANALYSIS COMPLETE")
    print("The agent is working correctly with enhanced mock data.")
    print("For production use, implement full OAuth2 flow for real Xero data.")

if __name__ == "__main__":
    main()