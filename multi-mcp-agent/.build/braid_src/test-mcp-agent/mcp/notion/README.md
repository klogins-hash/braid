# Notion MCP Integration

Connect your Braid agents to Notion workspaces for comprehensive knowledge management and productivity workflows.

## Overview

The Notion MCP server provides a standardized interface for interacting with Notion workspaces, enabling your agents to:

- 📖 **Read and search** pages and databases
- ✏️ **Create and update** content
- 🗂️ **Organize** workspace structure
- 🔍 **Query** databases with filters and sorting
- 📝 **Manage** collaborative documentation

## Capabilities

### Core Tools
- `notion_search_pages` - Search for pages across workspace
- `notion_create_page` - Create new pages with rich content
- `notion_update_page` - Modify existing page content and properties
- `notion_read_database` - Query database entries with filtering
- `notion_create_database_entry` - Add new records to databases
- `notion_update_database_entry` - Modify existing database records
- `notion_list_databases` - Get all accessible databases

### Use Cases
✅ **Knowledge Management** - Search and organize company wikis  
✅ **Project Tracking** - Update project databases and task lists  
✅ **Content Creation** - Generate and edit documentation  
✅ **Meeting Notes** - Create structured meeting summaries  
✅ **CRM Operations** - Manage customer and contact databases  
✅ **Research** - Collect and organize research findings  

## Authentication Setup

### 1. Create Notion Integration
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **"Create new integration"**
3. Fill in integration details:
   - Name: "Braid Agent Integration"
   - Workspace: Select your workspace
   - Capabilities: Select Read, Update, and Insert content
4. Click **"Submit"**

### 2. Get API Key
1. Copy the **"Internal Integration Token"**
2. Set environment variable:
   ```bash
   export NOTION_API_KEY="your_integration_token_here"
   ```

### 3. Share Content with Integration
1. Navigate to pages/databases you want the agent to access
2. Click **"Share"** in the top right
3. Search for your integration name
4. Click **"Invite"**

## Integration with Braid

### Adding to Agent
When creating a new agent that needs Notion capabilities:

```bash
# The agent will prompt you about MCP integrations
braid new my-knowledge-agent --production --tools files,csv

# During setup, if you mention Notion-related tasks, 
# the agent will suggest adding the Notion MCP
```

### Environment Configuration
Add to your agent's `.env` file:
```bash
# Required
NOTION_API_KEY=secret_your_integration_token

# Optional - default workspace
NOTION_WORKSPACE_ID=your_workspace_id
```

### Docker Integration
The Notion MCP runs as a separate service alongside your agent:

```yaml
# Auto-generated in docker-compose.yml
services:
  agent:
    # Your main agent
    
  notion-mcp:
    image: node:18-slim
    environment:
      - NOTION_API_KEY=${NOTION_API_KEY}
    command: ["npx", "-y", "@makenotion/notion-mcp-server"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
```

## Example Usage

### Search and Read Pages
```python
# Search for pages about a topic
results = await notion_search_pages("project planning")

# Read specific database
database_data = await notion_read_database(
    database_id="abc123",
    filter={"Status": {"equals": "In Progress"}}
)
```

### Create Content
```python
# Create a new project page
new_page = await notion_create_page(
    title="Q4 Marketing Campaign",
    content="## Overview\nPlanning for Q4 marketing initiatives...",
    parent_id="parent_page_id"
)

# Add entry to project database
await notion_create_database_entry(
    database_id="projects_db",
    properties={
        "Name": {"title": [{"text": {"content": "Q4 Campaign"}}]},
        "Status": {"select": {"name": "Planning"}},
        "Due Date": {"date": {"start": "2024-12-31"}}
    }
)
```

## Troubleshooting

### Common Issues

**Authentication Errors:**
- Verify NOTION_API_KEY is set correctly
- Check that integration has proper permissions
- Ensure pages/databases are shared with integration

**Connection Issues:**
- Verify internet connectivity
- Check Notion API status
- Review Docker container logs

**Permission Errors:**
- Re-share relevant pages with integration
- Verify integration has required capabilities
- Check workspace permissions

### Rate Limits
- Notion API: 3 requests per second
- The MCP server handles rate limiting automatically
- Consider caching for frequently accessed content

## Support

- **Notion MCP Issues**: [GitHub Repository](https://github.com/makenotion/notion-mcp-server/issues)
- **Braid Integration Issues**: See main Braid documentation
- **Notion API Documentation**: [Notion Developers](https://developers.notion.com/)

## Version Compatibility

- **Braid**: >= 1.0.0
- **MCP Protocol**: >= 1.0.0
- **Node.js**: >= 18.0.0
- **Notion API**: v1 (current)