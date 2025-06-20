#!/usr/bin/env python3
"""
Show P&L Response: Display exactly what Xero returns
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

load_dotenv(override=True)

class ShowResponseHandler(BaseHTTPRequestHandler):
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
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def format_currency(value):
    """Format currency values for display."""
    if not value:
        return "$0.00"
    try:
        val_str = str(value).replace(',', '').replace('$', '')
        val_float = float(val_str)
        if val_float < 0:
            return f"-${abs(val_float):,.2f}"
        else:
            return f"${val_float:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def display_pl_data(pl_data):
    """Display P&L data in a readable format."""
    
    print("\n" + "="*80)
    print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
    print("="*80)
    
    if 'Reports' not in pl_data or not pl_data['Reports']:
        print("❌ No Reports found in response")
        return
    
    report = pl_data['Reports'][0]
    
    print(f"📋 Report Name: {report.get('ReportName', 'N/A')}")
    print(f"📅 Report Date: {report.get('ReportDate', 'N/A')}")
    print(f"🏢 Report ID: {report.get('ReportID', 'N/A')}")
    print(f"📊 Updated: {report.get('UpdatedDateUTC', 'N/A')}")
    
    rows = report.get('Rows', [])
    print(f"\n📈 Total Data Rows: {len(rows)}")
    print("-"*80)
    
    # Display the financial data
    for i, row in enumerate(rows):
        title = row.get('Title', '')
        row_type = row.get('RowType', '')
        cells = row.get('Cells', [])
        
        if title:
            print(f"\n{i+1}. {title} ({row_type})")
            
            # Show cell values
            if cells:
                for j, cell in enumerate(cells):
                    value = cell.get('Value', '')
                    if value and str(value) not in ['', '0', '0.00']:
                        if j == 0:
                            print(f"    Account: {value}")
                        elif j == 1:
                            formatted_value = format_currency(value)
                            print(f"    Amount:  {formatted_value}")
                        else:
                            print(f"    Cell {j}: {value}")
            
            # Show sub-rows if they exist
            if 'Rows' in row:
                sub_rows = row.get('Rows', [])
                for k, sub_row in enumerate(sub_rows):
                    sub_title = sub_row.get('Title', '')
                    sub_cells = sub_row.get('Cells', [])
                    
                    if sub_title:
                        print(f"      └─ {sub_title}")
                        
                        if sub_cells:
                            for l, sub_cell in enumerate(sub_cells):
                                sub_value = sub_cell.get('Value', '')
                                if sub_value and str(sub_value) not in ['', '0', '0.00']:
                                    if l == 1:  # Usually the amount column
                                        formatted_sub_value = format_currency(sub_value)
                                        print(f"           Amount: {formatted_sub_value}")

def main():
    """Get P&L data and show the complete response."""
    
    print("📊 DEMO COMPANY P&L DATA VIEWER")
    print("="*60)
    print("This will show you exactly what data comes back from Xero")
    
    # Use NEW Xero app credentials
    client_id = "474346C165654911BFFA8A80C108094D"
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    redirect_uri = 'http://localhost:8080/callback'
    
    print(f"\n🔑 Using Client ID: {client_id}")
    
    if not client_secret:
        print("❌ Missing XERO_CLIENT_SECRET")
        return
    
    # OAuth2 flow
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'show_response'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Opening browser for authorization...")
    
    # Start server
    server = HTTPServer(('localhost', 8080), ShowResponseHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    
    # Wait for auth
    timeout = 90
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Authorization timeout")
        server.shutdown()
        return
    
    print("✅ Authorization successful")
    server.shutdown()
    
    # Get token
    token_response = requests.post(
        'https://identity.xero.com/connect/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': server.auth_code,
            'redirect_uri': redirect_uri
        }
    )
    
    if token_response.status_code != 200:
        print(f"❌ Token failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    
    # Get connections
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if conn_response.status_code != 200:
        print(f"❌ Connections failed: {conn_response.text}")
        return
    
    connections = conn_response.json()
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"✅ Connected to: {tenant_name}")
    
    # Get P&L data
    print("\n📊 Retrieving P&L data...")
    
    pl_response = requests.get(
        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id,
            'Content-Type': 'application/json'
        }
    )
    
    print(f"📡 Response Status: {pl_response.status_code}")
    print(f"📄 Response Size: {len(pl_response.text)} characters")
    print(f"📋 Content Type: {pl_response.headers.get('content-type', 'Unknown')}")
    
    if pl_response.status_code == 200:
        print("\n🔍 RAW RESPONSE (first 500 characters):")
        print("-" * 60)
        print(pl_response.text[:500])
        print("-" * 60)
        
        # Try different parsing approaches
        try:
            # Method 1: Direct JSON parsing
            pl_data = pl_response.json()
            print("\n✅ JSON parsing successful!")
            display_pl_data(pl_data)
            
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSON parsing failed: {e}")
            
            # Method 2: Check for BOM or encoding issues
            response_bytes = pl_response.content
            print(f"📄 Raw bytes length: {len(response_bytes)}")
            print(f"🔤 First 10 bytes: {response_bytes[:10]}")
            
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
                try:
                    text = response_bytes.decode(encoding)
                    parsed = json.loads(text)
                    print(f"\n✅ Success with {encoding} encoding!")
                    display_pl_data(parsed)
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    print(f"❌ Failed with {encoding} encoding")
                    continue
            else:
                print("\n❌ Could not parse response with any encoding")
                print("But the API call was successful - integration is working!")
                
    else:
        print(f"❌ API call failed: {pl_response.text}")

if __name__ == "__main__":
    main()