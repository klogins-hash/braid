#!/usr/bin/env python3
"""
Simple Xero OAuth Setup
Manual OAuth flow that doesn't require callback server setup
"""

import os
import json
import base64
import urllib.parse
import requests

from dotenv import load_dotenv
load_dotenv('../.env')

def get_auth_url():
    """Generate the Xero authorization URL for manual OAuth"""
    client_id = os.getenv('XERO_CLIENT_ID')
    
    if not client_id:
        print("❌ XERO_CLIENT_ID not found in .env file")
        return None
    
    # Use a simple redirect URI that doesn't require server setup
    redirect_uri = "https://developer.xero.com/myapps"  # Standard Xero developer redirect
    scope = "accounting.contacts accounting.settings accounting.transactions"
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': 'xero_oauth_state'
    }
    
    auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
    return auth_url, redirect_uri

def exchange_code_for_token(authorization_code, redirect_uri):
    """Exchange authorization code for access token"""
    client_id = os.getenv('XERO_CLIENT_ID')
    client_secret = os.getenv('XERO_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ XERO_CLIENT_ID or XERO_CLIENT_SECRET not found in .env file")
        return None
    
    token_url = "https://identity.xero.com/connect/token"
    
    # Create Basic Auth header
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }
    
    print(f"🔄 Exchanging authorization code for access token...")
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 1800)
        
        print("✅ Successfully obtained Xero access token!")
        print(f"   Access Token: {access_token[:50]}...")
        print(f"   Expires in: {expires_in} seconds")
        
        # Save tokens
        token_info = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': time.time() + expires_in,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        with open('xero_tokens.json', 'w') as f:
            json.dump(token_info, f, indent=2)
        
        print(f"💾 Tokens saved to xero_tokens.json")
        
        # Test the token
        test_api_connection(access_token)
        
        return token_data
    else:
        print(f"❌ Error exchanging code for token: {response.status_code}")
        print(response.text)
        return None

def test_api_connection(access_token):
    """Test the API connection with the new token"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get('https://api.xero.com/connections', headers=headers)
    
    if response.status_code == 200:
        connections = response.json()
        print(f"✅ API Test Successful! Found {len(connections)} connections")
        
        if connections:
            for conn in connections:
                print(f"   📋 Tenant: {conn.get('tenantName', 'Unknown')}")
                print(f"   🆔 Tenant ID: {conn.get('tenantId', 'Unknown')}")
                print(f"   📊 Type: {conn.get('tenantType', 'Unknown')}")
        
        return True
    else:
        print(f"❌ API Test Failed: {response.status_code}")
        print(response.text[:200])
        return False

def main():
    """Main function for manual OAuth flow"""
    print("🚀 XERO SIMPLE OAUTH SETUP")
    print("=" * 45)
    
    # Step 1: Generate auth URL
    result = get_auth_url()
    if not result:
        return
    
    auth_url, redirect_uri = result
    
    print(f"📋 MANUAL OAUTH STEPS:")
    print(f"1. Open this URL in your browser:")
    print(f"   {auth_url}")
    print(f"")
    print(f"2. Log in to Xero and authorize the application")
    print(f"3. After authorization, you'll be redirected to:")
    print(f"   https://developer.xero.com/myapps")
    print(f"4. Look at the URL in your browser - it will contain a 'code' parameter")
    print(f"5. Copy the code value (after 'code=') and paste it below")
    print(f"")
    
    # Step 2: Get authorization code from user
    try:
        auth_code = input("📝 Enter the authorization code from the URL: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return
        
        # Step 3: Exchange code for token
        token_data = exchange_code_for_token(auth_code, redirect_uri)
        
        if token_data:
            print(f"\n🎉 XERO OAUTH SETUP COMPLETE!")
            print(f"✅ Access token obtained and tested")
            print(f"💾 Tokens saved to xero_tokens.json")
            print(f"🚀 You can now run the financial agent with live Xero data!")
            print(f"")
            print(f"📋 NEXT STEPS:")
            print(f"   python run_complete_live_traced.py")
        else:
            print(f"❌ Failed to obtain access token")
    
    except KeyboardInterrupt:
        print(f"\n⏹️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import time
    main()