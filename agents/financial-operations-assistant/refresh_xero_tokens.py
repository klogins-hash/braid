#!/usr/bin/env python3
"""
Refresh Xero tokens for Financial Operations Assistant
Simple OAuth2 flow to get fresh tokens
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
                self.wfile.write(b'<html><body><h1>Success! Close this window and return to terminal.</h1></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    """Get fresh Xero tokens."""
    
    print("🔑 REFRESHING XERO TOKENS FOR FINANCIAL ASSISTANT")
    print("="*60)
    
    # Use existing app credentials
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    redirect_uri = 'http://localhost:8080/callback'
    
    if not client_id or not client_secret:
        print("❌ Missing XERO_CLIENT_ID or XERO_CLIENT_SECRET in .env file")
        print("Please add these to your .env file first")
        return
    
    # OAuth2 flow
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'financial_assistant'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Starting OAuth2 flow...")
    print("📱 Opening browser for Xero authorization...")
    
    # Start server
    server = HTTPServer(('localhost', 8080), TokenHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    webbrowser.open(auth_url)
    print("⏳ Waiting for authorization (90 seconds timeout)...")
    
    # Wait for auth
    timeout = 90
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if server.auth_code is None:
        print("❌ Authorization timeout - please try again")
        server.shutdown()
        return
    
    print("✅ Authorization successful! Getting tokens...")
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
        print(f"❌ Token request failed: {token_response.text}")
        return
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    
    # Get connections
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if conn_response.status_code != 200:
        print(f"❌ Connections request failed: {conn_response.text}")
        return
    
    connections = conn_response.json()
    if not connections:
        print("❌ No Xero organizations found")
        return
        
    tenant_id = connections[0]['tenantId']
    tenant_name = connections[0].get('tenantName', 'Unknown')
    
    print(f"✅ Connected to: {tenant_name}")
    print(f"🔑 Access Token: {access_token[:50]}...")
    print(f"🏢 Tenant ID: {tenant_id}")
    
    # Update .env file
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return
        
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Find and replace token lines
    lines = content.split('\n')
    token_updated = False
    tenant_updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('XERO_ACCESS_TOKEN='):
            lines[i] = f"XERO_ACCESS_TOKEN={access_token}"
            token_updated = True
        elif line.startswith('XERO_TENANT_ID='):
            lines[i] = f"XERO_TENANT_ID={tenant_id}"
            tenant_updated = True
    
    # Add lines if they don't exist
    if not token_updated:
        lines.append(f"XERO_ACCESS_TOKEN={access_token}")
    if not tenant_updated:
        lines.append(f"XERO_TENANT_ID={tenant_id}")
    
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Updated .env file with fresh tokens")
    print(f"🎉 Ready to test Financial Operations Assistant with real Xero data!")
    print("\nNext steps:")
    print("1. python simple_test.py  # Test with real data")
    print("2. python agent.py        # Run interactive agent")

if __name__ == "__main__":
    main()