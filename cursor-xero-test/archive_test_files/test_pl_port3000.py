#!/usr/bin/env python3
"""
Test P&L Data with Port 3000 - Avoid Redirect URI Issues
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

class Port3000Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Getting P&L data...</h1><script>window.close();</script></body></html>')
                print(f"✅ Authorization code received: {query['code'][0][:20]}...")
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No authorization code</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    print("📊 DEMO COMPANY P&L - PORT 3000 TEST")
    print("=" * 50)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    print(f"🔑 Client ID: {client_id}")
    
    if not client_id or not client_secret:
        print("❌ Missing Xero credentials")
        return
    
    # Try with port 3000 redirect URI
    redirect_uri = 'http://localhost:3000/callback'
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'port3000_test'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print(f"🌐 Using redirect URI: {redirect_uri}")
    print(f"🔗 Auth URL: {auth_url[:100]}...")
    
    # Start server on port 3000
    try:
        server = HTTPServer(('localhost', 3000), Port3000Handler)
        server.auth_code = None
        
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ Server started on port 3000")
        print("🌐 Opening browser...")
        
        webbrowser.open(auth_url)
        
        # Wait for authorization
        print("⏳ Waiting for authorization...")
        timeout = 120
        start_time = time.time()
        
        while server.auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        server.shutdown()
        
        if server.auth_code is None:
            print("❌ Authorization timeout")
            return
        
        print("✅ Authorization successful!")
        
        # Exchange for tokens
        print("🔄 Exchanging for access token...")
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
            print(f"❌ Token exchange failed: {token_response.status_code}")
            print(f"Response: {token_response.text}")
            return
        
        tokens = token_response.json()
        access_token = tokens['access_token']
        print("✅ Access token received")
        
        # Get connections
        print("🏢 Getting Xero connections...")
        conn_response = requests.get(
            'https://api.xero.com/connections',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if conn_response.status_code != 200:
            print(f"❌ Connections failed: {conn_response.status_code}")
            return
        
        connections = conn_response.json()
        if not connections:
            print("❌ No connections found")
            return
        
        tenant_id = connections[0]['tenantId']
        tenant_name = connections[0].get('tenantName', 'Unknown')
        print(f"✅ Connected to: {tenant_name}")
        
        # Get P&L Report
        print("📊 Retrieving Profit & Loss data...")
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
        
        print("🎉 SUCCESS: P&L data retrieved!")
        
        # Display P&L data
        pl_data = pl_response.json()
        report = pl_data['Reports'][0]
        
        print("\\n" + "=" * 80)
        print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
        print("=" * 80)
        print(f"📋 Report: {report.get('ReportName')}")
        print(f"📅 Date: {report.get('ReportDate')}")
        print(f"🏢 Organization: {tenant_name}")
        print("-" * 80)
        
        rows = report.get('Rows', [])
        print(f"\\n💰 KEY FINANCIAL DATA:")
        
        # Display key financial figures
        for row in rows[:15]:  # Show first 15 rows
            title = row.get('Title', '')
            cells = row.get('Cells', [])
            
            if title and cells and len(cells) > 1:
                value = cells[1].get('Value', '')
                if value and str(value) not in ['0', '0.00', '']:
                    try:
                        val_float = float(str(value).replace(',', ''))
                        if val_float != 0:
                            formatted = f"${val_float:,.2f}" if val_float >= 0 else f"-${abs(val_float):,.2f}"
                            print(f"   {title:<45} {formatted:>15}")
                    except (ValueError, TypeError):
                        if value:
                            print(f"   {title:<45} {str(value):>15}")
        
        print("\\n" + "=" * 80)
        print("🎉 REAL XERO DATA INTEGRATION COMPLETE!")
        print("✅ Successfully retrieved Demo Company (US) P&L")
        print("✅ Your financial forecasting agent can now access live data")
        print("=" * 80)
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port 3000 is in use. Try: lsof -ti:3000 | xargs kill -9")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()