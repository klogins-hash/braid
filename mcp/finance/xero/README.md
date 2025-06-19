# Xero MCP Server

Xero MCP provides comprehensive accounting and financial management capabilities through the Xero API with 50+ commands for contacts, invoicing, chart of accounts, financial reporting, and business operations through the Model Context Protocol.

## Overview

Xero is a leading cloud-based accounting software platform used by millions of businesses worldwide. This MCP server enables AI agents to access and manage accounting data, create invoices, manage contacts, process payments, and generate financial reports programmatically.

## Capabilities

### Core Accounting Tools

- **`xero_list-accounts`**: List all accounts in the chart of accounts
  - Output: Complete chart of accounts with codes, names, and types

- **`xero_create-account`**: Create new accounts
  - Input: Account name, type, code
  - Output: New account details and ID

- **`xero_update-account`**: Modify existing accounts
  - Input: Account ID, updated details
  - Output: Updated account information

### Contact Management

- **`xero_list-contacts`**: List all contacts (customers and suppliers)
  - Output: Complete contact database with details

- **`xero_create-contact`**: Create new contacts
  - Input: Name, email, phone, contact type
  - Output: New contact ID and details

- **`xero_update-contact`**: Update existing contacts
  - Input: Contact ID, updated information
  - Output: Updated contact details

### Invoice Management

- **`xero_create-invoice`**: Create new invoices
  - Input: Contact ID, line items, due date
  - Output: Invoice number and details

- **`xero_list-invoices`**: List invoices with filtering
  - Input: Status filter (optional)
  - Output: Invoice list with details

- **`xero_update-invoice`**: Update invoice status and details
  - Input: Invoice ID, updated information
  - Output: Updated invoice details

### Payment Processing

- **`xero_create-payment`**: Record payments for invoices
  - Input: Invoice ID, amount, payment date
  - Output: Payment confirmation and details

- **`xero_list-payments`**: List all payments
  - Output: Complete payment history

### Bank Transactions

- **`xero_create-bank-transaction`**: Create bank transactions
  - Input: Bank account ID, amount, type, description
  - Output: Transaction details

- **`xero_list-bank-transactions`**: List bank transactions
  - Input: Bank account ID (optional)
  - Output: Transaction history

### Financial Reporting

- **`xero_get-trial-balance`**: Generate trial balance reports
  - Input: Report date
  - Output: Complete trial balance with all accounts

- **`xero_get-profit-loss`**: Generate profit and loss statements
  - Input: Date range (from/to dates)
  - Output: P&L statement with revenue and expenses

- **`xero_get-balance-sheet`**: Generate balance sheet reports
  - Input: Report date
  - Output: Assets, liabilities, and equity breakdown

- **`xero_get-aged-receivables`**: Aged receivables analysis
  - Input: Report date
  - Output: Outstanding customer invoices by age

- **`xero_get-aged-payables`**: Aged payables analysis
  - Input: Report date
  - Output: Outstanding supplier bills by age

### Purchase Orders & Expenses

- **`xero_create-purchase-order`**: Create purchase orders
  - Input: Contact ID, line items, delivery date
  - Output: Purchase order details

- **`xero_list-purchase-orders`**: List all purchase orders
  - Output: Complete purchase order history

- **`xero_create-expense-claim`**: Create expense claims
  - Input: User ID, receipt details
  - Output: Expense claim ID and status

- **`xero_list-expense-claims`**: List expense claims
  - Output: All expense claims with status

### Additional Features

- **`xero_create-credit-note`**: Create credit notes
- **`xero_list-credit-notes`**: List credit notes
- **`xero_create-receipt`**: Create sales receipts
- **`xero_list-receipts`**: List receipts
- **`xero_create-journal-entry`**: Create manual journal entries
- **`xero_list-journal-entries`**: List journal entries
- **`xero_create-item`**: Create inventory items
- **`xero_list-items`**: List inventory items
- **`xero_create-tax-rate`**: Create tax rates
- **`xero_list-tax-rates`**: List tax rates
- **`xero_create-tracking-category`**: Create tracking categories
- **`xero_list-tracking-categories`**: List tracking categories
- **`xero_create-budget`**: Create budgets
- **`xero_list-budgets`**: List budgets
- **`xero_get-bank-summary`**: Bank summary reports
- **`xero_list-currencies`**: List available currencies
- **`xero_get-branding-themes`**: Get invoice branding themes
- **`xero_list-users`**: List organisation users

## Setup Instructions

### 1. Get Xero Developer Access

