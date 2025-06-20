#!/usr/bin/env python3
"""
Quick Xero API Test - Get Fresh Token and Test P&L Data
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

class QuickOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Close this window.</h1></body></html>')
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

def main():
    print("🚀 QUICK XERO TEST - GET FRESH TOKEN & TEST P&L")
    print("=" * 60)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Xero credentials in .env")
        return
    
    print(f"✅ Using Client ID: {client_id}")
    
    # Step 1: Get auth URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'quick_test'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    print(f"\n🌐 Opening browser for fresh authorization...")
    
    # Step 2: Start server and get auth code
    server = HTTPServer(('localhost', 8080), QuickOAuthHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    print("⏳ Waiting for authorization...")
    
    timeout = 60  # 1 minute
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Timeout")
        server.shutdown()
        return
    
    print(f"✅ Got auth code: {server.auth_code[:20]}...")
    server.shutdown()
    
    # Step 3: Exchange for tokens
    print("\n🔄 Getting fresh access token...")
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
        print(f"❌ Token exchange failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    print(f"✅ Fresh access token: {access_token[:20]}...")
    
    # Step 4: Get connections
    print("\n🏢 Getting Xero connections...")
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if conn_response.status_code != 200:
        print(f"❌ Connections failed: {conn_response.text}")
        return
    
    connections = conn_response.json()
    if not connections:
        print("❌ No connections found")
        return
    
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    print(f"✅ Using: {tenant_name} ({tenant_id})")
    
    # Step 5: Test REAL P&L data
    print("\n📊 TESTING REAL XERO P&L DATA...")
    print("=" * 50)
    
    pl_response = requests.get(
        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id
        }
    )
    
    if pl_response.status_code == 200:
        print("🎉 SUCCESS: Retrieved REAL Xero P&L data!")
        
        pl_data = pl_response.json()
        if 'Reports' in pl_data:
            report = pl_data['Reports'][0]
            print(f"📋 Report: {report.get('ReportName')}")
            print(f"📅 Date: {report.get('ReportDate')}")
            print(f"📊 Rows: {len(report.get('Rows', []))}")
            
            # Show some actual financial data
            rows = report.get('Rows', [])
            print("\n💰 Financial Data:")
            for row in rows[:5]:  # Show first 5 rows
                title = row.get('Title', '')
                if title and 'Total' not in title:
                    cells = row.get('Cells', [])
                    if len(cells) > 1:
                        value = cells[1].get('Value', 'N/A')
                        print(f"   {title}: {value}")
            
            print(f"\n🎉 REAL XERO DATA INTEGRATION WORKING!")
            print("=" * 50)
            print("✅ Your agent can now access live accounting data")
            print("✅ Demo Company (US) P&L report retrieved successfully")
            print("✅ Ready for full agent testing with real data")
            
        return True
    else:
        print(f"❌ P&L request failed: {pl_response.status_code}")
        print(f"   Response: {pl_response.text}")
        return False

if __name__ == "__main__":
    main()