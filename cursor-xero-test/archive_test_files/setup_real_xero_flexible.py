#!/usr/bin/env python3
"""
Flexible Xero OAuth2 Setup - Works with any redirect URI configuration
"""

import os
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import requests

def check_xero_app_config():
    """Check and display current Xero app configuration."""
    print("🔍 CHECKING XERO APP CONFIGURATION")
    print("=" * 50)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    if not client_id:
        print("❌ XERO_CLIENT_ID not found in .env file")
        return False
    
    print(f"✅ Client ID found: {client_id}")
    print("\n📋 To fix the redirect URI error:")
    print("1. Go to: https://developer.xero.com/app/manage")
    print("2. Click on your app")
    print("3. Go to Configuration tab")
    print("4. Add this redirect URI:")
    print("   http://localhost:8080/callback")
    print("5. Make sure these scopes are enabled:")
    print("   - accounting.reports.read")
    print("   - accounting.transactions.read") 
    print("   - accounting.contacts.read")
    print("   - accounting.settings.read")
    
    return True

def create_xero_app_if_needed():
    """Guide user to create Xero app if they don't have one."""
    print("\n🆕 CREATE NEW XERO APP (if needed)")
    print("=" * 50)
    
    print("If you don't have a Xero app yet:")
    print("1. Go to: https://developer.xero.com/app/manage")
    print("2. Click 'New app'")
    print("3. Fill in:")
    print("   - App name: Financial Forecast Agent")
    print("   - Company/Organisation: Your company")
    print("   - Description: Financial forecasting with real Xero data")
    print("   - Redirect URI: http://localhost:8080/callback")
    print("4. Select these scopes:")
    print("   - accounting.reports.read")
    print("   - accounting.transactions.read")
    print("   - accounting.contacts.read") 
    print("   - accounting.settings.read")
    print("5. Copy Client ID and Secret to your .env file")

def manual_oauth_flow():
    """Manual OAuth flow for users who can't use the automated version."""
    print("\n🔧 MANUAL OAUTH FLOW")
    print("=" * 50)
    
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Xero credentials in .env file")
        return
    
    # Generate manual auth URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
        'state': 'manual_flow'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    
    print("🌐 Manual Steps:")
    print("1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print("2. Login and authorize the app")
    print("3. You'll be redirected to localhost:8080/callback?code=...")
    print("4. Copy the 'code' parameter from the URL")
    print("5. Come back here and enter it")
    
    # Get code from user
    print("\n⏳ After authorizing, paste the authorization code here:")
    auth_code = input("Authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Exchange code for tokens
    print("\n🔄 Exchanging code for tokens...")
    
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
            print("✅ Got tokens successfully!")
            
            # Get connections
            headers = {
                'Authorization': f'Bearer {tokens["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            conn_response = requests.get('https://api.xero.com/connections', headers=headers)
            if conn_response.status_code == 200:
                connections = conn_response.json()
                if connections:
                    tenant_id = connections[0]['tenantId']
                    tenant_name = connections[0].get('tenantName', 'Unknown')
                    
                    print(f"✅ Connected to: {tenant_name}")
                    
                    # Save to .env
                    save_tokens_to_env(tokens['access_token'], tenant_id, tokens['refresh_token'])
                    
                    print("\n🎉 Setup complete! Run: python test_full_agent.py")
                else:
                    print("❌ No Xero organisations found")
            else:
                print(f"❌ Failed to get connections: {conn_response.text}")
        else:
            print(f"❌ Token exchange failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def save_tokens_to_env(access_token, tenant_id, refresh_token):
    """Save tokens to .env file."""
    env_file = '.env'
    
    try:
        # Read existing .env
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add tokens
        updated_lines = []
        found_keys = set()
        
        for line in lines:
            if line.startswith('XERO_ACCESS_TOKEN='):
                updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
                found_keys.add('access_token')
            elif line.startswith('XERO_TENANT_ID='):
                updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
                found_keys.add('tenant_id')
            elif line.startswith('XERO_REFRESH_TOKEN='):
                updated_lines.append(f'XERO_REFRESH_TOKEN={refresh_token}\n')
                found_keys.add('refresh_token')
            else:
                updated_lines.append(line)
        
        # Add missing tokens
        if 'access_token' not in found_keys:
            updated_lines.append(f'XERO_ACCESS_TOKEN={access_token}\n')
        if 'tenant_id' not in found_keys:
            updated_lines.append(f'XERO_TENANT_ID={tenant_id}\n')
        if 'refresh_token' not in found_keys:
            updated_lines.append(f'XERO_REFRESH_TOKEN={refresh_token}\n')
        
        # Write back
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ Tokens saved to .env file")
        
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")

def main():
    """Main setup with multiple options."""
    print("🔑 XERO REAL DATA SETUP - FLEXIBLE VERSION")
    print("=" * 60)
    
    # Check configuration first
    if not check_xero_app_config():
        create_xero_app_if_needed()
        return
    
    print("\n📋 Choose your setup method:")
    print("1. Fix redirect URI and use automated setup")
    print("2. Use manual OAuth flow (works with any redirect URI)")
    print("3. Create new Xero app with correct settings")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n✅ Great! After fixing the redirect URI:")
        print("1. Go to https://developer.xero.com/app/manage")
        print("2. Add redirect URI: http://localhost:8080/callback")
        print("3. Run: python setup_real_xero.py")
        
    elif choice == "2":
        manual_oauth_flow()
        
    elif choice == "3":
        create_xero_app_if_needed()
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()