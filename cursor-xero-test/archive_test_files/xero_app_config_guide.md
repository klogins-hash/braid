# 🎯 Exact Xero App Configuration Guide

## ❌ NOT the "Login URL for launcher"

The "Login URL for launcher (optional)" is NOT what we need.

## ✅ What You Actually Need: "OAuth 2.0 redirect URIs"

### Step-by-Step Visual Guide:

1. **Go to**: https://developer.xero.com/app/manage
2. **Click** on your existing app
3. **Click** the "Configuration" tab
4. **Scroll down** to find this section:

```
📋 OAuth 2.0 redirect URIs
┌─────────────────────────────────────────┐
│ http://localhost:8080/callback          │  ← ADD THIS
├─────────────────────────────────────────┤
│ + Add another redirect URI              │
└─────────────────────────────────────────┘
```

5. **Type exactly**: `http://localhost:8080/callback`
6. **Click** "Save"

## 🔍 Common Confusion:

- ❌ **Login URL for launcher** - This is for app store listings
- ✅ **OAuth 2.0 redirect URIs** - This is for API authentication

## 📱 What It Should Look Like:

```
App Configuration
├── App Details
├── Integration URLs
│   ├── Launch URL (optional)
│   └── Login URL for launcher (optional)  ← NOT THIS
├── OAuth 2.0 redirect URIs               ← THIS ONE!
│   └── http://localhost:8080/callback    ← ADD HERE
└── Scopes
    ├── ✅ accounting.reports.read
    ├── ✅ accounting.transactions.read
    └── ✅ accounting.contacts.read
```

## 🚀 After Adding the Redirect URI:

Run this command:
```bash
python setup_real_xero.py
```

The OAuth flow should work without the redirect URI error!

## 🔧 Still Can't Find It?

If you can't find "OAuth 2.0 redirect URIs" section, your app might be:
1. **Too old** - Create a new app
2. **Wrong type** - Make sure it's a "Web App" not "Mobile App"
3. **Different interface** - Xero sometimes updates their UI

**Quick alternative**: Use the manual flow:
```bash
python setup_real_xero_flexible.py
```
Choose option 2 - this works regardless of your app configuration!