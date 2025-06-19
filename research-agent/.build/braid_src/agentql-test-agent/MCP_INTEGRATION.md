# MCP Integration Summary

This agent has been configured with the following MCP servers:

## AgentQL MCP Server
- **Category**: development
- **Description**: Web data extraction and structured scraping capabilities using AI-powered web automation
- **Repository**: https://github.com/tinyfish-io/agentql-mcp
- **Capabilities**:
  - extract_web_data
  - structured_scraping
  - web_automation

## Required Environment Variables

Add these variables to your `.env` file:

- `AGENTQL_API_KEY`: [Add your value here]

## Docker Services

The following MCP servers will run as Docker services:

- `agentql-mcp`: node:18-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
