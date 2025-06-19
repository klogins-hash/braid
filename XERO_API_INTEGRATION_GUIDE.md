# Xero API Integration Guide

## Common Issues and Solutions from Production Experience

### 1. Authentication Gotchas

**❌ CRITICAL ISSUE: Client Credentials vs OAuth Confusion**

**Problem**: Client credentials tokens show 0 connections even when organizations are connected.

```bash
# ❌ Client credentials - limited access, can't see organizations
curl --request POST \
  --url https://identity.xero.com/connect/token \
  --header 'Authorization: Basic {base64_credentials}' \
  --data grant_type=client_credentials
# Returns: "xero_userid": "00000000-0000-0000-0000-000000000000"
```

**✅ Solution**: Use proper OAuth flow for organization access:

```bash
# ✅ OAuth flow - full access to connected organizations  
curl --request POST \
  --url https://identity.xero.com/connect/token \
  --header 'Authorization: Basic {base64_credentials}' \
  --data grant_type=authorization_code \
  --data code={authorization_code} \
  --data redirect_uri={redirect_uri}
# Returns: "xero_userid": "c4e5d868-7ae7-440f-b2a8-27e93b291821"
```

**Key Indicators**:
- **Client Credentials**: `xero_userid` is all zeros, 0 connections returned
- **Real OAuth**: `xero_userid` is actual UUID, shows connected organizations

### 2. Data Format Handling

**❌ CRITICAL ISSUE: Assuming JSON When API Returns XML**

**Problem**: Xero P&L reports return XML, not JSON, causing parsing errors.

```python
# ❌ WRONG - Assumes JSON response
response = requests.get(pl_url, headers=headers)
pl_data = response.json()  # Fails with XML response
```

**✅ Solution**: Handle both JSON and XML responses:

```python
def parse_xero_response(response):
    """Parse Xero API response handling both JSON and XML."""
    if response.status_code != 200:
        print(f"❌ API error: {response.status_code}")
        return None
    
    if not response.text.strip():
        print("⚠️  Empty response from Xero API")
        return None
    
    # Check response format
    if response.text.startswith('<'):
        # XML response (common for reports)
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(response.text)
            return parse_xml_report(root)
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return None
    else:
        # JSON response
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return None

def parse_xml_report(root):
    """Parse XML P&L report into structured data."""
    revenue_total = 0
    cogs_total = 0
    operating_expenses_total = 0
    
    # Parse P&L sections
    for row in root.findall('.//Row'):
        row_type = row.find('RowType')
        
        if row_type is not None and row_type.text == 'Section':
            title_elem = row.find('Title')
            if title_elem is not None:
                section_title = title_elem.text.strip()
                
                # Get section total
                cells = row.findall('Cells/Cell')
                if len(cells) >= 2:
                    total_elem = cells[1].find('Value')
                    if total_elem is not None and total_elem.text:
                        try:
                            section_total = float(total_elem.text)
                            
                            # Categorize by section title
                            title_lower = section_title.lower()
                            if 'income' in title_lower or section_title == 'Revenue':
                                revenue_total = section_total
                            elif 'cost of goods sold' in title_lower:
                                cogs_total = section_total
                            elif 'operating expenses' in title_lower:
                                operating_expenses_total = section_total
                        except ValueError:
                            continue
    
    # If sections don't have totals, sum individual line items
    if revenue_total == 0 or operating_expenses_total == 0:
        for row in root.findall('.//Row'):
            row_type = row.find('RowType')
            
            if row_type is not None and row_type.text == 'Row':
                cells = row.findall('Cells/Cell')
                if len(cells) >= 2:
                    account_elem = cells[0].find('Value')
                    amount_elem = cells[1].find('Value')
                    
                    if account_elem is not None and amount_elem is not None:
                        account_name = account_elem.text or ''
                        try:
                            amount = float(amount_elem.text) if amount_elem.text else 0
                        except ValueError:
                            amount = 0
                        
                        account_lower = account_name.lower()
                        
                        # Revenue items
                        if account_name == 'Sales' or 'sales' in account_lower:
                            revenue_total += amount
                        
                        # COGS items
                        elif 'cost of goods sold' in account_lower:
                            cogs_total += amount
                        
                        # Operating expense items
                        elif any(exp in account_lower for exp in [
                            'advertising', 'automobile', 'rent', 'utilities', 
                            'wages', 'salary', 'office', 'expense'
                        ]):
                            operating_expenses_total += amount
    
    return {
        'revenue': revenue_total,
        'cogs': cogs_total,
        'operating_expenses': operating_expenses_total,
        'gross_profit': revenue_total - cogs_total,
        'net_income': revenue_total - cogs_total - operating_expenses_total
    }
```

### 3. Real vs Fake Data Transparency

**❌ CRITICAL ISSUE: Claiming Live Data When Using Fallbacks**

**Problem**: Code claims data is "live from Xero API" when actually using hardcoded values.

```python
# ❌ WRONG - Misleading data source claims
def get_xero_data(user_id):
    try:
        # API call fails...
        pass
    except:
        # Uses hardcoded data but claims it's live
        return {
            'revenue': 1500000,  # Fake data
            'data_source': 'Live Xero API',  # Misleading claim
            'note': 'Real-time data'  # False
        }
```

**✅ Solution**: Transparent data sourcing with clear fallback indication:

