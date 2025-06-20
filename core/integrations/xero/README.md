# Xero Integration

Easy-to-use Xero API integration for Braid agents. Get real financial data with just a few simple steps!

## ⚡ Quick Setup

### Option 1: Command Line Setup (Recommended)
```bash
python -m core.integrations.xero.setup
```

### Option 2: Programmatic Setup
```python
from core.integrations.xero.setup import setup_xero_integration
setup_xero_integration()
```

### Option 3: Manual Setup
1. Create a Xero app at https://developer.xero.com/app/manage
2. Set redirect URI to: `http://localhost:8080/callback`
3. Add these to your `.env` file:
```env
XERO_CLIENT_ID=your_client_id
XERO_CLIENT_SECRET=your_client_secret
XERO_ACCESS_TOKEN=your_access_token
XERO_TENANT_ID=your_tenant_id
```

## 🛠️ Available Tools

### `get_xero_profit_and_loss`
Get Profit & Loss reports for financial forecasting.

**Default behavior:** Returns Year-to-Date data if no dates specified.

```python
from core.integrations.xero.tools import get_xero_profit_and_loss

# Get YTD P&L (default)
ytd_pl = get_xero_profit_and_loss.invoke({})

# Get specific period
q1_pl = get_xero_profit_and_loss.invoke({
    "fromDate": "2025-01-01",
    "toDate": "2025-03-31"
})
```

**Returns structured data:**
```json
{
  "reportName": "Profit and Loss",
  "reportDate": "1 January 2025 to 20 June 2025",
  "financial_data": {
    "total_revenue": 26504.84,
    "total_cogs": 2340.00,
    "gross_profit": 24164.84,
    "total_expenses": 38500.71,
    "net_income": -14335.87
  },
  "rows": [
    {"account": "Sales", "value": "26504.84"},
    {"account": "Cost of Sales", "value": "2340.00"}
  ]
}
```

### `get_xero_balance_sheet`
Get Balance Sheet reports for asset/liability analysis.

```python
from core.integrations.xero.tools import get_xero_balance_sheet

# Get current balance sheet
balance_sheet = get_xero_balance_sheet.invoke({})

# Get balance sheet for specific date
balance_sheet = get_xero_balance_sheet.invoke({
    "date": "2025-03-31"
})
```

### `get_xero_trial_balance`
Get Trial Balance reports to verify accounting accuracy.

```python
from core.integrations.xero.tools import get_xero_trial_balance

# Get trial balance
trial_balance = get_xero_trial_balance.invoke({
    "fromDate": "2025-01-01",
    "toDate": "2025-06-30"
})
```

## 🤖 Using in Your Agent

### LangGraph Agent Integration
```python
from langchain_core.tools import tool
from core.integrations.xero.tools import get_xero_tools

class MyFinancialAgent:
    def __init__(self):
        # Get all Xero tools
        self.xero_tools = get_xero_tools()
        
        # Or import specific tools
        from core.integrations.xero.tools import get_xero_profit_and_loss
        self.pl_tool = get_xero_profit_and_loss
    
    def analyze_finances(self):
        # Get YTD financial data
        pl_data = self.pl_tool.invoke({})
        # Process the financial data...
```

### Direct Tool Usage
```python
from core.integrations.xero.tools import get_xero_profit_and_loss

# The tool handles all the API complexity for you
financial_data = get_xero_profit_and_loss.invoke({
    "fromDate": "2025-01-01",
    "toDate": "2025-06-20"
})

print(financial_data)
```

## 🔧 Advanced Configuration

### Custom Date Ranges
```python
# Year-to-date (default when no dates provided)
ytd_data = get_xero_profit_and_loss.invoke({})

# Specific date range
custom_data = get_xero_profit_and_loss.invoke({
    "fromDate": "2024-01-01",
    "toDate": "2024-12-31",
    "periods": 12,
    "timeframe": "MONTH"
})
```

### Error Handling
The tools provide helpful error messages with setup instructions:

```python
try:
    data = get_xero_profit_and_loss.invoke({})
except Exception as e:
    print(e)
    # Output: "XERO_ACCESS_TOKEN environment variable not set. 
    #         Run: python -m core.integrations.xero.setup"
```

## 🔐 Authentication Details

### Token Management
- **Access tokens** expire after 30 minutes
- **Refresh tokens** last 60 days
- Re-run setup when tokens expire

### Scopes Required
The setup automatically requests these scopes:
- `accounting.reports.read` - P&L, Balance Sheet reports
- `accounting.transactions.read` - Transaction details
- `accounting.contacts.read` - Customer information
- `accounting.settings.read` - Organization details

### Security Best Practices
- Credentials are stored in `.env` file
- Never commit `.env` to version control
- Tokens automatically expire for security

## 🧪 Testing Your Setup

```python
# Test connection
from core.integrations.xero.setup import test_xero_connection
test_xero_connection()

# Test data retrieval
from core.integrations.xero.tools import get_xero_profit_and_loss
result = get_xero_profit_and_loss.invoke({})
print(result)
```

## 📊 Data Format

### Financial Data Structure
The tools return structured JSON with:
- **Meta data**: Report name, date range
- **Key metrics**: Extracted financial figures
- **Raw data**: All account line items

### Key Financial Metrics Extracted
- `total_revenue` - Total sales/income
- `total_cogs` - Cost of goods sold
- `gross_profit` - Revenue minus COGS
- `total_expenses` - Operating expenses
- `net_income` - Final profit/loss

## 🚨 Troubleshooting

### Common Issues

**"XERO_ACCESS_TOKEN environment variable not set"**
```bash
# Run setup to get fresh tokens
python -m core.integrations.xero.setup
```

**"Authentication failed. Tokens may have expired."**
```bash
# Tokens expire after 30 minutes, re-run setup
python -m core.integrations.xero.setup
```

**"Access denied. Check your Xero app permissions."**
- Ensure your Xero app has the required scopes
- Check that you've connected to the right organization

**"Endpoint not found"**
- Verify your Xero organization has the required modules enabled
- Some endpoints require specific Xero subscriptions

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now tool calls will show detailed request/response info
```

## 🔗 Related Resources

- [Xero Developer Portal](https://developer.xero.com/)
- [Xero API Documentation](https://developer.xero.com/documentation/api/accounting/)
- [Braid Agent Development Guide](../../docs/guides/agent-development/)

## 💡 Tips for Financial Agents

1. **Use Year-to-Date by default** - Most relevant for forecasting
2. **Extract key metrics** - Focus on revenue, expenses, net income
3. **Handle data gaps gracefully** - Not all orgs have complete data
4. **Cache expensive calls** - API has rate limits
5. **Validate data quality** - Check for reasonable values

## 🎯 Example Use Cases

- **Financial Forecasting** - Use P&L data as baseline for projections
- **Cash Flow Analysis** - Combine P&L with Balance Sheet data
- **Performance Tracking** - Compare periods using timeframe parameters
- **Automated Reporting** - Generate regular financial summaries
- **Risk Assessment** - Analyze expense ratios and profit margins

---

*For more advanced usage and custom integrations, see the [full Braid documentation](../../docs/).*