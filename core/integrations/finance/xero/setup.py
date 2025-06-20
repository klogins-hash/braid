#!/usr/bin/env python3
"""
Xero Integration Setup - Easy First-Time Configuration
Handles OAuth2 flow and saves credentials to .env file
"""

import os
import sys
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from pathlib import Path


class XeroAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback."""
    
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query:
                self.server.auth_code = query['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                success_page = """
                <html>
                <head><title>Xero Integration Setup Complete</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>✅ Success!</h1>
                    <p>Xero integration setup complete. You can close this window.</p>
                    <p>Your Xero credentials have been saved securely.</p>
                </body>
                </html>
                """
                self.wfile.write(success_page.encode())
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress server logs


def find_env_file():
    """Find the closest .env file in current or parent directories."""
    current_path = Path.cwd()
    for path in [current_path] + list(current_path.parents):
        env_file = path / '.env'
        if env_file.exists():
            return env_file
    
    # If no .env found, create one in current directory
    return current_path / '.env'


def update_env_file(env_file_path, credentials):
    """Update .env file with Xero credentials."""
    
    # Read existing content
    content = ""
    if env_file_path.exists():
        with open(env_file_path, 'r') as f:
            content = f.read()
    
    # Define new credentials
    new_creds = {
        'XERO_CLIENT_ID': credentials['client_id'],
        'XERO_CLIENT_SECRET': credentials['client_secret'],
        'XERO_ACCESS_TOKEN': credentials['access_token'],
        'XERO_TENANT_ID': credentials['tenant_id'],
        'XERO_REFRESH_TOKEN': credentials.get('refresh_token', ''),
        'XERO_REDIRECT_URI': credentials['redirect_uri']
    }
    
    # Update or add each credential
    lines = content.split('\n')
    updated_keys = set()
    
    for i, line in enumerate(lines):
        for key, value in new_creds.items():
            if line.startswith(f"{key}=") or line.startswith(f"# {key}="):
                lines[i] = f"{key}={value}"
                updated_keys.add(key)
                break
    
    # Add any missing credentials
    for key, value in new_creds.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}")
    
    # Write updated content
    with open(env_file_path, 'w') as f:
        f.write('\n'.join(lines))


def setup_xero_integration(client_id=None, client_secret=None, auto_open_browser=True):
    """
    Set up Xero integration with OAuth2 flow.
    
    Args:
        client_id: Xero app client ID (will prompt if not provided)
        client_secret: Xero app client secret (will prompt if not provided)
        auto_open_browser: Whether to automatically open browser for auth
    
    Returns:
        dict: Credentials dictionary with tokens
    """
    
    print("🔑 XERO INTEGRATION SETUP")
    print("=" * 60)
    print("This will set up Xero API access for your Braid agent.")
    print()
    
    # Get client credentials
    if not client_id:
        print("📋 First, you need a Xero app. Create one at:")
        print("   https://developer.xero.com/app/manage")
        print()
        print("📝 Make sure to set the redirect URI to:")
        print("   http://localhost:8080/callback")
        print()
        client_id = input("Enter your Xero Client ID: ").strip()
    
    if not client_secret:
        client_secret = input("Enter your Xero Client Secret: ").strip()
    
    if not client_id or not client_secret:
        raise ValueError("Client ID and Client Secret are required")
    
    redirect_uri = 'http://localhost:8080/callback'
    
    # OAuth2 parameters
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'braid_setup'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("\n🚀 Starting OAuth2 flow...")
    print("📋 Scopes requested:")
    print("   - accounting.reports.read (P&L, Balance Sheet)")
    print("   - accounting.transactions.read (Transaction details)")
    print("   - accounting.contacts.read (Customer data)")
    print("   - accounting.settings.read (Organization info)")
    print()
    
    # Start callback server
    server = HTTPServer(('localhost', 8080), XeroAuthHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    print("🔧 Callback server started on http://localhost:8080")
    
    if auto_open_browser:
        print("🌐 Opening browser for Xero authorization...")
        webbrowser.open(auth_url)
    else:
        print("🔗 Please open this URL in your browser:")
        print(f"   {auth_url}")
    
    print("⏳ Waiting for authorization...")
    print("   (Complete the login process in your browser)")
    
    # Wait for authorization
    timeout = 120  # 2 minutes
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    server.shutdown()
    
    if server.auth_code is None:
        raise TimeoutError("Authorization timeout. Please try again.")
    
    print("✅ Authorization successful!")
    
    # Exchange code for tokens
    print("🔄 Exchanging authorization code for access tokens...")
    
    token_response = requests.post(
        'https://identity.xero.com/connect/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': server.auth_code,
            'redirect_uri': redirect_uri
        },
        timeout=30
    )
    
    if token_response.status_code != 200:
        raise Exception(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token', '')
    
    # Get tenant information
    print("🏢 Getting organization information...")
    
    conn_response = requests.get(
        'https://api.xero.com/connections',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=30
    )
    
    if conn_response.status_code != 200:
        raise Exception(f"Failed to get organization info: {conn_response.status_code}")
    
    connections = conn_response.json()
    if not connections:
        raise Exception("No Xero organizations found")
    
    # Use first organization
    org = connections[0]
    tenant_id = org['tenantId']
    tenant_name = org.get('tenantName', 'Unknown Organization')
    
    print(f"✅ Connected to: {tenant_name}")
    
    # Prepare credentials
    credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'tenant_id': tenant_id,
        'redirect_uri': redirect_uri
    }
    
    # Save to .env file
    env_file = find_env_file()
    print(f"💾 Saving credentials to: {env_file}")
    
    update_env_file(env_file, credentials)
    
    print("\n🎉 Xero integration setup complete!")
    print("=" * 60)
    print("✅ Credentials saved to .env file")
    print("✅ Ready to use Xero tools in your agent")
    print()
    print("📚 Available tools:")
    print("   - get_xero_profit_and_loss")
    print("   - get_xero_balance_sheet") 
    print("   - get_xero_trial_balance")
    print()
    print("🔄 Note: Access tokens expire after 30 minutes.")
    print("   Re-run this setup if you get authentication errors.")
    
    return credentials


def test_xero_connection():
    """Test the Xero connection with current credentials."""
    
    print("🧪 Testing Xero connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        access_token = os.getenv('XERO_ACCESS_TOKEN')
        tenant_id = os.getenv('XERO_TENANT_ID')
        
        if not access_token or not tenant_id:
            print("❌ No Xero credentials found. Run setup first.")
            return False
        
        # Test API call
        headers = {
            'Authorization': f'Bearer {access_token}',
            'xero-tenant-id': tenant_id,
            'Accept': 'application/json'
        }
        
        response = requests.get(
            'https://api.xero.com/api.xro/2.0/Organisation',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            org_data = response.json()
            org_name = org_data['Organisations'][0]['Name']
            print(f"✅ Connection successful! Connected to: {org_name}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            if response.status_code == 401:
                print("   Tokens may have expired. Re-run setup.")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main():
    """CLI interface for Xero setup."""
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_xero_connection()
        return
    
    try:
        setup_xero_integration()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()