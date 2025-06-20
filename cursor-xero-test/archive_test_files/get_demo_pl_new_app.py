#!/usr/bin/env python3
"""
Get Demo Company P&L Data - Using NEW Xero App with Correct Redirect URI
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

class NewAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = '''
                <html><body>
                <h1>Success!</h1>
                <p>Authorization received for NEW Xero app.</p>
                <p>Getting Demo Company P&L data...</p>
                <script>setTimeout(function(){window.close();}, 3000);</script>
                </body></html>
                '''
                self.wfile.write(html.encode('utf-8'))
                print(f"✅ Auth code received for NEW app: {query['code'][0][:20]}...")
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

def format_currency(value):
    """Format currency for display."""
    try:
        if not value or value == "":
            return "$0.00"
        val_str = str(value).replace(',', '').replace('$', '')
        val_float = float(val_str)
        if val_float < 0:
            return f"-${abs(val_float):,.2f}"
        else:
            return f"${val_float:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def display_pl_summary(pl_data):
    """Display a summary of P&L data."""
    if 'Reports' not in pl_data or not pl_data['Reports']:
        print("❌ No P&L data in response")
        return
    
    report = pl_data['Reports'][0]
    
    print("\n" + "=" * 80)
    print("📊 DEMO COMPANY (US) - PROFIT & LOSS STATEMENT")
    print("=" * 80)
    print(f"📋 Report Name: {report.get('ReportName', 'N/A')}")
    print(f"📅 Report Date: {report.get('ReportDate', 'N/A')}")
    print(f"🏢 Organization: Demo Company (US)")
    print("-" * 80)
    
    rows = report.get('Rows', [])
    print(f"📊 Total data rows: {len(rows)}")
    
    print("\n💰 KEY FINANCIAL HIGHLIGHTS:")
    print("-" * 50)
    
    # Extract and display key financial figures
    for row in rows:
        title = row.get('Title', '')
        cells = row.get('Cells', [])
        
        if title and cells and len(cells) > 1:
            value = cells[1].get('Value', '')
            
            # Show important financial lines
            if any(keyword in title.lower() for keyword in 
                   ['total revenue', 'total income', 'gross profit', 'total expense', 'net profit', 'net income']):
                formatted_value = format_currency(value)
                print(f"   {title:<40} {formatted_value:>15}")
            
            # Show subcategories for revenue and expenses
            if 'Rows' in row:
                sub_rows = row.get('Rows', [])
                for sub_row in sub_rows[:5]:  # Show first 5 sub-items
                    sub_title = sub_row.get('Title', '')
                    sub_cells = sub_row.get('Cells', [])
                    if sub_title and sub_cells and len(sub_cells) > 1:
                        sub_value = sub_cells[1].get('Value', '')
                        if sub_value and str(sub_value) not in ['0', '0.00', '']:
                            formatted_sub_value = format_currency(sub_value)
                            print(f"     • {sub_title:<36} {formatted_sub_value:>15}")

def main():
    print("🆕 DEMO COMPANY P&L - NEW XERO APP")
    print("=" * 60)
    print("Using NEW Xero app with correct redirect URI configuration")
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    redirect_uri = os.getenv('XERO_REDIRECT_URI', 'http://localhost:8080/callback')
    
    print(f"🔑 NEW Client ID: {client_id}")
    print(f"🔗 Redirect URI: {redirect_uri}")
    
    if not client_id or not client_secret:
        print("❌ Missing NEW Xero app credentials")
        return
    
    # Generate authorization URL for NEW app
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'new_app_pl_test'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print(f"\n🌐 Opening browser for NEW app authorization...")
    print("This should work if your NEW Xero app has the correct redirect URI!")
    
    # Start callback server
    try:
        server = HTTPServer(('localhost', 8080), NewAppHandler)
        server.auth_code = None
        
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ Callback server started on port 8080")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for authorization
        print("⏳ Please complete authorization in browser...")
        timeout = 120  # 2 minutes
        start_time = time.time()
        
        while server.auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        server.shutdown()
        
        if server.auth_code is None:
            print("❌ Authorization timeout - check redirect URI configuration")
            return
        
        print("🎉 Authorization successful with NEW app!")
        
        # Exchange authorization code for tokens
        print("\n🔄 Exchanging code for access token...")
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
            print(f"   Response: {token_response.text}")
            return
        
        tokens = token_response.json()
        access_token = tokens['access_token']
        print("✅ Fresh access token received")
        
        # Get Xero connections
        print("\n🏢 Getting Xero connections...")
        conn_response = requests.get(
            'https://api.xero.com/connections',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if conn_response.status_code != 200:
            print(f"❌ Connections request failed: {conn_response.status_code}")
            print(f"   Response: {conn_response.text}")
            return
        
        connections = conn_response.json()
        if not connections:
            print("❌ No Xero organizations found")
            return
        
        tenant_id = connections[0]['tenantId']
        tenant_name = connections[0].get('tenantName', 'Unknown')
        print(f"✅ Connected to: {tenant_name} (ID: {tenant_id})")
        
        # Get P&L Report from Demo Company
        print("\n📊 Retrieving Demo Company P&L data...")
        pl_response = requests.get(
            'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
            headers={
                'Authorization': f'Bearer {access_token}',
                'xero-tenant-id': tenant_id,
                'Content-Type': 'application/json'
            }
        )
        
        if pl_response.status_code != 200:
            print(f"❌ P&L request failed: {pl_response.status_code}")
            print(f"   Response: {pl_response.text}")
            return
        
        print("🎉 SUCCESS: Retrieved Demo Company P&L data!")
        
        # Parse and display the P&L data
        pl_data = pl_response.json()
        display_pl_summary(pl_data)
        
        # Save tokens for future use
        print(f"\n💾 Saving tokens to .env file...")
        
        # Update .env file with new tokens
        env_lines = []
        with open('.env', 'r') as f:
            env_lines = f.readlines()
        
        # Add or update token lines
        updated_lines = []
        found_access = False
        found_tenant = False
        
        for line in env_lines:
            if line.startswith('# XERO_ACCESS_TOKEN='):
                updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
                found_access = True
            elif line.startswith('# XERO_TENANT_ID='):
                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                found_tenant = True
            else:
                updated_lines.append(line)
        
        if not found_access:
            updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
        if not found_tenant:
            updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
        
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ Tokens saved to .env file")
        
        print("\n" + "=" * 80)
        print("🎉 NEW XERO APP INTEGRATION COMPLETE!")
        print("=" * 80)
        print("✅ NEW Xero app working with correct redirect URI")
        print("✅ Demo Company (US) P&L data retrieved successfully")
        print("✅ Your financial agent can now access live Xero data")
        print("✅ Ready to test full agent with real data!")
        print("\nNext step: Run 'python test_full_agent.py' to see your agent")
        print("work with real Demo Company financial data!")
        print("=" * 80)
        
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 8080 in use. Run: lsof -ti:8080 | xargs kill -9")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()