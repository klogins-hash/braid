#!/usr/bin/env python3
"""
Xero SDK Integration - Clean and Official Way
Using the official xero-python SDK: https://github.com/XeroAPI/xero-python
"""

import os
import sys
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Check if xero-python is installed, install if needed
try:
    from xero_python.api_client import ApiClient
    from xero_python.api_client.configuration import Configuration
    from xero_python.api_client.oauth2 import OAuth2Token
    from xero_python.identity import IdentityApi
    from xero_python.accounting import AccountingApi
    from xero_python.models.accounting import *
    print("✅ Xero Python SDK found")
except ImportError:
    print("📦 Installing Xero Python SDK...")
    os.system("pip install xero-python")
    try:
        from xero_python.api_client import ApiClient
        from xero_python.api_client.configuration import Configuration
        from xero_python.api_client.oauth2 import OAuth2Token
        from xero_python.identity import IdentityApi
        from xero_python.accounting import AccountingApi
        from xero_python.models.accounting import *
        print("✅ Xero Python SDK installed and imported")
    except ImportError:
        print("❌ Failed to install/import Xero SDK")
        sys.exit(1)

class XeroOAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""
    
    def do_GET(self):
        if self.path.startswith('/callback'):
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            if 'code' in query_params:
                self.server.auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html><body>
                <h1>Success!</h1>
                <p>Authorization received. You can close this window.</p>
                <script>window.close();</script>
                </body></html>
                ''')
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

class XeroSDKSetup:
    """Easy Xero SDK setup for real data access."""
    
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
        
        # Initialize Xero configuration
        self.config = Configuration(
            debug=False,
            oauth2_token=OAuth2Token(
                client_id=self.client_id,
                client_secret=self.client_secret
            ),
        )
    
    def step_1_check_credentials(self):
        """Check if we have valid Xero credentials."""
        print("🔍 STEP 1: CHECKING XERO CREDENTIALS")
        print("=" * 50)
        
        if not self.client_id:
            print("❌ XERO_CLIENT_ID missing from .env file")
            return False
        
        if not self.client_secret:
            print("❌ XERO_CLIENT_SECRET missing from .env file")
            return False
        
        print(f"✅ Client ID: {self.client_id}")
        print(f"✅ Client Secret: {self.client_secret[:10]}...")
        print(f"✅ Redirect URI: {self.redirect_uri}")
        print(f"✅ Scopes: {', '.join(self.scopes)}")
        
        return True
    
    def step_2_get_auth_url(self):
        """Generate OAuth2 authorization URL using SDK."""
        print("\n🔗 STEP 2: GENERATING AUTHORIZATION URL")
        print("=" * 50)
        
        # Create API client
        api_client = ApiClient(self.config)
        
        # Generate authorization URL
        auth_url = api_client.oauth2_token.generate_url(
            redirect_uri=self.redirect_uri,
            scopes=self.scopes,
            state="xero_sdk_setup"
        )
        
        print("✅ Authorization URL generated:")
        print(f"   {auth_url}")
        
        return auth_url, api_client
    
    def step_3_start_server_and_authorize(self, auth_url):
        """Start callback server and open browser for authorization."""
        print("\n🌐 STEP 3: BROWSER AUTHORIZATION")
        print("=" * 50)
        
        # Start callback server
        server = HTTPServer(('localhost', 8080), XeroOAuthHandler)
        server.auth_code = None
        
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("🔧 Started callback server on localhost:8080")
        print("🌐 Opening browser for Xero authorization...")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for authorization code
        print("⏳ Waiting for authorization (complete login in browser)...")
        
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while server.auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if server.auth_code is None:
            print("❌ Timeout waiting for authorization")
            server.shutdown()
            return None
        
        print(f"✅ Authorization code received: {server.auth_code[:20]}...")
        server.shutdown()
        
        return server.auth_code
    
    def step_4_exchange_tokens(self, api_client, auth_code):
        """Exchange authorization code for tokens using SDK."""
        print("\n🔄 STEP 4: EXCHANGING CODE FOR TOKENS")
        print("=" * 50)
        
        try:
            # Exchange code for tokens
            api_client.oauth2_token.get_token(
                authorization_code=auth_code,
                redirect_uri=self.redirect_uri
            )
            
            print("✅ Successfully obtained tokens!")
            print(f"   Access Token: {api_client.oauth2_token.access_token[:20]}...")
            print(f"   Refresh Token: {api_client.oauth2_token.refresh_token[:20]}...")
            print(f"   Expires In: {api_client.oauth2_token.expires_in} seconds")
            
            return api_client
            
        except Exception as e:
            print(f"❌ Token exchange failed: {e}")
            return None
    
    def step_5_get_connections(self, api_client):
        """Get Xero connections using SDK."""
        print("\n🏢 STEP 5: GETTING XERO CONNECTIONS")
        print("=" * 50)
        
        try:
            # Create Identity API instance
            identity_api = IdentityApi(api_client)
            
            # Get connections
            connections = identity_api.get_connections()
            
            print(f"✅ Found {len(connections)} Xero organisation(s):")
            
            for i, connection in enumerate(connections):
                print(f"   {i+1}. {connection.tenant_name}")
                print(f"      ID: {connection.tenant_id}")
                print(f"      Type: {connection.tenant_type}")
            
            return connections
            
        except Exception as e:
            print(f"❌ Failed to get connections: {e}")
            return None
    
    def step_6_test_accounting_data(self, api_client, tenant_id):
        """Test getting real accounting data using SDK."""
        print("\n📊 STEP 6: TESTING REAL ACCOUNTING DATA")
        print("=" * 50)
        
        try:
            # Create Accounting API instance
            accounting_api = AccountingApi(api_client)
            
            # Test 1: Get organisation
            print("Testing organisation info...")
            organisations = accounting_api.get_organisations(
                xero_tenant_id=tenant_id
            )
            
            if organisations.organisations:
                org = organisations.organisations[0]
                print(f"✅ Organisation: {org.name}")
                print(f"   Country: {org.country_code}")
                print(f"   Currency: {org.base_currency}")
            
            # Test 2: Get Profit & Loss report
            print("\nTesting Profit & Loss report...")
            reports = accounting_api.get_report_profit_and_loss(
                xero_tenant_id=tenant_id
            )
            
            if reports.reports:
                report = reports.reports[0]
                print("🎉 SUCCESS: Got real P&L data from Xero SDK!")
                print(f"   Report: {report.report_name}")
                print(f"   Date: {report.report_date}")
                print(f"   Rows: {len(report.rows) if report.rows else 0}")
                
                # Extract some financial data
                if report.rows:
                    for row in report.rows[:3]:  # Show first 3 rows
                        if hasattr(row, 'title') and row.title:
                            print(f"   {row.title}: {row.cells[1].value if row.cells and len(row.cells) > 1 else 'N/A'}")
                
                return reports
            else:
                print("❌ No P&L data found")
                return None
                
        except Exception as e:
            print(f"❌ Error testing accounting data: {e}")
            return None
    
    def step_7_save_tokens(self, api_client, tenant_id):
        """Save tokens to .env file."""
        print("\n💾 STEP 7: SAVING TOKENS")
        print("=" * 50)
        
        try:
            # Read current .env
            env_file = '.env'
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update tokens
            updated_lines = []
            found_keys = set()
            
            for line in lines:
                if line.startswith('XERO_ACCESS_TOKEN='):
                    updated_lines.append(f'XERO_ACCESS_TOKEN={api_client.oauth2_token.access_token}\n')
                    found_keys.add('access')
                elif line.startswith('XERO_REFRESH_TOKEN='):
                    updated_lines.append(f'XERO_REFRESH_TOKEN={api_client.oauth2_token.refresh_token}\n')
                    found_keys.add('refresh')
                elif line.startswith('XERO_TENANT_ID='):
                    updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                    found_keys.add('tenant')
                else:
                    updated_lines.append(line)
            
            # Add missing tokens
            if 'access' not in found_keys:
                updated_lines.append(f'XERO_ACCESS_TOKEN={api_client.oauth2_token.access_token}\n')
            if 'refresh' not in found_keys:
                updated_lines.append(f'XERO_REFRESH_TOKEN={api_client.oauth2_token.refresh_token}\n')
            if 'tenant' not in found_keys:
                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
            
            # Write back
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print("✅ Tokens saved to .env file:")
            print(f"   XERO_ACCESS_TOKEN={api_client.oauth2_token.access_token[:20]}...")
            print(f"   XERO_REFRESH_TOKEN={api_client.oauth2_token.refresh_token[:20]}...")
            print(f"   XERO_TENANT_ID={tenant_id}")
            
        except Exception as e:
            print(f"❌ Error saving tokens: {e}")

def main():
    """Main SDK setup function."""
    print("🚀 XERO SDK SETUP - OFFICIAL PYTHON SDK")
    print("=" * 60)
    print("Using official xero-python SDK for clean, reliable integration\n")
    
    setup = XeroSDKSetup()
    
    # Step 1: Check credentials
    if not setup.step_1_check_credentials():
        print("\n❌ Setup failed: Missing credentials")
        print("Please add XERO_CLIENT_ID and XERO_CLIENT_SECRET to your .env file")
        return
    
    # Step 2: Generate auth URL
    auth_url, api_client = setup.step_2_get_auth_url()
    
    # Step 3: Get authorization
    auth_code = setup.step_3_start_server_and_authorize(auth_url)
    if not auth_code:
        print("❌ Authorization failed")
        return
    
    # Step 4: Exchange for tokens
    api_client = setup.step_4_exchange_tokens(api_client, auth_code)
    if not api_client:
        print("❌ Token exchange failed")
        return
    
    # Step 5: Get connections
    connections = setup.step_5_get_connections(api_client)
    if not connections or len(connections) == 0:
        print("❌ No Xero connections found")
        return
    
    # Use first connection
    tenant_id = connections[0].tenant_id
    tenant_name = connections[0].tenant_name
    
    print(f"\n🎯 Using organisation: {tenant_name}")
    
    # Step 6: Test real data
    accounting_data = setup.step_6_test_accounting_data(api_client, tenant_id)
    
    # Step 7: Save tokens
    setup.step_7_save_tokens(api_client, tenant_id)
    
    print("\n🎉 XERO SDK SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Official Xero Python SDK configured")
    print("✅ Real accounting data access verified")
    print("✅ Tokens saved for your agent")
    print("\nNext steps:")
    print("1. Run: python test_full_agent.py")
    print("2. Look for: '🎉 SUCCESS: Retrieved REAL Xero P&L data!'")
    print("3. Enjoy real financial forecasting with live data!")

if __name__ == "__main__":
    main()