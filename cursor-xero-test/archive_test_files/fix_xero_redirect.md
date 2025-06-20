# 🔧 Fix Xero Redirect URI Error

## ❌ Problem: `Invalid redirect_uri` Error 500

This happens because your Xero app isn't configured to accept the local callback URL.

## ✅ Solution: Update Xero App Configuration

### Step 1: Go to Xero Developer Console
1. Visit: https://developer.xero.com/app/manage
2. Login with your Xero account
3. Click on your existing app (or create one if needed)

### Step 2: Update Redirect URIs
1. Click "Configuration" tab
2. Scroll to "OAuth 2.0 redirect URIs"
3. Add this exact URL:
   ```
   http://localhost:8080/callback
   ```
4. Click "Save"

### Step 3: Verify App Settings
Make sure your app has these scopes enabled:
- ✅ `accounting.reports.read`
- ✅ `accounting.transactions.read`
- ✅ `accounting.contacts.read`
- ✅ `accounting.settings.read`

### Step 4: Get App Credentials
1. Copy your Client ID and Client Secret
2. Make sure they match your .env file:
   ```
   XERO_CLIENT_ID=your_client_id_here
   XERO_CLIENT_SECRET=your_client_secret_here
   ```

## 🚀 Alternative: Use Different Port

If you can't modify the Xero app, update the script to use a different port:

1. In your Xero app, add: `http://localhost:3000/callback`
2. Update the script to use port 3000

## 🔍 Quick Check

Your Xero app should look like this:
```
App Name: Financial Forecast Agent
OAuth 2.0 redirect URIs: 
- http://localhost:8080/callback

Scopes:
- accounting.reports.read ✅
- accounting.transactions.read ✅
- accounting.contacts.read ✅
- accounting.settings.read ✅
```

After fixing the redirect URI, run the setup again:
```bash
python setup_real_xero.py
```