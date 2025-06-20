# Perplexity MCP Server

Perplexity MCP provides real-time web search and research capabilities through Perplexity's Sonar API, enabling AI agents to access current information from across the web.

## Overview

Perplexity AI's Sonar API delivers real-time search results with AI-powered summarization. This MCP server integrates those capabilities, allowing agents to perform live web research, fact-checking, and information retrieval without leaving the conversation context.

## Capabilities

### Core Search Tool

- **`pplx_perplexity_ask`**: Real-time web search and research
  - Input: Conversation messages with roles (system, user, assistant)
  - Output: AI-summarized search results with sources and citations
  - Features: Live web data, current events, breaking news, fact verification

### Key Features

- **Real-time Information**: Access to current web data and recent developments
- **AI Summarization**: Intelligent synthesis of multiple sources
- **Source Citations**: Credible references for all information provided
- **Conversational Context**: Maintains conversation flow with search results
- **Multiple Domains**: Search across news, academic, technical, and general web content

## Setup Instructions

### 1. Get Perplexity API Key

1. Visit [https://www.perplexity.ai/](https://www.perplexity.ai/)
2. Sign up for an account
3. Navigate to the API section in your dashboard
4. Generate an API key
5. Note: Both free and paid tiers available with different rate limits

### 2. Environment Configuration

Add to your `.env` file:

```bash
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

### 3. Installation

The MCP server is automatically installed when using Braid's Docker orchestration:

```bash
braid package --production
docker compose up --build
```

For manual installation:
```bash
git clone https://github.com/ppl-ai/modelcontextprotocol.git
cd modelcontextprotocol/perplexity-ask
npm install
npm start
```

## Usage Examples

### Real-time Research

```python
# Get current information on any topic
research_result = agent.pplx_perplexity_ask([
    {
        "role": "user", 
        "content": "What are the latest developments in AI safety research in 2024?"
    }
])

# Result includes current information with sources
print(f"Research findings: {research_result['content']}")
print(f"Sources: {research_result['sources']}")
```

### Fact Checking

```python
# Verify claims with real-time data
fact_check = agent.pplx_perplexity_ask([
    {
        "role": "system",
        "content": "You are a fact-checking assistant. Verify claims with current data."
    },
    {
        "role": "user",
        "content": "Is it true that renewable energy now accounts for over 30% of global electricity generation?"
    }
])
```

### Current Events Monitoring

```python
# Stay updated on breaking news
news_update = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "What are the most significant technology news stories from this week?"
    }
])

# Get market-specific updates
market_news = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "What are the latest developments affecting the semiconductor industry?"
    }
])
```

### Academic Research

```python
# Find recent academic publications
academic_search = agent.pplx_perplexity_ask([
    {
        "role": "system",
        "content": "Focus on peer-reviewed sources and recent publications."
    },
    {
        "role": "user",
        "content": "What are the latest research findings on quantum computing error correction?"
    }
])
```

### Competitive Intelligence

```python
# Research competitors and market trends
market_research = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "What are the recent product announcements and funding news in the AI startup space?"
    }
])

# Product research
product_analysis = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "Compare the latest features and pricing of major project management tools launched in 2024"
    }
])
```

### Travel and Current Conditions

```python
# Get current travel information
travel_info = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "What are the current travel restrictions and weather conditions for visiting Japan?"
    }
])

