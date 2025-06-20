#!/usr/bin/env python3
"""
Test New Xero App - Quick Setup
"""

import os
import sys
import json
import webbrowser
import urllib.parse
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Force reload environment
from dotenv import load_dotenv
load_dotenv(override=True)

class NewOAuthHandler(BaseHTTPRequestHandler):
    """OAuth callback handler."""
    
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
                <h1>SUCCESS!</h1>
                <p>Authorization received. You can close this window.</p>
                <script>setTimeout(function(){window.close();}, 3000);</script>
                </body></html>
                '''
                self.wfile.write(html.encode('utf-8'))
                print("✅ Authorization code received!")
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

def main():
    """Test the new Xero app."""
    print("🆕 TESTING NEW XERO APP")
    print("=" * 50)
    
    # Get NEW credentials
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    print(f"📋 New Credentials:")
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    if not client_id or not client_secret:
        print("❌ No credentials found!")
        return
    
    # Generate auth URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'new_app_test'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print(f"\n🌐 Opening browser for authorization...")
    print(f"URL: {auth_url[:100]}...")
    
    # Start server on different port to avoid conflicts
    print(f"\n🔧 Starting callback server on port 8080...")
    
    try:
        server = HTTPServer(('localhost', 8080), NewOAuthHandler)
        server.auth_code = None
        
        # Start server in background
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ Server started successfully")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for authorization
        print("⏳ Waiting for authorization (complete in browser)...")
        
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while server.auth_code is None and (time.time() - start_time) < timeout:
            time.sleep(1)
        
        if server.auth_code is None:
            print("❌ Timeout waiting for authorization")
            server.shutdown()
            return
        
        print(f"✅ Got authorization code: {server.auth_code[:20]}...")
        server.shutdown()
        
        # Exchange for tokens
        print(f"\n🔄 Exchanging code for tokens...")
        
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
            print("🎉 SUCCESS: Got tokens!")
            print(f"   Access Token: {tokens['access_token'][:20]}...")
            
            # Check if refresh_token exists
            if 'refresh_token' in tokens:
                print(f"   Refresh Token: {tokens['refresh_token'][:20]}...")
            else:
                print("   No refresh token received (may be implicit grant)")
                print(f"   Available keys: {list(tokens.keys())}")
            
            # Get connections
            print(f"\n🏢 Getting Xero connections...")
            
            conn_response = requests.get(
                'https://api.xero.com/connections',
                headers={'Authorization': f'Bearer {tokens["access_token"]}'}
            )
            
            if conn_response.status_code == 200:
                connections = conn_response.json()
                print(f"✅ Found {len(connections)} organisation(s):")
                
                for conn in connections:
                    print(f"   - {conn.get('tenantName', 'Unknown')}")
                    print(f"     ID: {conn.get('tenantId')}")
                
                if connections:
                    tenant_id = connections[0]['tenantId']
                    
                    # Test P&L data
                    print(f"\n📊 Testing P&L data...")
                    
                    pl_response = requests.get(
                        'https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss',
                        headers={
                            'Authorization': f'Bearer {tokens["access_token"]}',
                            'xero-tenant-id': tenant_id
                        }
                    )
                    
                    if pl_response.status_code == 200:
                        print("🎉 SUCCESS: Retrieved REAL Xero P&L data!")
                        
                        pl_data = pl_response.json()
                        if 'Reports' in pl_data:
                            report = pl_data['Reports'][0]
                            print(f"   Report: {report.get('ReportName')}")
                            print(f"   Date: {report.get('ReportDate')}")
                            print(f"   Rows: {len(report.get('Rows', []))}")
                        
                        # Save tokens to .env
                        print(f"\n💾 Saving tokens to .env...")
                        
                        # Read current .env
                        with open('.env', 'r') as f:
                            lines = f.readlines()
                        
                        # Update tokens
                        updated_lines = []
                        found_tokens = set()
                        
                        for line in lines:
                            if line.startswith('XERO_ACCESS_TOKEN='):
                                updated_lines.append(f'XERO_ACCESS_TOKEN={tokens["access_token"]}\n')
                                found_tokens.add('access')
                            elif line.startswith('XERO_REFRESH_TOKEN='):
                                if 'refresh_token' in tokens:
                                    updated_lines.append(f'XERO_REFRESH_TOKEN={tokens["refresh_token"]}\n')
                                    found_tokens.add('refresh')
                                else:
                                    updated_lines.append(line)  # Keep existing line if no new refresh token
                            elif line.startswith('XERO_TENANT_ID='):
                                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                                found_tokens.add('tenant')
                            else:
                                updated_lines.append(line)
                        
                        # Add missing tokens
                        if 'access' not in found_tokens:
                            updated_lines.append(f'XERO_ACCESS_TOKEN={tokens["access_token"]}\n')
                        if 'refresh' not in found_tokens and 'refresh_token' in tokens:
                            updated_lines.append(f'XERO_REFRESH_TOKEN={tokens["refresh_token"]}\n')
                        if 'tenant' not in found_tokens:
                            updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                        
                        # Write back
                        with open('.env', 'w') as f:
                            f.writelines(updated_lines)
                        
                        print("✅ Tokens saved!")
                        
                        print(f"\n🎉 SETUP COMPLETE!")
                        print("=" * 50)
                        print("✅ New Xero app working perfectly!")
                        print("✅ Real P&L data access confirmed!")
                        print("✅ Tokens saved for your agent!")
                        print("\nNext: Run python test_full_agent.py")
                        
                    else:
                        print(f"❌ P&L request failed: {pl_response.status_code}")
                        print(f"   Response: {pl_response.text}")
                        
            else:
                print(f"❌ Connections request failed: {conn_response.status_code}")
        else:
            print(f"❌ Token exchange failed: {token_response.status_code}")
            print(f"   Response: {token_response.text}")
            
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 8080 is in use. Trying different port...")
            print("Run: lsof -ti:8080 | xargs kill -9")
            print("Then try again.")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()