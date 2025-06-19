# Agent Development Best Practices

## Critical Issues and Solutions from Financial Forecasting Agent Development

### 1. LangSmith Tracing Architecture

**❌ CRITICAL ISSUE: Isolated Tool Calls**
- **Problem**: Direct `tool.invoke()` calls create isolated events instead of unified workflow traces
- **Symptom**: Each tool appears as separate event in LangSmith, not as waterfall flow
- **Root Cause**: Bypassing LangGraph's tracing system

**✅ SOLUTION: Proper Agent → Tools → Agent Flow**

```python
# ❌ WRONG - Creates isolated traces
def run_workflow():
    client_info = get_client_information.invoke({'user_id': 'user_123'})
    xero_data = get_xero_data.invoke({'user_id': 'user_123'})
    # Each call appears as isolated event

# ✅ CORRECT - Creates unified trace
def agent_node(state: dict) -> dict:
    response = model.invoke(messages)  # Model decides which tools to call
    return {"messages": messages + [response]}

def tool_node(state: dict) -> dict:
    # Execute tools called by model and return ToolMessage
    for tool_call in last_message.tool_calls:
        result = tool_map[tool_name].invoke(tool_args)
        tool_message = ToolMessage(content=str(result), tool_call_id=tool_call['id'])
    return {"messages": messages + tool_messages}
```

**Key Requirements:**
- Tools must be bound to model: `model = model.bind_tools(tools)`
- Use ToolMessage responses with matching `tool_call_id`
- Let model decide which tools to call, don't invoke directly

### 2. Live API Integration Patterns

**❌ CRITICAL ISSUE: Fake vs Real Data**
- **Problem**: Using hardcoded fallback data but claiming it's from live APIs
- **Symptom**: Data doesn't match actual API source
- **Root Cause**: Poor error handling and transparent data sourcing

**✅ SOLUTION: Transparent Data Sourcing**

```python
def get_live_api_data(self, user_id):
    """Get real data from API with transparent fallback."""
    try:
        # Attempt live API call
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200 and response.text.strip():
            # Parse and validate real data
            real_data = self._parse_api_response(response)
            
            if self._validate_data(real_data):
                print(f"✅ REAL API data retrieved: {data_summary}")
                return {
                    'data': real_data,
                    'data_source': f'REAL {api_name} API - {org_name}',
                    'note': f'Live data from {api_name} API'
                }
        
        print(f"⚠️  No valid data from {api_name} API")
        
    except Exception as e:
        print(f"❌ {api_name} API error: {e}")
    
    # Transparent fallback
    print(f"🔄 Using fallback data (clearly labeled)")
    return {
        'data': fallback_data,
        'data_source': f'{api_name} API Failed - Using Fallback',
        'note': 'Fallback data due to API issues'
    }
```

### 3. Xero API Integration Gotchas

**❌ CRITICAL ISSUE: Token Management**
- **Problem**: Client credentials tokens don't see organization connections
- **Symptom**: 0 connections returned, falling back to mock data
- **Root Cause**: OAuth flow vs client credentials confusion

**✅ SOLUTION: Proper Xero Authentication**

```python
# Client credentials - good for testing but limited access
curl --request POST \
  --url https://identity.xero.com/connect/token \
  --header 'Authorization: Basic {base64_client_credentials}' \
  --data grant_type=client_credentials

# Full OAuth flow - required for organization access
# 1. Authorization URL with correct redirect URI
# 2. User authorization
# 3. Exchange code for token
# 4. Token includes real user_id and organization access
```

**Key Points:**
- Client credentials: `xero_userid: "00000000-0000-0000-0000-000000000000"`
- Real OAuth: `xero_userid: "c4e5d868-7ae7-440f-b2a8-27e93b291821"`
- Check token expiry and refresh when needed
- Validate organization connection before claiming live data

**❌ CRITICAL ISSUE: Data Parsing Assumptions**
- **Problem**: Assuming P&L endpoint returns JSON when it returns XML
- **Symptom**: Empty responses or parsing errors
- **Root Cause**: Not checking response format

**✅ SOLUTION: Robust Response Handling**

```python
def parse_xero_response(response):
    """Parse Xero API response handling both JSON and XML."""
    if response.status_code != 200:
        return None
    
    if not response.text.strip():
        print("⚠️  Empty response from Xero API")
        return None
    
    # Check response format
    if response.text.startswith('<'):
        # XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)
        return self._parse_xml_report(root)
    else:
        # JSON response
        return response.json()
```

### 4. Data Structure Consistency

**❌ CRITICAL ISSUE: Key Mismatch**
- **Problem**: Functions expect different key names than provided
- **Symptom**: `KeyError: 'business_name'` when calling Notion API
- **Root Cause**: Inconsistent data structure between components

**✅ SOLUTION: Consistent Data Contracts**

```python
# Define clear data contracts
class ClientInfo:
    user_id: str
    business_name: str  # Consistent key naming
    industry: str
    location: str

# Validate data structure before passing between functions
def validate_client_info(client_info):
    required_keys = ['user_id', 'business_name', 'industry', 'location']
    for key in required_keys:
        if key not in client_info:
            raise ValueError(f"Missing required key: {key}")
    return client_info

# Pass complete data structures
report_data = {
    "client_info": validate_client_info(client_info),
    "forecast_data": forecast_data,  # Include all needed data
    "forecast_id": forecast_id
}
```

### 5. Error Handling and Debugging

**✅ DEBUGGING CHECKLIST**

1. **API Connectivity**
   ```bash
   # Test API endpoints directly
   curl -H "Authorization: Bearer $TOKEN" https://api.example.com/test
   ```

2. **Data Validation**
   ```python
   print(f"🔍 Data structure: {type(data)}")
   print(f"📊 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
   print(f"💰 Sample values: {str(data)[:200]}...")
   ```

3. **Token Validation**
   ```python
   # Decode JWT token to check contents
   import base64, json
   payload = token.split('.')[1]
   decoded = json.loads(base64.urlsafe_b64decode(payload + '=='))
   print(f"Token user_id: {decoded.get('xero_userid', 'Unknown')}")
   ```

### 6. Production Readiness Checklist

**Before deploying any agent:**

- [ ] **LangSmith Tracing**: Verify unified workflow traces, not isolated events
- [ ] **Live API Testing**: Confirm real data matches expected source
- [ ] **Token Management**: Implement refresh logic and expiry handling  
- [ ] **Error Handling**: Graceful fallbacks with transparent messaging
- [ ] **Data Validation**: Consistent data structures between components
- [ ] **Testing**: Test with both live APIs and fallback scenarios
- [ ] **Documentation**: Clear setup instructions and troubleshooting guide

### 7. Common Anti-Patterns to Avoid

**❌ Don't:**
- Call `tool.invoke()` directly in LangGraph workflows
- Claim data is "live" when using fallback/mock data
- Assume API response formats without checking
- Use inconsistent key names between functions
- Skip token validation and expiry checks

**✅ Do:**
- Use proper agent → tools → agent flow for LangSmith tracing
- Be transparent about data sources (real vs fallback)
- Handle both JSON and XML API responses
- Validate data structures before passing between functions
- Implement robust token management and refresh logic

## Template Files

See `/templates/production-agent/` for:
- `langsmith_traced_agent.py` - Proper tracing template
- `live_api_integration.py` - Robust API integration patterns
- `data_validation.py` - Data structure validation utilities
- `error_handling.py` - Comprehensive error handling patterns