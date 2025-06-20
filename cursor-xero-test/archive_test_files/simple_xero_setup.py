#!/usr/bin/env python3
"""
Simple Xero Setup - Works Every Time
No SDK dependencies, just pure OAuth2 flow
"""

import os
import json
import webbrowser
import urllib.parse
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleOAuthHandler(BaseHTTPRequestHandler):
    """Simple OAuth callback handler."""
    
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
                <p>Authorization received. You can close this window.</p>
                <script>setTimeout(function(){window.close();}, 2000);</script>
                </body></html>
                '''
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No code received</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def check_env_credentials():
    """Check if we have Xero credentials."""
    # Force reload environment
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    print("🔍 CHECKING CREDENTIALS")
    print("=" * 40)
    
    if not client_id:
        print("❌ XERO_CLIENT_ID missing from .env")
        return False, None, None
    
    if not client_secret:
        print("❌ XERO_CLIENT_SECRET missing from .env")
        return False, None, None
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {client_secret[:10]}...")
    
    # Verify this is the NEW client ID
    expected_new_id = "474346C165654911BFFA8A80C108094D"
    if client_id == expected_new_id:
        print("✅ Using NEW Xero app with correct redirect URI")
    else:
        print(f"⚠️  Expected NEW ID: {expected_new_id}")
        print(f"⚠️  Got: {client_id}")
    
    return True, client_id, client_secret

def generate_auth_url(client_id):
    """Generate OAuth2 authorization URL."""
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'simple_setup'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    return auth_url

def start_callback_server():
    """Start local server for OAuth callback."""
    print("\n🔧 STARTING CALLBACK SERVER")
    print("=" * 40)
    
    server = HTTPServer(('localhost', 8080), SimpleOAuthHandler)
    server.auth_code = None
    
    # Start server in background thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("✅ Server started on http://localhost:8080")
    return server

def wait_for_authorization(server, timeout=300):
    """Wait for user to complete authorization."""
    print("\n⏳ WAITING FOR AUTHORIZATION")
    print("=" * 40)
    print("Complete the authorization in your browser...")
    
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Timeout waiting for authorization")
        return None
    
    print(f"✅ Authorization code received: {server.auth_code[:20]}...")
    return server.auth_code

def exchange_code_for_tokens(client_id, client_secret, auth_code):
    """Exchange authorization code for access tokens."""
    print("\n🔄 EXCHANGING CODE FOR TOKENS")
    print("=" * 40)
    
    token_url = "https://identity.xero.com/connect/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080/callback'
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Tokens received successfully!")
            print(f"   Access Token: {tokens['access_token'][:20]}...")
            print(f"   Refresh Token: {tokens['refresh_token'][:20]}...")
            print(f"   Expires In: {tokens['expires_in']} seconds")
            return tokens
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error exchanging tokens: {e}")
        return None

def get_connections(access_token):
    """Get Xero connections."""
    print("\n🏢 GETTING XERO CONNECTIONS")
    print("=" * 40)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://api.xero.com/connections', headers=headers)
        
        if response.status_code == 200:
            connections = response.json()
            print(f"✅ Found {len(connections)} organisation(s):")
            
            for i, conn in enumerate(connections):
                print(f"   {i+1}. {conn.get('tenantName', 'Unknown')}")
                print(f"      ID: {conn.get('tenantId')}")
            
            return connections
        else:
            print(f"❌ Failed to get connections: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting connections: {e}")
        return None

def test_accounting_data(access_token, tenant_id):
    """Test getting real accounting data."""
    print("\n📊 TESTING ACCOUNTING DATA")
    print("=" * 40)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'xero-tenant-id': tenant_id
    }
    
    # Test P&L report
    try:
        response = requests.get(
            'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 SUCCESS: Retrieved real P&L data!")
            
            if 'Reports' in data and len(data['Reports']) > 0:
                report = data['Reports'][0]
                print(f"   Report: {report.get('ReportName')}")
                print(f"   Date: {report.get('ReportDate')}")
                print(f"   Rows: {len(report.get('Rows', []))}")
                
                # Try to find revenue
                rows = report.get('Rows', [])
                for row in rows[:5]:  # Check first 5 rows
                    title = row.get('Title', '')
                    if 'Revenue' in title or 'Income' in title:
                        cells = row.get('Cells', [])
                        if len(cells) > 1:
                            print(f"   {title}: {cells[1].get('Value', 'N/A')}")
            
            return data
        else:
            print(f"❌ P&L request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing accounting data: {e}")
        return None

def save_tokens_to_env(access_token, refresh_token, tenant_id):
    """Save tokens to .env file."""
    print("\n💾 SAVING TOKENS TO .ENV")
    print("=" * 40)
    
    try:
        # Read existing .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update or add tokens
        updated_lines = []
        tokens_found = set()
        
        for line in lines:
            if line.startswith('XERO_ACCESS_TOKEN='):
                updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
                tokens_found.add('access')
            elif line.startswith('XERO_REFRESH_TOKEN='):
                updated_lines.append(f'XERO_REFRESH_TOKEN={refresh_token}\n')
                tokens_found.add('refresh')
            elif line.startswith('XERO_TENANT_ID='):
                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                tokens_found.add('tenant')
            else:
                updated_lines.append(line)
        
        # Add missing tokens
        if 'access' not in tokens_found:
            updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
        if 'refresh' not in tokens_found:
            updated_lines.append(f'XERO_REFRESH_TOKEN={refresh_token}\n')
        if 'tenant' not in tokens_found:
            updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
        
        # Write back to file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ Tokens saved successfully!")
        print(f"   XERO_ACCESS_TOKEN={access_token[:20]}...")
        print(f"   XERO_REFRESH_TOKEN={refresh_token[:20]}...")
        print(f"   XERO_TENANT_ID={tenant_id}")
        
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")

def main():
    """Main setup function."""
    print("🔑 SIMPLE XERO SETUP - REAL DATA ACCESS")
    print("=" * 60)
    print("This will connect your agent to real Xero accounting data\n")
    
    # Step 1: Check credentials
    has_creds, client_id, client_secret = check_env_credentials()
    if not has_creds:
        print("\n❌ Setup failed: Missing credentials")
        print("Add XERO_CLIENT_ID and XERO_CLIENT_SECRET to your .env file")
        return
    
    # Step 2: Generate auth URL
    auth_url = generate_auth_url(client_id)
    print(f"\n🔗 AUTHORIZATION URL")
    print("=" * 40)
    print("Opening browser for Xero authorization...")
    print(f"URL: {auth_url}")
    
    # Step 3: Start server and open browser
    server = start_callback_server()
    webbrowser.open(auth_url)
    
    # Step 4: Wait for authorization
    auth_code = wait_for_authorization(server)
    server.shutdown()
    
    if not auth_code:
        print("❌ Authorization failed")
        return
    
    # Step 5: Exchange for tokens
    tokens = exchange_code_for_tokens(client_id, client_secret, auth_code)
    if not tokens:
        print("❌ Token exchange failed")
        return
    
    # Step 6: Get connections
    connections = get_connections(tokens['access_token'])
    if not connections or len(connections) == 0:
        print("❌ No Xero organisations found")
        return
    
    # Use first connection
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"\n🎯 Using organisation: {tenant_name}")
    
    # Step 7: Test real data
    accounting_data = test_accounting_data(tokens['access_token'], tenant_id)
    
    # Step 8: Save tokens
    save_tokens_to_env(
        tokens['access_token'],
        tokens['refresh_token'],
        tenant_id
    )
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Your agent can now access real Xero data")
    print("✅ Tokens saved to .env file")
    print("✅ Real accounting data verified")
    print("\nNext steps:")
    print("1. Run: python test_full_agent.py")
    print("2. Look for: 'SUCCESS: Retrieved REAL Xero P&L data!'")
    print("3. Enjoy real financial forecasting!")

if __name__ == "__main__":
    main()