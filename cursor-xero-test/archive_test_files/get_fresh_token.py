#!/usr/bin/env python3
"""
Get Fresh Xero Token - Minimal OAuth2 Flow
"""

import os
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv

load_dotenv()

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Token received.</h1><script>window.close();</script></body></html>')
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
    print("🔑 Getting Fresh Xero Token...")
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing credentials")
        return
    
    # Generate auth URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'get_token'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    # Start server
    server = HTTPServer(('localhost', 8080), TokenHandler)
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
    
    if token_response.status_code == 200:
        tokens = token_response.json()
        access_token = tokens['access_token']
        print(f"✅ Fresh token: {access_token[:30]}...")
        
        # Get tenant
        conn_response = requests.get(
            'https://api.xero.com/connections',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if conn_response.status_code == 200:
            connections = conn_response.json()
            tenant_id = connections[0]['tenantId']
            
            # Now get P&L data
            print(f"\n📊 Getting P&L data...")
            pl_response = requests.get(
                'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'xero-tenant-id': tenant_id
                }
            )
            
            if pl_response.status_code == 200:
                print("🎉 SUCCESS: Retrieved Demo Company P&L!")
                
                pl_data = pl_response.json()
                report = pl_data['Reports'][0]
                
                print(f"\n📋 DEMO COMPANY (US) - P&L SUMMARY")
                print("=" * 50)
                print(f"Report: {report.get('ReportName')}")
                print(f"Date: {report.get('ReportDate')}")
                
                # Show key financial figures
                rows = report.get('Rows', [])
                print(f"\nKey Financial Data:")
                
                for row in rows[:10]:  # Show first 10 rows
                    title = row.get('Title', '')
                    cells = row.get('Cells', [])
                    
                    if title and cells and len(cells) > 1:
                        value = cells[1].get('Value', '')
                        if value and value != "0" and value != "0.00":
                            try:
                                val_float = float(str(value).replace(',', ''))
                                formatted = f"${val_float:,.2f}" if val_float >= 0 else f"-${abs(val_float):,.2f}"
                                print(f"  {title:<40} {formatted:>12}")
                            except:
                                print(f"  {title:<40} {value:>12}")
                
                print(f"\n🎉 REAL XERO DATA SUCCESSFULLY RETRIEVED!")
                print("✅ Your agent can now access live Demo Company financial data")
                
            else:
                print(f"❌ P&L failed: {pl_response.status_code}")
        else:
            print(f"❌ Connections failed: {conn_response.status_code}")
    else:
        print(f"❌ Token exchange failed: {token_response.status_code}")

if __name__ == "__main__":
    main()