1. Visit [https://developer.xero.com/](https://developer.xero.com/)
2. Sign up for a free developer account
3. Create a new app in your developer dashboard
4. Get your Bearer Token for API access
5. Ensure your app has the required scopes:
   - `accounting.transactions`
   - `accounting.contacts`
   - `accounting.settings`

### 2. Environment Configuration

Add to your `.env` file:

```bash
XERO_BEARER_TOKEN=your-xero-bearer-token-here
```

### 3. Installation

The MCP server is automatically installed when using Braid's Docker orchestration:

```bash
braid package --production
docker compose up --build
```

For manual installation:
```bash
git clone https://github.com/XeroAPI/xero-mcp-server.git
cd xero-mcp-server
npm install
npm run build
```

## Usage Examples

### Invoice Management

```python
# Create a new customer contact
contact = agent.xero_create_contact(
    name="ABC Company Ltd",
    email="billing@abccompany.com",
    phone="+1-555-123-4567",
    contactType="CUSTOMER"
)

# Create an invoice for the customer
invoice = agent.xero_create_invoice(
    contactId=contact["contactId"],
    lineItems=[
        {
            "description": "Professional Services",
            "quantity": 10,
            "unitAmount": 150.00,
            "accountCode": "200"
        }
    ],
    dueDate="2024-07-15"
)

print(f"Invoice created: {invoice['invoiceNumber']} for ${invoice['total']}")
```

### Financial Reporting

```python
# Generate current month P&L
from datetime import datetime, date

today = date.today()
first_day = today.replace(day=1)

profit_loss = agent.xero_get_profit_loss(
    fromDate=first_day.strftime("%Y-%m-%d"),
    toDate=today.strftime("%Y-%m-%d")
)

print(f"Revenue: ${profit_loss['revenue']}")
print(f"Expenses: ${profit_loss['expenses']}")
print(f"Net Profit: ${profit_loss['net_profit']}")

# Get trial balance
trial_balance = agent.xero_get_trial_balance(
    date=today.strftime("%Y-%m-%d")
)

# Generate aged receivables report
aged_receivables = agent.xero_get_aged_receivables(
    date=today.strftime("%Y-%m-%d")
)

print(f"Total Outstanding: ${aged_receivables['total_outstanding']}")
```

### Contact and Customer Management

```python
# List all customers
customers = agent.xero_list_contacts()
customer_list = [c for c in customers if c['contactType'] == 'CUSTOMER']

print(f"Total customers: {len(customer_list)}")

# Update customer information
updated_contact = agent.xero_update_contact(
    contactId="customer-id-here",
    name="Updated Company Name",
    email="new-email@company.com"
)

# Create a supplier
supplier = agent.xero_create_contact(
    name="Office Supplies Inc",
    email="accounts@officesupplies.com",
    contactType="SUPPLIER"
)
```

### Payment Processing

```python
# List outstanding invoices
invoices = agent.xero_list_invoices(status="AUTHORISED")

# Process payment for an invoice
payment = agent.xero_create_payment(
    invoiceId=invoices[0]["invoiceId"],
    amount=invoices[0]["amountDue"],
    date=datetime.now().strftime("%Y-%m-%d")
)

print(f"Payment processed: ${payment['amount']} for invoice {payment['invoiceNumber']}")

# List all payments
payments = agent.xero_list_payments()
total_payments_today = sum(p['amount'] for p in payments if p['date'] == today.strftime("%Y-%m-%d"))
```

### Expense Management

```python
# Create an expense claim
expense_claim = agent.xero_create_expense_claim(
    userId="user-id-here",
    receipts=[
        {
            "description": "Business Lunch",
            "amount": 45.50,
            "date": "2024-06-15"
        }
    ]
)

# Create purchase order
purchase_order = agent.xero_create_purchase_order(
    contactId="supplier-id-here",
    lineItems=[
        {
            "description": "Office Supplies",
            "quantity": 100,
            "unitAmount": 2.50
        }
    ],
    deliveryDate="2024-07-01"
)
```

### Chart of Accounts Management

```python
# List all accounts
accounts = agent.xero_list_accounts()

# Create a new expense account
new_account = agent.xero_create_account(
    name="Marketing Expenses",
    type="EXPENSE",
    code="6200"
)

# Create tracking categories for departments
tracking_category = agent.xero_create_tracking_category(
    name="Department"
)
```

## Use Cases

### Small Business Accounting
- **Invoice Automation**: Automatically create and send invoices
- **Expense Tracking**: Record and categorize business expenses
- **Payment Reconciliation**: Match payments to invoices
- **Financial Reporting**: Generate P&L, balance sheets, cash flow

### Enterprise Integration
- **ERP Integration**: Sync data between systems
- **Multi-entity Reporting**: Consolidate multiple business units
- **Advanced Analytics**: Custom financial analysis and dashboards
- **Compliance Reporting**: Automated regulatory reporting

### Professional Services
- **Time & Billing**: Track billable hours and create invoices
- **Project Accounting**: Track expenses by project or client
- **Recurring Invoices**: Automate monthly billing cycles
- **Client Portals**: Provide clients with invoice and payment access

### E-commerce Integration
- **Order Processing**: Convert orders to invoices automatically
- **Inventory Management**: Track stock levels and costs
- **Multi-currency Support**: Handle international transactions
- **Tax Compliance**: Automatic tax calculations and reporting

## Rate Limiting & Best Practices

### API Limits
- **Per Minute**: 60 requests per minute
- **Per Day**: 5,000 requests per day
- **Burst Capacity**: 10 requests burst allowance
- **Premium Plans**: Higher limits available for Xero partners

### Optimization Tips
1. **Batch Operations**: Group related API calls together
2. **Use Webhooks**: Subscribe to real-time updates instead of polling
3. **Cache Data**: Store frequently accessed data locally
4. **Implement Retry Logic**: Handle rate limits gracefully with exponential backoff
5. **Filter Results**: Use date ranges and status filters to reduce data transfer

### Error Handling
```python
import time
from datetime import datetime, timedelta

def safe_xero_call(func, *args, **kwargs):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            raise
        except AuthenticationError:
            print("Check your Xero bearer token")
            raise
        except ValidationError as e:
            print(f"Invalid data: {e}")
            raise

# Usage
invoice = safe_xero_call(agent.xero_create_invoice, 
                        contactId="123", 
                        lineItems=[...])
```

## Security & Compliance

### Authentication Security
- **Bearer Token**: Secure token-based authentication
- **Scope Limitations**: Tokens limited to required permissions only
- **Token Rotation**: Regular token refresh recommended
- **Audit Logging**: All API calls logged for compliance

### Data Protection
- **Encryption**: All data transmitted via HTTPS
- **No Local Storage**: Sensitive data not cached locally
- **Access Controls**: Role-based access to financial data
- **Compliance**: SOC 2, ISO 27001 certified infrastructure

### Financial Compliance
- **Audit Trail**: Complete transaction history maintained
- **Tax Compliance**: Automatic tax calculations and reporting
- **Multi-currency**: Proper currency conversion and reporting
- **Regulatory Reporting**: Support for various accounting standards

## Troubleshooting

### Common Issues

**Authentication Errors**
- Verify bearer token is correctly set in `.env` file
- Check token hasn't expired (tokens typically last 30 minutes)
- Ensure required OAuth scopes are granted
- Verify app is connected to the correct Xero organisation

**Rate Limit Exceeded**
- Implement exponential backoff retry logic
- Reduce request frequency during peak usage
- Consider upgrading to Xero partner status for higher limits
- Use webhooks instead of polling for real-time data

**Validation Errors**
- Check required fields are provided for create operations
- Verify data formats (dates, currencies, IDs)
- Ensure account codes exist in chart of accounts
- Validate contact IDs exist before creating transactions

**Network Issues**
- Ensure container has internet access
- Check firewall settings for outbound HTTPS connections
- Verify DNS resolution for api.xero.com
- Test connection with curl or similar tool

### Debug Mode

To enable detailed logging:

```bash
# Set debug environment variables
NODE_ENV=development
DEBUG=xero:*
node dist/index.js
```

### Health Checks

Monitor MCP server health:

```bash
# Check server status
curl http://localhost:3004/health

# View metrics
curl http://localhost:3004/metrics
```

## Integration with Braid

When using Xero MCP with Braid agents, all tools are automatically available with the `xero_` prefix:

- `xero_create_invoice()` - Create invoices
- `xero_list_contacts()` - Manage customer database
- `xero_get_profit_loss()` - Financial reporting
- And all other 50+ accounting tools

The MCP runs in a separate Docker container with proper networking, security, and monitoring configured automatically.

## Advanced Features

### Webhook Integration
- **Real-time Updates**: Receive notifications when data changes in Xero
- **Event Types**: Invoice updates, payment received, contact changes
- **Automation**: Trigger workflows based on accounting events

### Multi-Organisation Support
- **Organisation Switching**: Work with multiple Xero organisations
- **Consolidated Reporting**: Aggregate data across entities
- **Role-based Access**: Different permissions per organisation

### Custom Fields and Tracking
- **Tracking Categories**: Custom dimensions for reporting
- **Custom Fields**: Additional data fields on transactions
- **Project Tracking**: Assign transactions to projects or departments

## Migration and Data Import

### From Other Accounting Systems
- **Chart of Accounts**: Import existing account structures
- **Historical Data**: Import opening balances and transactions
- **Contact Migration**: Bulk import customer and supplier data
- **Reconciliation**: Verify imported data accuracy

### Backup and Export
- **Data Export**: Export all accounting data for backup
- **Report Generation**: Automated backup of key reports
- **Audit Trail**: Complete transaction history export

## Support

- **Xero Developer Documentation**: [https://developer.xero.com/documentation/](https://developer.xero.com/documentation/)
- **MCP Repository**: [https://github.com/XeroAPI/xero-mcp-server](https://github.com/XeroAPI/xero-mcp-server)
- **Xero API Support**: [https://developer.xero.com/support/](https://developer.xero.com/support/)
- **Community Forum**: [https://community.xero.com/developer/](https://community.xero.com/developer/)

## Premium Features

Consider Xero premium plans for:
- **Higher Rate Limits**: Increased API call allowances
- **Advanced Reporting**: Additional report types and customization
- **Multi-currency**: Enhanced foreign exchange features
- **Integrations**: Pre-built connectors to other business tools
- **Priority Support**: Faster response times and dedicated support