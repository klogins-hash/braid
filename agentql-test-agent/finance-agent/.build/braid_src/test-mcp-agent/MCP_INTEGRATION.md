# MCP Integration Summary

This agent has been configured with the following MCP servers:

## Notion MCP Server
- **Category**: productivity
- **Description**: Connect to Notion workspaces for reading, creating, and updating pages and databases
- **Repository**: https://github.com/makenotion/notion-mcp-server
- **Capabilities**:
  - search_pages
  - create_pages
  - update_pages
  - read_databases
  - create_database_entries
  - ... and 2 more

## Required Environment Variables

Add these variables to your `.env` file:

- `NOTION_API_KEY`: [Add your value here]

## Docker Services

The following MCP servers will run as Docker services:

- `notion-mcp`: node:18-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
