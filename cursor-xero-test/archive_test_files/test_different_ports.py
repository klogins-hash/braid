#!/usr/bin/env python3
"""
Test Different Redirect URI Ports to Find What Works
"""

import os
import urllib.parse
import webbrowser
from dotenv import load_dotenv

load_dotenv()

def test_different_redirect_uris():
    """Test different redirect URIs to see which might work."""
    
    client_id = os.getenv('XERO_CLIENT_ID')
    
    if not client_id:
        print("❌ No XERO_CLIENT_ID found")
        return
    
    print("🔍 TESTING DIFFERENT REDIRECT URIS")
    print("=" * 60)
    print(f"Client ID: {client_id}")
    print()
    
    # Common redirect URIs that might be configured
    test_uris = [
        'http://localhost:8080/callback',
        'http://localhost:3000/callback', 
        'http://localhost:5000/callback',
        'http://localhost:8000/callback',
        'http://localhost:4200/callback',
        'http://localhost:3001/callback',
        'https://localhost:8080/callback',
        'http://127.0.0.1:8080/callback',
        'urn:ietf:wg:oauth:2.0:oob',  # Out-of-band flow
    ]
    
    print("Generating test URLs for different redirect URIs:")
    print("(Try these manually to see which one works)")
    print()
    
    for i, redirect_uri in enumerate(test_uris, 1):
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'accounting.reports.read accounting.transactions.read accounting.contacts.read accounting.settings.read',
            'state': f'test_{i}'
        }
        
        auth_url = f"https://login.xero.com/identity/connect/authorize?{urllib.parse.urlencode(params)}"
        
        print(f"{i}. {redirect_uri}")
        print(f"   URL: {auth_url}")
        print()
    
    print("MANUAL TEST INSTRUCTIONS:")
    print("1. Copy one of the URLs above")
    print("2. Paste it in your browser")
    print("3. If you get 'Invalid redirect_uri' → try the next URL")
    print("4. If it works → you'll be redirected to authorize")
    print("5. Let me know which redirect URI worked!")
    print()
    print("RECOMMENDATION:")
    print("It's easier to just add 'http://localhost:8080/callback'")
    print("to your Xero app configuration at:")
    print("https://developer.xero.com/app/manage")

def main():
    test_different_redirect_uris()

if __name__ == "__main__":
    main()