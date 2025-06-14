#!/usr/bin/env python3
"""
Simple script to test and complete MS365 authentication.
Run this interactively to complete the OAuth flow.
"""
import os
import json
from O365 import Account
from O365.connection import FileSystemTokenBackend

def test_authentication():
    CREDS_PATH = "credentials/ms365_credentials.json"
    TOKEN_PATH = "credentials/ms365_token.json"
    
    if not os.path.exists(CREDS_PATH):
        print(f"Credentials file not found at {CREDS_PATH}")
        return False
    
    with open(CREDS_PATH) as f:
        creds = json.load(f)
    
    print("Setting up MS365 account...")
    token_backend = FileSystemTokenBackend(token_path=TOKEN_PATH)
    account = Account(
        (creds["client_id"], creds["client_secret"]), 
        tenant_id="e76a482b-c060-4a49-affc-87c454bd1976",
        token_backend=token_backend
    )
    
    if not account.is_authenticated:
        print("Account not authenticated. Starting OAuth flow...")
        scopes = ["User.Read", "Mail.Send", "ChannelMessage.Send", "Team.ReadBasic.All"]
        account.authenticate(scopes=scopes)
    
    if account.is_authenticated:
        print("✅ Authentication successful!")
        print(f"✅ Token saved to {TOKEN_PATH}")
        
        # Test basic functionality
        try:
            user = account.get_current_user()
            if user:
                print(f"✅ User info retrieved: {user.display_name}")
                print(f"✅ Email: {user.mail}")
            else:
                print("⚠️  Could not retrieve user info")
        except Exception as e:
            print(f"⚠️  Error retrieving user info: {e}")
        
        return True
    else:
        print("❌ Authentication failed")
        return False

if __name__ == "__main__":
    test_authentication()