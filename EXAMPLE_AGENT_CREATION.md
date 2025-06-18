# Example: Using the Documentation System for Agent Creation

This example demonstrates how the new documentation system guides optimal tool selection.

## User Request Example

**User fills out agent-creator-template.md with:**

```markdown
## Core Tasks and Sequences of Agent

**Your Requirements**: 
I need an agent that monitors our customer support tickets from our API, 
analyzes the sentiment and categorizes them, then posts daily summaries 
to our #support-team Slack channel and updates a Google Sheet with trends.

## Tools Agent Should Use

**Your Required Tools**: 
[User leaves this blank - needs guidance]
```

## AI Assistant Analysis Process

### Step 1: Consult TOOL_REFERENCE.md
I review the available tools and their capabilities:

- **API integration**: Need `http` for fetching ticket data
- **Data processing**: Need `transform` for sentiment analysis and categorization
- **Communication**: Need `slack` for team notifications
- **Business integration**: Need `gworkspace` for Google Sheets
- **File operations**: Need `files` for storing data and logs
- **Scheduling**: Need `execution` for daily automation

### Step 2: Use TOOL_SELECTION_GUIDE.md
Following the decision tree:

**Problem Category**: Complex Automation (multi-step, scheduled, business integration)

**Pattern Match**: "API data → processed → shared" = Communication Hub pattern

**Recommended Combination**: `http,transform,slack,gworkspace,files,execution`

### Step 3: Generate Recommendation

```markdown
## Recommended Tools: `http,transform,slack,gworkspace,files,execution`

**Rationale**:
- `http`: Fetch support tickets from your API
- `transform`: Analyze sentiment, categorize tickets, compute daily summaries  
- `slack`: Post daily summaries to #support-team channel
- `gworkspace`: Update Google Sheets with trend data
- `files`: Store processed data and maintain logs
- `execution`: Handle daily scheduling and workflow coordination

**Command**: `braid new support-analyzer --tools http,transform,slack,gworkspace,files,execution`
```

### Step 4: User Gets Complete Agent

The agent is created with all necessary tools and the user can see:

```
support-analyzer/
├── agent.py                    # Main LangGraph agent
├── requirements.txt           # All dependencies included
├── .env.example              # Required environment variables
└── tools/
    ├── http_tools.py          # API integration
    ├── transform_tools.py     # Data processing
    ├── slack_tools.py         # Team notifications
    ├── gworkspace_tools.py    # Google Sheets integration
    ├── files_tools.py         # File operations
    └── execution_tools.py     # Workflow control
```

## Benefits Demonstrated

### ✅ Complete Tool Coverage
- Every aspect of the user's requirement is addressed
- No missing capabilities or unnecessary tools
- Optimal combination for the specific use case

### ✅ Clear Decision Logic
- Transparent reasoning for tool selection
- References to documentation for validation
- Pattern-based recommendations

### ✅ Actionable Output
- Specific CLI command provided
- Ready-to-customize agent structure
- All dependencies automatically included

## Before vs After Comparison

### Before Documentation System
```
User: "I need to process API data and send to Slack"
AI: "You might need some API and communication tools"
User: "Which ones specifically?"
AI: "I'm not sure what's available..."
```

### After Documentation System
```
User: "I need to process API data and send to Slack"
AI: "Based on TOOL_REFERENCE.md, you need:
     - http: For API integration
     - transform: For data processing  
     - slack: For team communication
     - files: For data storage
     
     Command: braid new api-processor --tools http,transform,slack,files"
```

The documentation system enables precise, confident tool recommendations that match user needs perfectly.