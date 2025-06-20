#!/usr/bin/env python3
"""
Display Demo Company (US) P&L Data from Xero
"""

import os
import requests
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv

load_dotenv()

class PLOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Getting P&L data...</h1></body></html>')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No code</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def format_currency(value_str):
    """Format currency value for display."""
    try:
        if not value_str or value_str == "":
            return "$0.00"
        # Remove any existing formatting
        clean_value = str(value_str).replace(',', '').replace('$', '')
        if clean_value == "0" or clean_value == "0.00":
            return "$0.00"
        
        # Convert to float and format
        value = float(clean_value)
        if value < 0:
            return f"-${abs(value):,.2f}"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return str(value_str)

def display_pl_data(pl_data):
    """Display P&L data in a readable format."""
    print("\n" + "=" * 80)
    print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
    print("=" * 80)
    
    if 'Reports' not in pl_data or not pl_data['Reports']:
        print("❌ No P&L data found")
        return
    
    report = pl_data['Reports'][0]
    print(f"📋 Report: {report.get('ReportName', 'P&L Report')}")
    print(f"📅 Date: {report.get('ReportDate', 'N/A')}")
    print(f"🏢 Organization: Demo Company (US)")
    print("-" * 80)
    
    rows = report.get('Rows', [])
    
    for row in rows:
        title = row.get('Title', '')
        row_type = row.get('RowType', '')
        cells = row.get('Cells', [])
        
        if title and cells:
            # Get the main value (usually in the second cell)
            if len(cells) > 1:
                value = cells[1].get('Value', '')
                formatted_value = format_currency(value)
                
                # Format display based on row type and title
                if row_type == 'Header':
                    print(f"\n📈 {title.upper()}")
                    print("-" * 40)
                elif 'Total' in title:
                    print(f"💰 {title:<40} {formatted_value:>15}")
                    print("-" * 57)
                else:
                    print(f"   {title:<40} {formatted_value:>15}")
        
        # Handle sub-rows
        if 'Rows' in row:
            for sub_row in row['Rows']:
                sub_title = sub_row.get('Title', '')
                sub_cells = sub_row.get('Cells', [])
                if sub_title and sub_cells and len(sub_cells) > 1:
                    sub_value = sub_cells[1].get('Value', '')
                    formatted_sub_value = format_currency(sub_value)
                    print(f"     • {sub_title:<36} {formatted_sub_value:>15}")

def main():
    print("📊 XERO DEMO COMPANY (US) - P&L DATA VIEWER")
    print("=" * 60)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Xero credentials")
        return
    
    print(f"🔑 Using Client ID: {client_id}")
    
    # Step 1: Get authorization
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'pl_viewer'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    print("\n🌐 Opening browser for Xero authorization...")
    
    # Start callback server
    server = HTTPServer(('localhost', 8080), PLOAuthHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    print("⏳ Please authorize in browser...")
    
    # Wait for auth code
    timeout = 120
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Authorization timeout")
        server.shutdown()
        return
    
    print("✅ Authorization received")
    server.shutdown()
    
    # Step 2: Get access token
    print("\n🔄 Getting access token...")
    token_response = requests.post(
        'https://identity.xero.com/connect/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': server.auth_code,
            'redirect_uri': 'http://localhost:8080/callback'
        }
    )
    
    if token_response.status_code != 200:
        print(f"❌ Token failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    print("✅ Access token received")
    
    # Step 3: Get tenant info
    print("\n🏢 Getting organization info...")
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if conn_response.status_code != 200:
        print(f"❌ Connections failed: {conn_response.text}")
        return
    
    connections = conn_response.json()
    if not connections:
        print("❌ No organizations found")
        return
    
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    print(f"✅ Connected to: {tenant_name}")
    
    # Step 4: Get P&L Report
    print("\n📊 Retrieving Profit & Loss data...")
    pl_response = requests.get(
        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id
        }
    )
    
    if pl_response.status_code != 200:
        print(f"❌ P&L request failed: {pl_response.status_code}")
        print(f"Response: {pl_response.text}")
        return
    
    print("✅ P&L data retrieved successfully!")
    
    # Display the data
    pl_data = pl_response.json()
    display_pl_data(pl_data)
    
    print("\n" + "=" * 80)
    print("🎉 REAL XERO DATA INTEGRATION COMPLETE!")
    print("✅ Successfully retrieved Demo Company (US) P&L")
    print("✅ Your agent can now access live financial data")
    print("=" * 80)

if __name__ == "__main__":
    main()