```python
def get_xero_financial_data(self, user_id):
    """Get financial data with transparent sourcing."""
    try:
        # Attempt live API call
        headers = {
            'Authorization': f'Bearer {self.xero_token}',
            'Content-Type': 'application/json',
            'Xero-tenant-id': tenant_id
        }
        
        pl_response = requests.get(pl_url, headers=headers)
        
        if pl_response.status_code == 200 and pl_response.text.strip():
            # Parse real data
            real_data = self.parse_xero_response(pl_response)
            
            if real_data and real_data['revenue'] > 0:
                print(f"✅ REAL Xero data: Revenue ${real_data['revenue']:,.2f}")
                return {
                    **real_data,
                    'data_source': f'REAL Xero P&L API - {tenant_name}',
                    'note': f'YTD {current_year} actual P&L data from Xero API'
                }
        
        print("⚠️  No valid data from Xero API")
        
    except Exception as e:
        print(f"❌ Xero API error: {e}")
    
    # Transparent fallback
    print("🔄 Using fallback data (clearly labeled)")
    return {
        'revenue': 0,
        'cogs': 0,
        'operating_expenses': 0,
        'data_source': f'Xero API Failed - Using Fallback',
        'note': 'Fallback data due to API connection issues'
    }
```

### 4. Token Management Best Practices

**✅ Production Token Management Pattern**:

```python
class XeroTokenManager:
    def __init__(self):
        self.client_id = os.getenv('XERO_CLIENT_ID')
        self.client_secret = os.getenv('XERO_CLIENT_SECRET')
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        
    def get_valid_token(self):
        """Get a valid access token, refreshing if needed."""
        # Try direct token from env
        direct_token = os.getenv('XERO_ACCESS_TOKEN', '').strip()
        if direct_token and direct_token.startswith('eyJ'):
            if not self._is_token_expired(direct_token):
                return direct_token
        
        # Try to load from file
        token_data = self._load_token_file()
        if token_data:
            if time.time() < token_data.get('expires_at', 0):
                return token_data['access_token']
            else:
                # Refresh expired token
                return self._refresh_token(token_data)
        
        # Need new authorization
        raise TokenExpiredError("Need new OAuth authorization")
    
    def _refresh_token(self, token_data):
        """Refresh expired token."""
        if not token_data.get('refresh_token'):
            raise TokenExpiredError("No refresh token available")
        
        token_url = "https://identity.xero.com/connect/token"
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': token_data['refresh_token']
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            new_token_data = response.json()
            
            # Update and save
            token_data['access_token'] = new_token_data['access_token']
            token_data['expires_at'] = time.time() + new_token_data.get('expires_in', 1800)
            
            self._save_token_file(token_data)
            
            print("✅ Token refreshed successfully")
            return new_token_data['access_token']
        else:
            raise TokenRefreshError(f"Token refresh failed: {response.status_code}")
```

### 5. Quick Setup Commands

**Get fresh token quickly:**

```bash
# For testing - client credentials (limited access)
curl --request POST \
  --url https://identity.xero.com/connect/token \
  --header 'Authorization: Basic RDg2QUM5MjkyNEUzNDhEQzk0Mjc2ODUxNzE4ODZFMEQ6OXEtOHVzT1EzWEZwc3MwZHY3RGpqb1RtdXRYR0VtNTh0WFptU19OWVRSbm85OTM4' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=client_credentials \
  --data scope='accounting.transactions accounting.contacts accounting.settings accounting.reports.read'
```

**Test connection:**

```bash
# Test if token works
curl -H "Authorization: Bearer $XERO_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.xero.com/connections
```

### 6. Common Endpoints and Expected Formats

**Connections** (JSON):
- URL: `https://api.xero.com/connections`
- Returns: List of connected organizations
- Format: JSON

**P&L Report** (XML):
- URL: `https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss?fromDate=YYYY-MM-DD&toDate=YYYY-MM-DD`
- Returns: Profit & Loss report
- Format: XML (not JSON!)

**Trial Balance** (XML):
- URL: `https://api.xero.com/api.xro/2.0/Reports/TrialBalance`
- Returns: Account balances
- Format: XML

**Invoices** (JSON):
- URL: `https://api.xero.com/api.xro/2.0/Invoices`
- Returns: Invoice list
- Format: JSON

### 7. Troubleshooting Checklist

When Xero integration fails:

1. **Check token validity:**
   ```python
   # Decode JWT to check contents
   import base64, json
   payload = token.split('.')[1]
   decoded = json.loads(base64.urlsafe_b64decode(payload + '=='))
   print(f"Token user_id: {decoded.get('xero_userid')}")
   print(f"Expires: {datetime.fromtimestamp(decoded.get('exp', 0))}")
   ```

2. **Test connections endpoint:**
   ```bash
   curl -H "Authorization: Bearer $TOKEN" https://api.xero.com/connections
   ```

3. **Check response format:**
   ```python
   print(f"Response starts with: {response.text[:50]}")
   print(f"Content-Type: {response.headers.get('content-type')}")
   ```

4. **Validate organization access:**
   - Client credentials: Usually 0 connections
   - Real OAuth: Should show connected organizations

5. **Check scopes:**
   - Reports require: `accounting.reports.read`
   - Transactions require: `accounting.transactions`
   - Basic access: `accounting.contacts accounting.settings`

This guide prevents the major Xero integration issues we encountered during the financial forecasting agent development.