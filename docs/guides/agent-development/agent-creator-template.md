# Agent Requirements Template

**📖 For Claude Code**: Use [CLAUDE_CODE_GUIDE.md](./CLAUDE_CODE_GUIDE.md) for complete codebase understanding and agent development patterns.

## Core Tasks and Sequences of Agent

**Description**: Provide a detailed description of what the agent should do, including the sequence of actions and expected behavior.

**Example**: For every upcoming sales meeting on my Google Calendar, search the prospect in Perplexity and return a concise summary in the #Sales-Prep slack channel.

**Your Requirements**: 
[Replace this with your specific task description]

## Tools & Integrations Required

**🛠️ Available Tools** (See [TOOL_REFERENCE.md](./TOOL_REFERENCE.md) for complete details):

**🏢 External Integrations**:
- **gworkspace**: Gmail, Google Calendar, Google Sheets, Google Drive
- **slack**: Team messaging, notifications, file sharing (12 tools)

**📊 Data Processing**:
- **files**: File read/write operations, directory management
- **csv**: CSV processing, analysis, filtering
- **transform**: ETL-style data transformation, filtering, sorting

**🌐 Network & Communication**:
- **http**: REST API integration, web scraping

**⚙️ Workflow Control**:
- **execution**: Process coordination, delays, sub-workflows
- **code**: Python/JavaScript code execution

**🔌 Direct API Integrations**:
- **notion**: Workspace management (direct API)
- **perplexity**: Real-time search and research (direct API)
- **xero**: Financial accounting and business data (direct API)
- **slack**: Team messaging (enhanced direct integration)
- **gworkspace**: Google services (direct integration)

**💡 Common Patterns** (See CLAUDE_CODE_GUIDE.md for more):
```bash
# Data processing
--tools transform,csv,files,http

# Team automation  
--tools slack,gworkspace,files --integrations notion

# Research & analysis
--tools http,transform,files --integrations perplexity

# Financial analysis
--tools transform,files --integrations xero,notion
```

**Your Required Tools & Integrations**: 
[List specific tools and integrations - see TOOL_REFERENCE.md and CLAUDE_CODE_GUIDE.md]

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

**📖 For Claude Code Development**: This template provides structured requirements for creating LangGraph agents using the Braid toolkit.

**Quick Development Process**:
1. **Start with CLAUDE_CODE_GUIDE.md** - Get familiar with codebase and patterns
2. **Fill out requirements above** - Define tasks, tools, and safety rules
3. **Use agent creation patterns** - See CLAUDE_CODE_GUIDE.md for common scenarios
4. **Create agent**: `braid new <agent-name> --production --tools <tool-list> --integrations <integration-list> --description "description"`
5. **Develop iteratively** - Use `make test` and debugging patterns from guide

**Example Commands**:
```bash
# Basic team assistant
braid new team-bot --production --tools slack,gworkspace,files --description "Team coordination assistant"

# Data processing with notifications
braid new data-processor --production --tools transform,csv,files,slack --description "Process data and notify team"

# Research agent with external services
braid new research-agent --production --tools http,files --integrations perplexity,notion --description "Research and knowledge management"

# Financial analysis agent
braid new financial-agent --production --tools transform,files --integrations xero,notion --description "Financial analysis and reporting"
```

**🔍 See CLAUDE_CODE_GUIDE.md for**:
- Complete codebase architecture
- Development patterns and debugging
- Tool selection strategies
- Complex agent examples
- Memory, RAG, and direct integration patterns