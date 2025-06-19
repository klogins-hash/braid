# Live API Integration Checklist

## Pre-Development Checklist

**Before building any agent with live APIs:**

- [ ] **API Documentation Review**
  - [ ] Understand authentication requirements (OAuth vs API key vs client credentials)
  - [ ] Identify response formats (JSON vs XML vs CSV)
  - [ ] Check rate limits and quotas
  - [ ] Review required scopes/permissions
  - [ ] Test endpoints with curl/Postman first

- [ ] **Authentication Setup**
  - [ ] Obtain proper credentials (not just testing credentials)
  - [ ] Test token generation and validation
  - [ ] Implement token refresh logic
  - [ ] Verify organization/account access

- [ ] **Data Structure Analysis**
  - [ ] Map API response fields to your data model
  - [ ] Handle nested/complex response structures
  - [ ] Plan for missing or null fields
  - [ ] Define clear data contracts between components

## Development Checklist

**While building the agent:**

- [ ] **Transparent Data Sourcing**
  - [ ] Always label data source accurately (`REAL API`, `Fallback`, `Mock`)
  - [ ] Include metadata about data freshness and completeness
  - [ ] Never claim live data when using fallbacks
  - [ ] Log data source decisions clearly

- [ ] **Error Handling**
  - [ ] Handle network timeouts and connection errors
  - [ ] Parse API error responses properly
  - [ ] Implement graceful fallbacks with clear labeling
  - [ ] Log all API errors with context

- [ ] **Response Parsing**
  - [ ] Check response format before parsing (JSON vs XML)
  - [ ] Handle empty responses gracefully
  - [ ] Validate required fields exist
  - [ ] Convert data types explicitly (avoid numpy/pandas types)

- [ ] **LangSmith Tracing Integration**
  - [ ] Never call `tool.invoke()` directly in workflows
  - [ ] Use proper agent → tools → agent flow
  - [ ] Include ToolMessage responses with matching `tool_call_id`
  - [ ] Test unified workflow traces in LangSmith dashboard

## Testing Checklist

**Before considering the integration complete:**

- [ ] **API Connectivity Tests**
  - [ ] Test with valid credentials
  - [ ] Test with expired/invalid credentials
  - [ ] Test with network disconnection
  - [ ] Test rate limiting scenarios

- [ ] **Data Validation Tests**
  - [ ] Compare API data with source system UI
  - [ ] Test with different date ranges/filters
  - [ ] Verify calculations match source system
  - [ ] Test edge cases (zero revenue, negative values)

- [ ] **Integration Tests**
  - [ ] Full workflow with live APIs
  - [ ] Fallback scenarios when APIs fail
  - [ ] Mixed scenarios (some APIs work, others fail)
  - [ ] LangSmith trace verification

- [ ] **Production Readiness**
  - [ ] Token refresh works automatically
  - [ ] Error messages are user-friendly
  - [ ] Logging provides debugging information
  - [ ] Performance is acceptable under load

## Common Anti-Patterns to Avoid

### ❌ Authentication Anti-Patterns

```python
# DON'T: Use testing credentials in production
XERO_ACCESS_TOKEN = "test_token_12345"

# DON'T: Ignore token expiry
def get_data():
    return requests.get(url, headers={'Authorization': f'Bearer {old_token}'})

# DON'T: Hard-code organization IDs
tenant_id = "12345-abcde-67890"  # Will break for other users
```

### ✅ Authentication Best Practices

```python
# DO: Implement proper token management
class TokenManager:
    def get_valid_token(self):
        if self.is_expired():
            self.refresh_token()
        return self.access_token

# DO: Handle multiple organizations
def get_organizations(self):
    response = requests.get('https://api.xero.com/connections', headers=self.headers)
    return response.json()
```

### ❌ Data Handling Anti-Patterns

```python
# DON'T: Assume response format
data = response.json()  # Fails if API returns XML

# DON'T: Claim live data when using fallbacks
return {
    'revenue': 1000000,  # Hardcoded value
    'data_source': 'Live API'  # Misleading claim
}

# DON'T: Ignore data validation
revenue = api_response['revenue']  # May not exist or be wrong type
```

### ✅ Data Handling Best Practices

