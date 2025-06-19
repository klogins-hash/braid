# MCP Integration Summary

This agent has been configured with the following MCP servers:

## Perplexity MCP Server
- **Category**: data
- **Description**: Real-time web search and research capabilities using Perplexity's Sonar API for live information retrieval
- **Repository**: https://github.com/ppl-ai/modelcontextprotocol
- **Capabilities**:
  - real_time_search
  - web_research
  - fact_checking
  - current_events
  - live_information

## AlphaVantage MCP Server
- **Category**: finance
- **Description**: Real-time and historical financial market data including stocks, forex, cryptocurrencies, and technical indicators
- **Repository**: https://github.com/calvernaz/alphavantage
- **Capabilities**:
  - stock_quotes
  - time_series_data
  - company_fundamentals
  - forex_rates
  - crypto_data
  - ... and 1 more

## Required Environment Variables

Add these variables to your `.env` file:

- `ALPHAVANTAGE_API_KEY`: [Add your value here]
- `PERPLEXITY_API_KEY`: [Add your value here]

## Docker Services

The following MCP servers will run as Docker services:

- `perplexity-mcp`: node:18-slim
- `alphavantage-mcp`: python:3.12-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
