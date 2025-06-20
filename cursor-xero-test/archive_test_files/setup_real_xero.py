#!/usr/bin/env python3
"""
Easy Xero OAuth2 Setup for Real Accounting Data
This script helps you get proper Xero access tokens for accounting data.
"""

import os
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import requests

class XeroOAuthHandler(BaseHTTPRequestHandler):
    """Handle the OAuth2 callback from Xero."""
    
    def do_GET(self):
        """Handle GET request from Xero OAuth callback."""
        if self.path.startswith('/callback'):
            # Parse the authorization code from the callback
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            if 'code' in query_params:
                self.server.auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                <h1>Success!</h1>
                <p>Authorization code received. You can close this window.</p>
                <p>Check your terminal for the next steps.</p>
                </body>
                </html>
                ''')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No authorization code received</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

class XeroRealDataSetup:
    """Setup real Xero data access."""
    
    def __init__(self):
        self.client_id = os.getenv('XERO_CLIENT_ID')
        self.client_secret = os.getenv('XERO_CLIENT_SECRET')
        self.redirect_uri = "http://localhost:8080/callback"
        self.scopes = [
            "accounting.reports.read",
            "accounting.transactions.read", 
            "accounting.contacts.read",
            "accounting.settings.read"
        ]
        
    def step_1_authorization_url(self):
        """Generate the authorization URL for Xero."""
        print("🚀 STEP 1: XERO OAUTH2 AUTHORIZATION")
        print("=" * 50)
        
        if not self.client_id or not self.client_secret:
            print("❌ Missing Xero credentials in .env file")
            print("   Make sure XERO_CLIENT_ID and XERO_CLIENT_SECRET are set")
            return None
        
        # Generate authorization URL
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': 'financial_forecast_agent'
        }
        
        auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
        
        print("✅ Authorization URL generated:")
        print(f"   {auth_url}")
        print("\n📋 This will grant access to:")
        for scope in self.scopes:
            print(f"   - {scope}")
        
        return auth_url
    
    def step_2_start_callback_server(self):
        """Start local server to receive OAuth callback."""
        print("\n🔧 STEP 2: STARTING CALLBACK SERVER")
        print("=" * 50)
        
        print("Starting local server on http://localhost:8080")
        print("This will receive the authorization code from Xero...")
        
        server = HTTPServer(('localhost', 8080), XeroOAuthHandler)
        server.auth_code = None
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return server
    
    def step_3_exchange_code_for_tokens(self, auth_code):
        """Exchange authorization code for access and refresh tokens."""
        print("\n🔄 STEP 3: EXCHANGING CODE FOR TOKENS")
        print("=" * 50)
        
        token_url = "https://identity.xero.com/connect/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                tokens = response.json()
                print("✅ Successfully obtained tokens!")
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
    
    def step_4_get_connections(self, access_token):
        """Get available Xero connections/tenants."""
        print("\n🏢 STEP 4: GETTING XERO CONNECTIONS")
        print("=" * 50)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get('https://api.xero.com/connections', headers=headers)
            
            if response.status_code == 200:
                connections = response.json()
                print(f"✅ Found {len(connections)} Xero organisation(s):")
                
                for i, conn in enumerate(connections):
                    print(f"   {i+1}. {conn.get('tenantName', 'Unknown')}")
                    print(f"      ID: {conn.get('tenantId')}")
                    print(f"      Type: {conn.get('tenantType')}")
                
                return connections
            else:
                print(f"❌ Failed to get connections: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting connections: {e}")
            return None
    
    def step_5_test_accounting_data(self, access_token, tenant_id):
        """Test getting real accounting data."""
        print("\n📊 STEP 5: TESTING REAL ACCOUNTING DATA")
        print("=" * 50)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'xero-tenant-id': tenant_id
        }
        
        # Test 1: Organisation info
        print("Testing organisation info...")
        try:
            org_response = requests.get('https://api.xero.com/api.xro/2.0/Organisation', headers=headers)
            if org_response.status_code == 200:
                org_data = org_response.json()
                org = org_data['Organisations'][0]
                print(f"✅ Organisation: {org.get('Name')}")
                print(f"   Country: {org.get('CountryCode')}")
                print(f"   Currency: {org.get('BaseCurrency')}")
            else:
                print(f"❌ Organisation request failed: {org_response.status_code}")
        except Exception as e:
            print(f"❌ Error getting organisation: {e}")
        
        # Test 2: Profit & Loss report
        print("\nTesting Profit & Loss report...")
        try:
            pl_response = requests.get('https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss', headers=headers)
            if pl_response.status_code == 200:
                pl_data = pl_response.json()
                print("🎉 SUCCESS: Got real P&L data!")
                
                report = pl_data['Reports'][0]
                print(f"   Report: {report.get('ReportName')}")
                print(f"   Period: {report.get('ReportDate')}")
                
                # Try to extract revenue
                rows = report.get('Rows', [])
                for row in rows:
                    if 'Revenue' in row.get('Title', ''):
                        cells = row.get('Cells', [])
                        if cells and len(cells) > 1:
                            print(f"   Revenue: {cells[1].get('Value', 'N/A')}")
                
                return pl_data
            else:
                print(f"❌ P&L request failed: {pl_response.status_code}")
                print(f"   Response: {pl_response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting P&L: {e}")
            return None
    
    def step_6_save_tokens(self, tokens, tenant_id):
        """Save tokens to .env file for agent use."""
        print("\n💾 STEP 6: SAVING TOKENS FOR AGENT USE")
        print("=" * 50)
        
        # Read current .env file
        env_file = '.env'
        env_lines = []
        
        try:
            with open(env_file, 'r') as f:
                env_lines = f.readlines()
        except FileNotFoundError:
            print("❌ .env file not found")
            return
        
        # Update or add tokens
        updated_lines = []
        found_access_token = False
        found_tenant_id = False
        
        for line in env_lines:
            if line.startswith('XERO_ACCESS_TOKEN='):
                updated_lines.append(f'XERO_ACCESS_TOKEN={tokens["access_token"]}\n')
                found_access_token = True
            elif line.startswith('XERO_TENANT_ID='):
                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                found_tenant_id = True
            else:
                updated_lines.append(line)
        
        # Add new entries if not found
        if not found_access_token:
            updated_lines.append(f'XERO_ACCESS_TOKEN={tokens["access_token"]}\n')
        if not found_tenant_id:
            updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
        
        # Also save refresh token
        updated_lines.append(f'XERO_REFRESH_TOKEN={tokens["refresh_token"]}\n')
        
        # Write back to file
        try:
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print("✅ Tokens saved to .env file:")
            print(f"   XERO_ACCESS_TOKEN={tokens['access_token'][:20]}...")
            print(f"   XERO_TENANT_ID={tenant_id}")
            print(f"   XERO_REFRESH_TOKEN={tokens['refresh_token'][:20]}...")
            
        except Exception as e:
            print(f"❌ Error saving to .env file: {e}")

def main():
    """Main setup function - interactive OAuth2 flow."""
    print("🔑 XERO REAL DATA SETUP - OAUTH2 FLOW")
    print("=" * 60)
    print("This will set up real Xero accounting data access for your agent.\n")
    
    setup = XeroRealDataSetup()
    
    # Step 1: Generate authorization URL
    auth_url = setup.step_1_authorization_url()
    if not auth_url:
        return
    
    # Step 2: Start callback server
    server = setup.step_2_start_callback_server()
    
    # Step 3: Open browser for user authorization
    print(f"\n🌐 Opening browser for Xero authorization...")
    print("   If browser doesn't open, copy this URL:")
    print(f"   {auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for authorization code
    print("\n⏳ Waiting for authorization (complete the login in your browser)...")
    
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Timeout waiting for authorization")
        server.shutdown()
        return
    
    print(f"✅ Authorization code received: {server.auth_code[:20]}...")
    server.shutdown()
    
    # Step 4: Exchange code for tokens
    tokens = setup.step_3_exchange_code_for_tokens(server.auth_code)
    if not tokens:
        return
    
    # Step 5: Get connections
    connections = setup.step_4_get_connections(tokens['access_token'])
    if not connections:
        return
    
    # Use first connection (or let user choose)
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"\n🎯 Using organisation: {tenant_name}")
    
    # Step 6: Test real data
    real_data = setup.step_5_test_accounting_data(tokens['access_token'], tenant_id)
    
    # Step 7: Save tokens
    setup.step_6_save_tokens(tokens, tenant_id)
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Your agent can now access real Xero accounting data")
    print("✅ Tokens have been saved to your .env file")
    print("✅ Run your agent now to see real financial data")
    print("\nNext steps:")
    print("1. Run: python test_full_agent.py")
    print("2. Check that Xero data shows 'Live Xero API' as data source")
    print("3. Enjoy real financial forecasting!")

if __name__ == "__main__":
    main()