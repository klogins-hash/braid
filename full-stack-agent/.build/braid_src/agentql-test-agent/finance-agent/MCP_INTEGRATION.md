# MCP Integration Summary

This agent has been configured with the following MCP servers:

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

## Docker Services

The following MCP servers will run as Docker services:

- `alphavantage-mcp`: python:3.12-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
