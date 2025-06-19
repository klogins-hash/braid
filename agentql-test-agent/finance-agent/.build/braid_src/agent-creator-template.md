# Agent Requirements Template

## Core Tasks and Sequences of Agent

**Description**: Provide a detailed description of what the agent should do, including the sequence of actions and expected behavior.

**Example**: For every upcoming sales meeting on my Google Calendar, search the prospect in Perplexity and return a concise summary in the #Sales-Prep slack channel.

**Your Requirements**: 
[Replace this with your specific task description]

## Tools Agent Should Use

**📋 Complete Tool Reference**: See [TOOL_REFERENCE.md](./TOOL_REFERENCE.md) for detailed documentation of all available tools.

**🏷️ Available Tool Categories**:

**🏢 External Integrations**:
- **gworkspace**: Gmail, Google Calendar, Google Sheets, Google Drive (4 tools)
- **slack**: Team messaging, notifications, file sharing (12 tools)

**📊 Data Processing**:
- **files**: File read/write operations, directory management (3 tools)
- **csv**: CSV processing, analysis, filtering (1 tool)
- **transform**: ETL-style data transformation, filtering, sorting (5 tools)

**🌐 Network & Communication**:
- **http**: REST API integration, web scraping (2 tools)

**⚙️ Workflow Control**:
- **execution**: Process coordination, delays, sub-workflows (3 tools)
- **code**: Python/JavaScript code execution (2 tools)

**💡 Tool Selection Examples**:
- **Data Pipeline**: `transform,csv,files,http` (ETL + API + storage)
- **Team Assistant**: `slack,gworkspace,files` (communication + productivity)
- **API Integrator**: `http,transform,files` (external services + processing)
- **Workflow Engine**: `execution,code,http,files` (control flow + custom logic)

**Your Required Tools**: 
[List specific tools from the categories above - see TOOL_REFERENCE.md for detailed capabilities]

## Preventative Rules Agent to Follow

**Safety and Confirmation Rules**: Define when the agent should ask for user confirmation before taking actions.

**Example**: Before sending POST, PUT, or PATCH requests, confirm the request body and parameters with me.

**Your Rules**: 
[Define specific safety rules and confirmation requirements]

## Technical Configuration Requirements

### Environment Variables Needed:
- OPENAI_API_KEY (required)
- SLACK_BOT_TOKEN (if using Slack)
- SLACK_USER_TOKEN (if using Slack search features)
- Additional API keys for other services

### Expected Output Format:
[Specify if you want JSON, plain text, formatted messages, etc.]

### Error Handling Preferences:
[How should the agent handle failures? Retry? Alert user? Graceful degradation?]

## Success Criteria

**How to measure if the agent is working correctly**:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

## Testing Scenarios

**Test Case 1**: [Describe a basic happy path scenario]
**Test Case 2**: [Describe an edge case or error scenario]
**Test Case 3**: [Describe a complex multi-step scenario]

---

**Note for Cursor/AI Development Tools**: This template provides structured requirements for creating LangGraph agents using the Braid toolkit. 

**Tool Selection Process**:
1. Review the user requirements in "Core Tasks and Sequences"
2. Consult [TOOL_REFERENCE.md](./TOOL_REFERENCE.md) to understand available capabilities
3. Select optimal tool combination based on the task requirements
4. Use `braid new <agent-name> --tools <tool-list>` to scaffold the agent structure
5. Customize the agent.py file with the specific logic described above

**Example Command**: `braid new sales-prep-agent --tools gworkspace,slack,http,files`