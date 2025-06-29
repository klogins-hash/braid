# Mural Content Assistant Agent

A natural language interface for the Mural API that enables users to create, manage, and collaborate on visual workspaces through conversational commands.

## Overview

The Mural Content Assistant provides intuitive natural language access to Mural's visual collaboration platform. Users can create murals, add content like sticky notes and text boxes, manage collaborators, and search existing workspaces—all through simple conversational requests.

## Features

### Core Capabilities
- **Mural Management**: Create, search, and manage murals
- **Content Creation**: Add sticky notes, text boxes, titles, and other widgets
- **Content Discovery**: Search murals, templates, and workspaces
- **Collaboration**: Manage users, permissions, and access

### Example Interactions
```
User: "Create a new retrospective mural for our sprint team"
Agent: "Created 'Sprint Retrospective' mural in your workspace. Link: [URL]"

User: "Add sticky notes for What Went Well, What Could Improve, and Action Items"
Agent: "Added three section headers to your retrospective mural!"

User: "Find murals about user research from last month" 
Agent: "Found 3 user research murals: [detailed list with links]"
```

## Setup

### 1. Environment Variables
Copy `.env.example` to `.env` and fill in your Mural API credentials:

```env
# Required: Mural API Authentication
MURAL_ACCESS_TOKEN=your_access_token_here
MURAL_CLIENT_ID=your_client_id_here
MURAL_CLIENT_SECRET=your_client_secret_here

# Required: OpenAI API for LLM
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Default workspace/room settings
MURAL_DEFAULT_WORKSPACE_ID=your_default_workspace_id
MURAL_DEFAULT_ROOM_ID=your_default_room_id
```

### 2. Getting Mural API Credentials

1. **Sign up for Mural API Beta**: Visit [developers.mural.co](https://developers.mural.co) and join the beta program
2. **Create an App**: Register your application to get Client ID and Secret
3. **OAuth Flow**: Complete OAuth to get your access token
4. **Find IDs**: Use the API to find your workspace and room IDs for defaults

### 3. Authentication Setup
The agent uses OAuth2 with the following scopes:
- `murals:read` - Read mural content and metadata
- `murals:write` - Create and modify murals
- `users:read` - Access user and collaboration information

### 4. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Test the agent
python agent.py
```

## Usage

### Interactive Mode
```bash
python agent.py
```
This starts an interactive chat session where you can give natural language commands.

### Test Mode
```bash
python agent.py test
```
Runs predefined test queries to verify the agent is working correctly.

### Example Commands
- `"Create a brainstorming mural for our product ideas"`
- `"Add a sticky note saying 'User feedback integration'"`
- `"Who has access to the design system mural?"`
- `"Search for templates about retrospectives"`
- `"Show me all murals in the Marketing workspace"`

## API Coverage

### Implemented Operations (12 Core Tools)

**Mural Management:**
- `create_mural()` - Create new murals with custom settings
- `get_mural_details()` - Retrieve mural information and metadata
- `search_murals()` - Find murals by keywords, workspace, or date
- `get_workspace_murals()` - List all murals in a workspace

**Content Creation:**
- `create_sticky_note()` - Add sticky notes with custom text and styling
- `create_textbox()` - Add formatted text blocks
- `create_title()` - Add section titles and headers
- `get_mural_widgets()` - View existing content and widgets

**User & Collaboration:**
- `get_mural_users()` - See current collaborators
- `invite_users_to_mural()` - Add team members to murals
- `get_workspaces()` - List available workspaces
- `search_templates()` - Find mural templates

## Architecture

The agent follows Braid's direct integration pattern:
- **LangGraph workflow**: Agent → Tools → Agent flow with proper tracing
- **Direct API calls**: No MCP servers, direct HTTP to Mural API
- **Error handling**: Graceful fallbacks with clear error messages
- **Data transparency**: All responses indicate data source and authenticity

### File Structure
```
mural-content-assistant/
├── agent.py              # Main LangGraph agent implementation
├── mural_tools.py         # Mural API integration tools
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── README.md             # This documentation
└── demo_test.py          # Example usage and testing (optional)
```

## Error Handling

The agent provides graceful error handling for common scenarios:
- **Authentication errors**: Clear guidance on token setup
- **Permission errors**: Explains access requirements
- **API rate limits**: Automatic retry with exponential backoff
- **Resource not found**: Helpful suggestions for alternatives

## Data Sources

All responses clearly indicate data authenticity:
- **Real data**: "REAL Mural API - Direct Integration"
- **Fallback data**: "Mural API Failed - Using Demo Data"
- **Mock data**: "Demo Data - For Development"

## Troubleshooting

### Common Issues

1. **"Mural API token not configured"**
   - Ensure `MURAL_ACCESS_TOKEN` is set in your `.env` file
   - Verify the token hasn't expired

2. **"No room ID specified"**
   - Set `MURAL_DEFAULT_ROOM_ID` in `.env`
   - Or specify room_id in your requests

3. **401 Unauthorized errors**
   - Check that your OAuth token has the required scopes
   - Verify the token is still valid

4. **403 Forbidden errors**
   - Ensure you have permission to access the workspace/room
   - Check if the resource exists and you're a member

### Debug Mode
Set `DEBUG=true` in your `.env` file for verbose logging.

## Production Considerations

- **Security**: OAuth tokens managed securely via environment variables
- **Rate limiting**: Built-in respect for API limits and throttling
- **Monitoring**: LangSmith tracing for debugging and optimization
- **Scalability**: Designed for team and enterprise usage patterns

## Limitations

- **Beta API**: Mural API is currently in beta, some features may change
- **Content types**: Currently supports text-based widgets (sticky notes, text boxes, titles)
- **Visual elements**: Does not yet support images, drawings, or complex shapes
- **Real-time updates**: No live collaboration features

## Future Enhancements

- Support for images and file uploads
- Advanced widget types (shapes, arrows, tables)
- Bulk operations for content management
- Integration with other Braid tools (Slack, Notion)
- Real-time collaboration features
- Advanced search and filtering capabilities

## Contributing

When extending this agent:
1. Follow Braid's direct integration patterns
2. Add proper error handling and fallbacks
3. Include data source transparency
4. Update this README with new capabilities
5. Add tests for new functionality

## Support

For issues or questions:
1. Check the Mural API documentation: https://developers.mural.co
2. Review Braid development patterns in `/docs/`
3. Test with the included interactive mode: `python agent.py`
4. Check environment configuration in `.env`