#!/usr/bin/env python3
"""
Xero OAuth Setup
Handles the OAuth flow to get fresh access tokens for Xero API integration
"""

import os
import json
import base64
import urllib.parse
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

from dotenv import load_dotenv
load_dotenv('../.env')

class XeroOAuthHandler:
    def __init__(self):
        self.client_id = os.getenv('XERO_CLIENT_ID')
        self.client_secret = os.getenv('XERO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('XERO_REDIRECT_URI', 'http://localhost:8080/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("XERO_CLIENT_ID and XERO_CLIENT_SECRET must be set in .env file")
        
        self.authorization_code = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        
    def get_auth_url(self):
        """Generate the Xero authorization URL"""
        scope = "accounting.contacts accounting.settings accounting.transactions"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': 'xero_oauth_state'
        }
        
        auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        token_url = "https://identity.xero.com/connect/token"
        
        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.expires_at = time.time() + token_data.get('expires_in', 1800)
            
            print("✅ Successfully obtained Xero access token!")
            print(f"   Access Token: {self.access_token[:50]}...")
            print(f"   Expires in: {token_data.get('expires_in', 'unknown')} seconds")
            
            return token_data
        else:
            print(f"❌ Error exchanging code for token: {response.status_code}")
            print(response.text)
            return None
    
    def test_api_connection(self):
        """Test the API connection with the new token"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.xero.com/connections', headers=headers)
        
        if response.status_code == 200:
            connections = response.json()
            print(f"✅ API Test Successful! Found {len(connections)} connections")
            
            if connections:
                for conn in connections:
                    print(f"   Tenant: {conn.get('tenantName', 'Unknown')}")
                    print(f"   Tenant ID: {conn.get('tenantId', 'Unknown')}")
                    print(f"   Type: {conn.get('tenantType', 'Unknown')}")
            
            return True
        else:
            print(f"❌ API Test Failed: {response.status_code}")
            print(response.text[:200])
            return False
    
    def save_tokens_to_env(self):
        """Save tokens to a file for use by the financial agent"""
        if not self.access_token:
            print("❌ No tokens to save")
            return
        
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        # Save to a tokens file
        tokens_file = 'xero_tokens.json'
        with open(tokens_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"✅ Tokens saved to {tokens_file}")
        print(f"📋 Add this to your .env file:")
        print(f"XERO_ACCESS_TOKEN={self.access_token}")
        print(f"XERO_REFRESH_TOKEN={self.refresh_token}")

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            # Parse the callback URL
            url_parts = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(url_parts.query)
            
            if 'code' in query_params:
                # Store the authorization code
                self.server.authorization_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <head><title>Xero Authorization Complete</title></head>
                <body>
                    <h1>✅ Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(function(){window.close();}, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                
                # Shutdown the server
                threading.Thread(target=self.server.shutdown).start()
            else:
                # Handle error
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = "<html><body><h1>❌ Authorization Failed</h1></body></html>"
                self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass

def run_oauth_flow():
    """Run the complete OAuth flow"""
    print("🚀 XERO OAUTH SETUP")
    print("=" * 40)
    
    handler = XeroOAuthHandler()
    
    # Step 1: Generate auth URL
    auth_url = handler.get_auth_url()
    print(f"🔗 Authorization URL generated")
    
    # Step 2: Start local server for callback
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.authorization_code = None
    
    print(f"🔄 Starting local callback server on port 8080...")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Step 3: Open browser for user authorization
    print(f"🌐 Opening browser for Xero authorization...")
    print(f"   If browser doesn't open, go to: {auth_url}")
    
    webbrowser.open(auth_url)
    
    # Step 4: Wait for callback
    print(f"⏳ Waiting for authorization (this may take a minute)...")
    
    timeout = 120  # 2 minutes
    start_time = time.time()
    
    while server.authorization_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.authorization_code:
        print(f"✅ Authorization code received!")
        
        # Step 5: Exchange code for token
        token_data = handler.exchange_code_for_token(server.authorization_code)
        
        if token_data:
            # Step 6: Test API connection
            handler.test_api_connection()
            
            # Step 7: Save tokens
            handler.save_tokens_to_env()
            
            print(f"\n🎉 XERO OAUTH SETUP COMPLETE!")
            print(f"✅ Access token obtained and tested")
            print(f"💾 Tokens saved for use by financial agent")
            
            return handler.access_token
        else:
            print(f"❌ Failed to exchange authorization code for token")
            return None
    else:
        print(f"❌ Timeout waiting for authorization")
        return None

def main():
    """Main function"""
    try:
        access_token = run_oauth_flow()
        
        if access_token:
            print(f"\n📋 NEXT STEPS:")
            print(f"1. The financial agent can now use live Xero data")
            print(f"2. Run the complete agent with: python run_complete_live_traced.py")
            print(f"3. Check LangSmith for unified workflow traces")
        else:
            print(f"\n❌ OAuth setup failed")
            print(f"📋 Troubleshooting:")
            print(f"   - Check XERO_CLIENT_ID and XERO_CLIENT_SECRET in .env")
            print(f"   - Ensure redirect URI matches Xero app settings")
            print(f"   - Try running again")
    
    except KeyboardInterrupt:
        print(f"\n⏹️  OAuth setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during OAuth setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()