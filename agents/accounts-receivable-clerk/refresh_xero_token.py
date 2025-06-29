#!/usr/bin/env python3
"""
Quick Xero token refresh using existing credentials.
Uses the core integration setup with your existing client ID and secret.
"""
import os
import sys
from dotenv import load_dotenv

# Add core integrations to path
sys.path.append('/Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid')

def refresh_xero_token():
    """Refresh Xero token using existing credentials."""
    
    # Load existing credentials
    load_dotenv()
    
    client_id = os.getenv("XERO_CLIENT_ID", "").strip()
    client_secret = os.getenv("XERO_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        print("❌ Missing XERO_CLIENT_ID or XERO_CLIENT_SECRET in .env file")
        return False
    
    print("🔑 XERO TOKEN REFRESH")
    print("=" * 50)
    print(f"Using Client ID: {client_id}")
    print("Starting OAuth2 flow...")
    print()
    
    try:
        from core.integrations.finance.xero.setup import setup_xero_integration
        
        # Run setup with existing credentials
        credentials = setup_xero_integration(
            client_id=client_id,
            client_secret=client_secret,
            auto_open_browser=True
        )
        
        print()
        print("✅ Token refresh successful!")
        print(f"New token expires in 30 minutes")
        print(f"Tenant: {credentials['tenant_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token refresh failed: {e}")
        return False

def test_connection():
    """Test the refreshed connection."""
    print("\n🧪 Testing refreshed connection...")
    
    try:
        from core.integrations.finance.xero.setup import test_xero_connection
        return test_xero_connection()
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main refresh workflow."""
    
    print("🚀 Xero Token Refresh for AR Clerk Demo")
    print("=" * 60)
    
    # Step 1: Refresh token
    if not refresh_xero_token():
        print("\n❌ Token refresh failed. Check your Xero app credentials.")
        return False
    
    # Step 2: Test connection
    if not test_connection():
        print("\n❌ Connection test failed after refresh.")
        return False
    
    print("\n🎉 SUCCESS! Xero integration ready for live demo")
    print("=" * 60)
    print("✅ Fresh access token obtained")
    print("✅ Connection tested and working")
    print("✅ Ready to run AR Clerk agent with live data")
    print()
    print("🚀 To start your demo, run:")
    print("   python3 agent.py")
    print()
    print("💡 Try this demo input:")
    print('   "Process new contract for Demo Corp, $15,000 consulting, Net 30, contact: demo@democorp.com"')
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Refresh cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)