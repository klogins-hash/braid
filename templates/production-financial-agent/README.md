# Production Financial Forecasting Agent Template

This is a battle-tested production template for building financial forecasting agents with live API integrations and proper LangSmith tracing.

## What This Template Provides

✅ **Complete Working System** - Pulls real financial data and generates forecasts  
✅ **Live API Integrations** - Xero, Perplexity, and Notion APIs working correctly  
✅ **Proper LangSmith Tracing** - Unified workflow traces, not isolated events  
✅ **Transparent Data Handling** - Clear labeling of real vs fallback data  
✅ **Robust Error Handling** - Graceful fallbacks with honest messaging  
✅ **Production Ready** - Token management, validation, and monitoring  

## Key Features Demonstrated

### 1. Live Xero API Integration
- **Real P&L Data Extraction**: Pulls actual YTD financial data from Xero organizations
- **XML Response Handling**: Properly parses Xero's XML P&L reports  
- **OAuth Token Management**: Handles token refresh and organization connections
- **Transparent Fallbacks**: Clear labeling when API data unavailable

### 2. Live Perplexity Market Research
- **Real-time Analysis**: Uses Perplexity's online models for current market data
- **Industry-specific Research**: Tailored market analysis based on company industry
- **Assumption Generation**: Market-informed forecasting assumptions

### 3. Proper LangSmith Tracing
- **Unified Workflow Traces**: All tool calls appear as connected workflow
- **Agent → Tools → Agent Flow**: Proper routing for tracing visibility
- **ToolMessage Responses**: Correct tool_call_id matching for trace continuity

### 4. 5-Year Financial Forecasting
- **P&L Modeling**: Revenue, COGS, OpEx, and profitability projections
- **Scenario Analysis**: Pessimistic, base case, and optimistic scenarios
- **Key Metrics**: CAGR, growth rates, profitability ratios
- **Validation Logic**: Assumption validation and feedback loops

## Files Included

```
templates/production-financial-agent/
├── README.md                           # This file
├── run_production_live.py             # Main production agent
├── requirements.txt                   # Dependencies
├── .env.template                      # Environment variables template
└── setup_instructions.md             # Step-by-step setup guide
```

## Quick Setup

1. **Install Dependencies**:
   ```bash
   cd templates/production-financial-agent/
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

3. **Test API Connections**:
   ```bash
   python test_api_connections.py
   ```

4. **Run Agent**:
   ```bash
   python run_production_live.py
   ```

## API Requirements

### Xero API
- **Client ID & Secret**: From Xero developer app
- **OAuth Flow**: Required for organization access
- **Scopes**: `accounting.contacts accounting.settings accounting.transactions accounting.reports.read`

### Perplexity API
- **API Key**: From Perplexity dashboard
- **Model**: Uses `llama-3.1-sonar-large-128k-online` for current data

### Notion API (Optional)
- **Integration Token**: From Notion workspace integrations
- **Page Access**: Needs existing pages to use as parents

### LangSmith (Recommended)
- **API Key**: For workflow tracing and debugging
- **Project**: To organize traces

## Architecture Patterns Demonstrated

### 1. Live API Integration Pattern
```python
def get_live_api_data(self, params):
    """Pattern for transparent live API integration."""
    try:
        # Attempt live API call
        response = self.call_api(params)
        
        if self.validate_response(response):
            real_data = self.parse_response(response)
            print(f"✅ REAL {self.api_name} data retrieved")
            return {
                **real_data,
                'data_source': f'REAL {self.api_name} API',
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"⚠️  Invalid response from {self.api_name}")
        
    except Exception as e:
        print(f"❌ {self.api_name} API error: {e}")
    
    # Transparent fallback
    print(f"🔄 Using fallback data (clearly labeled)")
    return {
        'data': self.get_fallback_data(),
        'data_source': f'{self.api_name} API Failed',
        'note': 'Fallback due to API issues'
    }
```

### 2. LangSmith Tracing Pattern
```python
def create_traced_agent():
    """Pattern for proper LangSmith tracing."""
    tools = [tool1, tool2, tool3]
    tool_map = {tool.name: tool for tool in tools}
    
    model = ChatOpenAI(model="gpt-4o")
    model = model.bind_tools(tools)  # Essential for tracing
    
    def agent_node(state: dict) -> dict:
        # Agent decides which tools to call
        response = model.invoke(messages)
        return {"messages": messages + [response]}
    
    def tool_node(state: dict) -> dict:
        # Execute tools with proper ToolMessage responses
        for tool_call in last_message.tool_calls:
            result = tool_map[tool_call['name']].invoke(tool_call['args'])
            tool_messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call['id']  # Critical for unified tracing
            ))
        return {"messages": messages + tool_messages}
    
    # Build graph with proper routing
    builder = StateGraph(dict)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    builder.add_conditional_edges("agent", should_continue)
    builder.add_conditional_edges("tools", should_continue)
    
    return builder.compile()
```

### 3. Data Validation Pattern
```python
def validate_financial_data(self, data):
    """Pattern for robust data validation."""
    required_fields = ['revenue', 'cogs', 'operating_expenses']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Convert to standard Python types (avoid numpy/pandas types)
    validated_data = {}
    for key, value in data.items():
        if isinstance(value, (np.int64, np.float64)):
            validated_data[key] = float(value)  # Convert to standard Python float
        else:
            validated_data[key] = value
    
    return validated_data
```

## Common Issues Prevented

This template prevents the major issues discovered during development:

❌ **Isolated LangSmith Traces** → ✅ Unified workflow tracing  
❌ **Fake "Live" Data Claims** → ✅ Transparent data sourcing  
❌ **Token Management Failures** → ✅ Robust OAuth handling  
❌ **XML/JSON Parsing Errors** → ✅ Format-aware response parsing  
❌ **Data Structure Mismatches** → ✅ Consistent data contracts  

## Production Deployment Notes

### Environment Variables Required
```bash
# Core APIs
XERO_CLIENT_ID="your_client_id"
XERO_CLIENT_SECRET="your_client_secret"  
XERO_ACCESS_TOKEN="your_oauth_token"
PERPLEXITY_API_KEY="your_perplexity_key"

# Optional APIs
NOTION_API_KEY="your_notion_token"

# Tracing
LANGCHAIN_API_KEY="your_langsmith_key"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="financial-forecasting"

# Core LLM
OPENAI_API_KEY="your_openai_key"
```

### Monitoring and Debugging
- **LangSmith Dashboard**: Monitor workflow execution and tool calls
- **API Logs**: Check `data_source` fields to verify live vs fallback data
- **Token Validation**: Use included token validation utilities
- **Error Tracking**: All API errors logged with context

### Scaling Considerations
- **Rate Limiting**: Implement backoff for high-volume usage
- **Caching**: Cache stable data (client info) to reduce API calls
- **Async Processing**: Consider async patterns for multiple concurrent forecasts
- **Database Integration**: Store results for audit trail and comparison

## Support and Troubleshooting

See the main documentation:
- `AGENT_DEVELOPMENT_BEST_PRACTICES.md` - Overall patterns and anti-patterns
- `XERO_API_INTEGRATION_GUIDE.md` - Xero-specific issues and solutions
- `LIVE_API_INTEGRATION_CHECKLIST.md` - Pre-deployment checklist

This template represents a production-ready pattern for building financial forecasting agents with live API integrations and proper observability.