```python
# DO: Check response format
def parse_response(response):
    if response.text.startswith('<'):
        return parse_xml(response.text)
    else:
        return response.json()

# DO: Be transparent about data sources
def get_financial_data(self):
    try:
        real_data = self.call_api()
        return {
            **real_data,
            'data_source': 'REAL API',
            'timestamp': datetime.now().isoformat()
        }
    except APIError:
        return {
            'revenue': 0,
            'data_source': 'API Failed - Using Fallback',
            'note': 'Live API unavailable'
        }

# DO: Validate and convert data types
def extract_revenue(api_response):
    revenue_raw = api_response.get('revenue', 0)
    try:
        return float(revenue_raw)  # Convert to standard Python type
    except (ValueError, TypeError):
        return 0.0
```

### ❌ LangSmith Tracing Anti-Patterns

```python
# DON'T: Direct tool invocation (creates isolated traces)
def run_workflow():
    client_data = get_client_tool.invoke({'id': 'user_123'})
    api_data = get_api_tool.invoke({'client': client_data})
    # Each appears as isolated event in LangSmith
```

### ✅ LangSmith Tracing Best Practices

```python
# DO: Proper agent flow (creates unified traces)
def agent_node(state):
    messages = state.get("messages", [])
    response = model.invoke(messages)  # Model decides tools
    return {"messages": messages + [response]}

def tool_node(state):
    # Execute tools and create ToolMessage responses
    for tool_call in last_message.tool_calls:
        result = tool_map[tool_call['name']].invoke(tool_call['args'])
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call['id']  # Critical for unified tracing
        ))
    return {"messages": messages + tool_messages}
```

## API-Specific Considerations

### Xero API
- **Format**: Reports return XML, other endpoints return JSON
- **Auth**: OAuth required for organization access (client credentials has limitations)
- **Scope**: Need `accounting.reports.read` for P&L reports
- **Gotcha**: Client credentials shows 0 connections

### Notion API
- **Format**: JSON with complex nested structures
- **Auth**: Integration token with workspace permissions
- **Scope**: Page creation requires parent page access
- **Gotcha**: Must find existing pages to use as parents

### Perplexity API
- **Format**: Standard JSON chat completion format
- **Auth**: Bearer token authentication
- **Rate Limits**: Usage-based billing
- **Gotcha**: Online models provide fresh data, base models don't

### QuickBooks API
- **Format**: JSON with OAuth 2.0
- **Auth**: Requires app registration and user consent
- **Scope**: Company-specific access tokens
- **Gotcha**: Sandbox vs production environments

## Debugging Tools

### API Testing Commands

```bash
# Test Xero connection
curl -H "Authorization: Bearer $XERO_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.xero.com/connections

# Test Notion access
curl -H "Authorization: Bearer $NOTION_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/users/me

# Test Perplexity
curl -X POST "https://api.perplexity.ai/chat/completions" \
     -H "Authorization: Bearer $PERPLEXITY_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "llama-3.1-sonar-small-128k-online", "messages": [{"role": "user", "content": "test"}]}'
```

### Token Validation

```python
def validate_jwt_token(token):
    """Decode JWT token to check contents and expiry."""
    import base64, json
    from datetime import datetime
    
    try:
        # Decode payload (second part of JWT)
        payload = token.split('.')[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        
        print(f"Token user_id: {decoded.get('xero_userid', 'N/A')}")
        print(f"Expires: {datetime.fromtimestamp(decoded.get('exp', 0))}")
        print(f"Scopes: {decoded.get('scope', [])}")
        
        return decoded
    except Exception as e:
        print(f"Token validation error: {e}")
        return None
```

This checklist prevents the major issues we encountered during financial forecasting agent development and ensures robust live API integrations.

## Related Documentation

See also:
- [Agent Development Best Practices](../agent-development/AGENT_DEVELOPMENT_BEST_PRACTICES.md) - Overall patterns and anti-patterns
- [Xero API Integration Guide](./XERO_API_INTEGRATION_GUIDE.md) - Xero-specific troubleshooting
- [Production Financial Agent Template](../../../templates/production-financial-agent/) - Working example
- [Production Best Practices](../../tutorials/langgraph_agent_guide/08_production_best_practices.md) - LangSmith tracing