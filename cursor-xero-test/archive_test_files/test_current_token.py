#!/usr/bin/env python3
"""
Test current token directly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def test_token():
    access_token = os.getenv('XERO_ACCESS_TOKEN')
    tenant_id = os.getenv('XERO_TENANT_ID')
    
    print(f"Token: {access_token[:20]}...")
    print(f"Tenant: {tenant_id}")
    
    # Test connections
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print(f"Connections status: {conn_response.status_code}")
    
    if conn_response.status_code == 200:
        connections = conn_response.json()
        print(f"Connected to: {connections[0].get('tenantName', 'Unknown')}")
        
        # Test P&L
        from datetime import datetime, date
        current_year = datetime.now().year
        from_date = f"{current_year}-01-01"
        to_date = date.today().strftime("%Y-%m-%d")
        
        pl_response = requests.get(
            f'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss?fromDate={from_date}&toDate={to_date}',
            headers={
                'Authorization': f'Bearer {access_token}',
                'xero-tenant-id': tenant_id,
                'Accept': 'application/xml'
            }
        )
        
        print(f"P&L status: {pl_response.status_code}")
        if pl_response.status_code == 200:
            print("✅ SUCCESS: Token works!")
        else:
            print(f"❌ P&L failed: {pl_response.text}")
    else:
        print(f"❌ Connections failed: {conn_response.text}")

if __name__ == "__main__":
    test_token()