# Event and conference updates
event_info = agent.pplx_perplexity_ask([
    {
        "role": "user",
        "content": "What are the major tech conferences happening in the next 3 months?"
    }
])
```

## Use Cases

### Research & Analysis
- **Academic Research**: Access to latest publications and studies
- **Market Research**: Real-time industry trends and competitor analysis
- **Technology Trends**: Current developments in AI, blockchain, startups
- **Policy & Regulation**: Latest government policies and regulatory changes

### News & Current Events
- **Breaking News**: Real-time updates on global events
- **Industry News**: Sector-specific updates and announcements
- **Financial Markets**: Current market conditions and economic indicators
- **Technology Announcements**: Product launches and company news

### Business Intelligence
- **Competitive Analysis**: Competitor moves and market positioning
- **Investment Research**: Due diligence on companies and markets
- **Trend Analysis**: Emerging trends and future predictions
- **Risk Assessment**: Current risks and mitigation strategies

### Content Creation
- **Fact Verification**: Ensure accuracy of claims and statements
- **Current Examples**: Use recent, relevant examples in content
- **Trend Integration**: Incorporate latest trends into content strategy
- **Source Discovery**: Find credible sources for citations

## Best Practices

### 1. Effective Query Construction
- **Be Specific**: Include timeframes, regions, or specific aspects you're interested in
- **Use Context**: Provide background context for better results
- **Ask Follow-ups**: Build on previous responses for deeper research

### 2. Source Verification
- Always review the sources provided with search results
- Cross-reference important information with multiple sources
- Consider the credibility and recency of sources

### 3. Rate Limit Management
- **Monitor Usage**: Track API calls to stay within limits
- **Batch Related Queries**: Combine related questions when possible
- **Cache Results**: Store frequently accessed information locally

### 4. Query Optimization
```python
# Good: Specific and contextual
query = "What are the latest FDA approvals for Alzheimer's treatments in 2024?"

# Better: Include specific context
query_with_context = """
I'm researching pharmaceutical developments for a healthcare investment analysis. 
What are the latest FDA approvals for Alzheimer's treatments in 2024, including 
their mechanisms of action and market potential?
"""
```

## Rate Limiting & API Usage

### API Limits
- **Free Tier**: Limited requests per month
- **Paid Plans**: Higher rate limits and additional features
- **Rate Limiting**: Automatic backoff and retry handling

### Usage Optimization
1. **Combine Queries**: Ask multiple related questions in one request
2. **Use Conversation Context**: Build on previous responses
3. **Cache Results**: Store search results for repeated access
4. **Monitor Quotas**: Track usage through Perplexity dashboard

## Troubleshooting

### Common Issues

**API Key Not Working**
- Verify the key is correctly set in your `.env` file
- Check that the API key is active in your Perplexity dashboard
- Ensure you haven't exceeded your API quota

**Search Results Quality**
- Refine your queries to be more specific
- Provide more context in your search terms
- Use follow-up questions to drill down into topics

**Rate Limiting**
- Monitor your API usage in the Perplexity dashboard
- Implement delays between requests if needed
- Consider upgrading to a higher-tier plan

**Network Issues**
- Ensure the container has internet access
- Check firewall settings for outbound HTTPS connections
- Verify DNS resolution for api.perplexity.ai

### Debug Mode

To see detailed API interaction logs:

```bash
# Set debug environment variable
DEBUG=perplexity* npm start
```

## Integration with Braid

When using Perplexity MCP with Braid agents, the tools are automatically available with the `pplx_` prefix:

- `pplx_perplexity_ask()` - Real-time web search and research

The MCP runs in a separate Docker container with proper networking, caching, and error handling configured automatically.

## Security Notes

- **API Keys**: Securely stored in environment variables
- **Request Logging**: Search queries may be logged by Perplexity for service improvement
- **Data Privacy**: Review Perplexity's privacy policy for data handling details
- **Rate Limiting**: Built-in respect for API quotas and limits

## Advanced Configuration

### Custom Search Parameters

You can modify search behavior by updating the MCP server configuration:

```javascript
// Modify search parameters in index.ts
const searchParams = {
  model: "sonar-small-online",
  temperature: 0.2,
  max_tokens: 1000,
  top_p: 0.9
};
```

### Response Customization

Configure response formatting and source handling:

```javascript
// Customize response processing
const responseConfig = {
  include_sources: true,
  max_sources: 5,
  source_format: "citations"
};
```

## Support

- **Perplexity Documentation**: [https://docs.perplexity.ai/](https://docs.perplexity.ai/)
- **MCP Repository**: [https://github.com/ppl-ai/modelcontextprotocol](https://github.com/ppl-ai/modelcontextprotocol)
- **API Support**: Contact Perplexity through their support channels
- **Community**: Join Perplexity's developer community for updates and discussions