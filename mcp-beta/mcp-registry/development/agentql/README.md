# AgentQL MCP Server

AgentQL MCP provides web data extraction and structured scraping capabilities through the Model Context Protocol.

## Overview

AgentQL allows AI agents to extract structured data from websites using natural language descriptions. Instead of writing complex scraping code, you describe what data you want to extract, and AgentQL handles the web automation.

## Capabilities

### Tools Available

- **`extract-web-data`**: Extracts structured data from any URL using descriptive prompts
  - Input: URL, data schema definition, extraction prompt  
  - Output: Structured JSON data matching your schema
  - Use cases: Product info, contact details, pricing, news articles, etc.

## Setup Instructions

### 1. Get AgentQL API Key

1. Visit [https://dev.agentql.com](https://dev.agentql.com)
2. Sign up for an account
3. Navigate to the Developer Portal
4. Generate an API key

### 2. Environment Configuration

Add to your `.env` file:

```bash
AGENTQL_API_KEY=your-agentql-api-key-here
```

### 3. Installation

The MCP server is automatically installed when using Braid's Docker orchestration:

```bash
braid package --production
docker compose up --build
```

For manual installation:
```bash
npm install -g agentql-mcp
```

## Usage Examples

### Extract Product Information

```python
# The agent can now use AgentQL tools directly
result = agent.extract_web_data(
    url="https://example-store.com/product/123",
    data_schema={
        "product_name": "string",
        "price": "number", 
        "availability": "string",
        "reviews_count": "number"
    },
    prompt="Extract product details including name, price, stock status, and review count"
)
```

### Extract Contact Information

```python
contacts = agent.extract_web_data(
    url="https://company.com/contact",
    data_schema={
        "email": "string",
        "phone": "string",
        "address": "string",
        "business_hours": "string"
    },
    prompt="Find all contact information including email, phone, address, and hours"
)
```

### Market Research Data

```python
market_data = agent.extract_web_data(
    url="https://competitor.com/pricing",
    data_schema={
        "plans": [
            {
                "name": "string",
                "price": "number",
                "features": ["string"]
            }
        ]
    },
    prompt="Extract pricing plans with names, costs, and key features"
)
```

## Use Cases

- **Competitive Intelligence**: Monitor competitor pricing, features, and announcements
- **Lead Generation**: Extract contact information from business directories
- **Market Research**: Gather pricing data, product information, and market trends
- **Content Aggregation**: Collect articles, news, and research from multiple sources
- **E-commerce Monitoring**: Track product availability, prices, and reviews
- **SEO Analysis**: Extract meta data, headings, and page structure information

## Best Practices

### 1. Descriptive Prompts
- Be specific about what data you want to extract
- Provide context about the website structure
- Use clear field names in your data schema

### 2. Handle Rate Limits
- AgentQL handles rate limiting internally
- For high-volume usage, consider implementing delays between requests
- Monitor your API usage in the AgentQL dashboard

### 3. Error Handling
- Always check if the extraction was successful
- Have fallback strategies for missing data
- Validate extracted data format

### 4. Respect Website Terms
- Review website terms of service before scraping
- Use appropriate request intervals
- Consider robots.txt guidelines

## Troubleshooting

### Common Issues

**API Key Not Working**
- Verify the key is correctly set in your `.env` file
- Check that the API key has not expired
- Ensure you have sufficient API credits

**Data Not Extracted**
- Check if the website structure has changed
- Refine your extraction prompt to be more specific
- Verify the target URL is accessible

**Rate Limiting**
- AgentQL automatically handles rate limits
- If you hit limits, wait before retrying
- Consider upgrading your AgentQL plan for higher limits

### Debug Mode

To see detailed extraction logs:

```bash
# Set debug environment variable
DEBUG=agentql* npx agentql-mcp
```

## Integration with Braid

When using AgentQL MCP with Braid agents, the tools are automatically available with the `agentql_` prefix:

- `agentql_extract_web_data()` - Main data extraction tool

The MCP runs in a separate Docker container with proper networking and health checks configured automatically.

## Security Notes

- API keys are passed securely through environment variables
- The MCP server runs in an isolated Docker container
- External network access is required for web scraping
- All data extraction follows AgentQL's security and privacy policies

## Support

- **AgentQL Documentation**: [https://docs.agentql.com](https://docs.agentql.com)
- **GitHub Repository**: [https://github.com/tinyfish-io/agentql-mcp](https://github.com/tinyfish-io/agentql-mcp)
- **API Support**: Contact AgentQL support through their developer portal