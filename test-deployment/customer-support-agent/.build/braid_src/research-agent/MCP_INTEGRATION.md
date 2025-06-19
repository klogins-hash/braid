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

## Required Environment Variables

Add these variables to your `.env` file:

- `PERPLEXITY_API_KEY`: [Add your value here]

## Docker Services

The following MCP servers will run as Docker services:

- `perplexity-mcp`: node:18-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
