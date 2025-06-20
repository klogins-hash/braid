#!/usr/bin/env python3
"""
Get fresh Xero tokens for agent testing
"""

import os
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from dotenv import load_dotenv

load_dotenv(override=True)

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! Tokens retrieved.</h1></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    """Get fresh tokens."""
    
    print("🔑 GETTING FRESH XERO TOKENS")
    print("="*50)
    
    client_id = "474346C165654911BFFA8A80C108094D"
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    redirect_uri = 'http://localhost:8080/callback'
    
    if not client_secret:
        print("❌ Missing XERO_CLIENT_SECRET")
        return
    
    # OAuth2 flow
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'get_tokens'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Starting OAuth2 flow...")
    
    # Start server
    server = HTTPServer(('localhost', 8080), TokenHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    
    # Wait for auth
    timeout = 90
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Authorization timeout")
        server.shutdown()
        return
    
    print("✅ Authorization successful")
    server.shutdown()
    
    # Get token
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
        print(f"❌ Token failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    
    # Get connections
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    connections = conn_response.json()
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"✅ Connected to: {tenant_name}")
    print(f"🔑 Access Token: {access_token[:50]}...")
    print(f"🏢 Tenant ID: {tenant_id}")
    
    # Update .env file
    env_file = ".env"
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the commented out token lines
    content = content.replace(
        "# XERO_ACCESS_TOKEN=will be set by OAuth2 flow",
        f"XERO_ACCESS_TOKEN={access_token}"
    )
    content = content.replace(
        "# XERO_TENANT_ID=will be set by OAuth2 flow", 
        f"XERO_TENANT_ID={tenant_id}"
    )
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated .env file with fresh tokens")
    print(f"🎉 Ready to test agent with real Demo Company data!")

if __name__ == "__main__":
    main()