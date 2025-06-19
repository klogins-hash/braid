# MCP Integration Summary

This agent has been configured with the following MCP servers:

## MongoDB MCP Server
- **Category**: data
- **Description**: Complete MongoDB database operations and Atlas cluster management with CRUD operations, queries, and administration tools
- **Repository**: https://github.com/mongodb-js/mongodb-mcp-server
- **Capabilities**:
  - crud_operations
  - database_queries
  - aggregation
  - atlas_management
  - index_management
  - ... and 1 more

## Docker Services

The following MCP servers will run as Docker services:

- `mongodb-mcp`: node:20-slim

These are automatically configured in your `docker-compose.yml`.

## Usage

MCP tools are automatically available in your agent. You can use them just like core tools, with the appropriate prefixes.

## Documentation

See individual MCP directories in `mcp/` for specific documentation and setup instructions.
