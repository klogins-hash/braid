# Financial Operations Assistant

An intelligent LangGraph agent that automates routine financial reporting for small businesses and teams. Fetches real financial data, adds market context, generates professional reports, and sends notifications.

## 🚀 Features

✅ **Live Financial Data** - Pulls real P&L, balance sheets, and invoices from Xero  
✅ **Market Intelligence** - Adds industry context via Perplexity research  
✅ **Professional Reports** - Creates structured Notion pages with analysis  
✅ **Smart Notifications** - Sends summaries and links via Slack  
✅ **Natural Language** - Processes flexible requests like "show Q2 performance"  
✅ **Production Ready** - Proper error handling, tracing, and transparency  

## 🏗️ Architecture

### Workflow
1. **Parse Request** → Extract reporting period and requirements
2. **Fetch Financial Data** → Get real Xero financial reports  
3. **Market Analysis** → Add context via Perplexity research
4. **Generate Report** → Create structured Notion page
5. **Notify Team** → Send Slack summary with report link

### Core Integrations
- **Xero API** - P&L statements, balance sheets, trial balances
- **Perplexity API** - Market trends and industry analysis  
- **Notion API** - Structured report generation
- **Slack API** - Notifications and command triggers
- **LangSmith** - Unified workflow tracing

## 🔧 Setup

### 1. Install Dependencies
```bash
cd agents/financial-operations-assistant/
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.template .env
# Edit .env with your API keys (see API Setup section)
```

### 3. Test Connections
```bash
python test_agent.py
```

### 4. Run Agent
```bash
python agent.py
```

## 🔑 API Setup

### Required APIs

#### Xero API
1. Add your Xero app credentials to `.env`:
   ```
   XERO_CLIENT_ID=your_client_id
   XERO_CLIENT_SECRET=your_client_secret
   ```
2. Run token refresh:
   ```bash
   python refresh_xero_tokens.py
   ```
3. This will automatically update your `.env` with fresh tokens

#### Perplexity API  
1. Get API key from [Perplexity](https://www.perplexity.ai/)
2. Add to `.env`:
   ```
   PERPLEXITY_API_KEY=your_api_key
   ```

#### Notion API
1. Create integration at [Notion Developers](https://developers.notion.com/)
2. Share target pages with your integration
3. Add to `.env`:
   ```
   NOTION_API_KEY=your_integration_token
   NOTION_DEFAULT_PAGE_ID=parent_page_id
   ```

#### OpenAI API
1. Get API key from [OpenAI](https://platform.openai.com/)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=your_api_key
   ```

### Optional APIs

#### Slack API (for notifications)
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_DEFAULT_CHANNEL=your-channel-id
```

#### LangSmith (for tracing)
```
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=financial-operations-assistant
```

## 💬 Usage Examples

### Natural Language Requests
- `"Generate monthly financial report"`
- `"Show me Q2 performance with market context"`
- `"Create weekly summary for the team"`
- `"Pull YTD P&L and compare to last year"`

### Slack Commands (when configured)
- `@FinanceBot monthly report`
- `@FinanceBot show Q3 performance`
- `@FinanceBot weekly update`

## 📊 Generated Reports

The agent creates comprehensive Notion reports including:

### Executive Summary
- Key financial metrics and trends
- Period-over-period comparisons
- Market context and insights

### Financial Data Tables
- P&L statement with analysis
- Balance sheet key ratios
- Cash flow indicators

### Market Analysis
- Industry trends relevant to business
- Economic indicators and context
- Competitive landscape insights

### Action Items
- Recommendations based on data
- Areas requiring attention
- Opportunities for improvement

## 🔍 Data Transparency

The agent follows strict transparency rules:
- ✅ **Real Data Labeled** - "REAL Xero API data retrieved"
- ⚠️ **Fallbacks Noted** - "Using fallback data due to API issues"
- 📅 **Timestamps** - All data includes retrieval timestamps
- 🏷️ **Source Attribution** - Clear data source labeling

## 🛠️ Troubleshooting

### Common Issues

**"XERO_ACCESS_TOKEN not set"**
- Run Xero OAuth setup: `python -m core.integrations.xero.setup`
- Tokens expire and need refresh

**"Notion page creation failed"**
- Verify integration has access to parent page
- Check `NOTION_DEFAULT_PAGE_ID` is correct

**"Perplexity API error"**
- Verify API key is active
- Check rate limits

### Debug Mode
Add to `.env` for detailed logging:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

### Test Individual Components
```bash
# Test Xero connection
python -c "from core.integrations.xero.tools import get_xero_profit_and_loss; print(get_xero_profit_and_loss.invoke({}))"

# Test Perplexity 
python -c "from core.integrations.perplexity.tools import perplexity_ask; print(perplexity_ask.invoke({'query': 'test'}))"
```

## 🚀 Production Deployment

### Environment Variables Checklist
- [ ] `OPENAI_API_KEY` - GPT-4 access
- [ ] `XERO_ACCESS_TOKEN` & `XERO_TENANT_ID` - Financial data
- [ ] `PERPLEXITY_API_KEY` - Market research  
- [ ] `NOTION_API_KEY` & `NOTION_DEFAULT_PAGE_ID` - Report generation
- [ ] `SLACK_BOT_TOKEN` - Notifications (optional)
- [ ] `LANGCHAIN_API_KEY` - Tracing (recommended)

### Scheduling Options
- **Cron Jobs** - Unix/Linux scheduling
- **GitHub Actions** - Automated workflows
- **AWS Lambda** - Serverless execution
- **Docker** - Containerized deployment

### Monitoring
- **LangSmith Dashboard** - Workflow tracing and debugging
- **API Rate Limits** - Monitor usage across services
- **Error Logs** - Track and alert on failures
- **Data Freshness** - Verify regular successful runs

## 📝 Customization

### Add New Financial Metrics
Edit `agent.py` to include additional Xero tools:
```python
from core.integrations.xero.tools import get_xero_invoices
financial_tools.append(get_xero_invoices)
```

### Modify Report Format
Update the Notion report generation in `tools_node`:
```python
# Customize report structure and content
report_content = generate_custom_report(financial_data, market_context)
```

### Change Analysis Depth
Adjust Perplexity research prompts:
```python
# Modify market research depth and focus
market_prompt = f"Analyze {industry} trends for {timeframe} with focus on {specific_areas}"
```

## 🤝 Support

For issues and questions:
- Check troubleshooting section above
- Review [Braid Documentation](../../docs/)
- Test individual API connections first
- Verify environment variable setup

Built with ❤️ using the Braid LangGraph framework.