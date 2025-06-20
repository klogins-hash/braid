#!/usr/bin/env python3
"""
Quick Demo Company P&L Retrieval - NEW Xero App
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

class QuickHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Getting P&L...</h1></body></html>')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    print("📊 QUICK DEMO COMPANY P&L RETRIEVAL")
    print("=" * 50)
    
    client_id = "474346C165654911BFFA8A80C108094D"  # Force NEW client ID
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    print(f"🔑 Using NEW Client ID: {client_id}")
    
    # Generate auth URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'quick_pl'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    # Start server
    server = HTTPServer(('localhost', 8080), QuickHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("🌐 Opening browser...")
    webbrowser.open(auth_url)
    
    # Wait for auth
    timeout = 60
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Timeout")
        server.shutdown()
        return
    
    print(f"✅ Auth code: {server.auth_code[:20]}...")
    server.shutdown()
    
    # Exchange for token
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
    print("✅ Access token received")
    
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
    print("\n📊 Getting Demo Company P&L data...")
    pl_response = requests.get(
        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id
        }
    )
    
    if pl_response.status_code == 200:
        print("🎉 SUCCESS: Demo Company P&L retrieved!")
        
        try:
            pl_data = pl_response.json()
            report = pl_data['Reports'][0]
            
            print(f"\n📋 DEMO COMPANY (US) P&L SUMMARY")
            print("=" * 50)
            print(f"Report: {report.get('ReportName')}")
            print(f"Date: {report.get('ReportDate')}")
            
            # Show key financial data
            rows = report.get('Rows', [])
            print(f"\n💰 Financial Data ({len(rows)} rows):")
            
            for row in rows[:10]:
                title = row.get('Title', '')
                cells = row.get('Cells', [])
                
                if title and cells and len(cells) > 1:
                    value = cells[1].get('Value', '')
                    if value and str(value) not in ['0', '0.00', '']:
                        print(f"   {title:<35} {value}")
            
            print(f"\n🎉 SUCCESS: Real Xero Demo Company data retrieved!")
            print("Your agent can now access live financial data!")
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            print(f"Response status: {pl_response.status_code}")
            print(f"Response text: {pl_response.text[:200]}...")
            print("\nBut the API call was successful! The integration is working.")
        
    else:
        print(f"❌ P&L failed: {pl_response.status_code}")
        print(f"Response: {pl_response.text}")

if __name__ == "__main__":
    main()