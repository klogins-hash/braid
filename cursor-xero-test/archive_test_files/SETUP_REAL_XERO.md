# 🔑 Get Real Xero Accounting Data - Easy Setup

This guide will help you get **real Xero accounting data** instead of mock data in just a few minutes.

## 📋 Prerequisites

✅ You already have:
- Xero Client ID and Secret (in your .env file)
- A Xero account or Demo Company access

## 🚀 Quick Setup (3 Steps)

### Step 1: Run the OAuth Setup Script
```bash
python setup_real_xero.py
```

This will:
1. 🌐 Open your browser to Xero login
2. 🔐 Ask you to authorize the app
3. 🏢 Show your available Xero organisations  
4. 💾 Save the tokens to your .env file

### Step 2: Complete Authorization in Browser
1. Login to your Xero account
2. Select the organisation to connect
3. Click "Allow access" 
4. The script will automatically capture the tokens

### Step 3: Test Real Data
```bash
python test_full_agent.py
```

You should now see:
- ✅ `🎉 SUCCESS: Retrieved REAL Xero P&L data!`
- ✅ Data source: `"Live Xero Organisation"`
- ✅ Real financial numbers from your Xero account

## 🎯 What You'll Get

**Before (Mock Data):**
```json
{
  "revenue": 2650000,
  "data_source": "Enhanced mock data - Xero API authenticated"
}
```

**After (Real Data):**
```json
{
  "revenue": 45250.75,
  "data_source": "Live Xero API - Your Company Name"
}
```

## 🔧 Troubleshooting

### Problem: "No organisations found"
**Solution:** Make sure you have access to at least one Xero organisation

### Problem: "Token expired" 
**Solution:** Run `python setup_real_xero.py` again (tokens expire in 30 minutes)

### Problem: "Permission denied"
**Solution:** Make sure your Xero app has accounting scopes enabled

## 🎉 Demo Company Option

If you don't have real accounting data, Xero provides demo companies:

1. Go to https://developer.xero.com/
2. Create a Demo Company
3. Run the setup script and connect to the demo company
4. You'll get realistic demo financial data

## 📊 What Data You'll Access

With real Xero access, you'll get:
- ✅ **Real P&L statements** with actual revenue/expenses
- ✅ **Historical financial data** from your accounting system  
- ✅ **Multi-period comparisons** for accurate forecasting
- ✅ **Real company information** (name, currency, country)

## 🔄 Token Management

- **Access tokens** expire in 30 minutes
- **Refresh tokens** last 60 days  
- The script saves both for future use
- Re-run setup when tokens expire

---

**Ready to get real data?** Run:
```bash
python setup_real_xero.py
```