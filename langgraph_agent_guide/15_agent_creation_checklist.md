# Agent Creation Checklist & Best Practices

This guide provides a checklist of essential steps and best practices to follow when creating a new agent. Following these steps will help you avoid the common bugs and configuration issues we discovered.

## 🚨 CRITICAL: LangSmith Tracing Architecture

- [ ] **Use Proper LangGraph Tool Flow**: Always route tool calls through LangGraph nodes to ensure unified tracing.
  ```python
  # ❌ WRONG - Creates isolated traces
  result = my_tool.invoke({'param': 'value'})
  
  # ✅ CORRECT - Creates unified trace
  # Let LLM make tool calls through model.bind_tools()
  # Execute tools in tool_node with ToolMessage responses
  ```
- [ ] **Create ToolMessage Responses**: Tool execution must create `ToolMessage` objects with matching `tool_call_id`.
- [ ] **Follow Agent → Tools → Agent Pattern**: Build LangGraph with proper routing for unified traces.
- [ ] **Use LangSmith Traced Agent Template**: Reference `/templates/langsmith-traced-agent/` for correct implementation.

**Why This Matters**: Direct `tool.invoke()` calls bypass LangGraph tracing, causing tool calls to appear as isolated events instead of unified workflow traces in LangSmith.

### 1. Environment & Dependencies

- [ ] **Activate Virtual Environment**: Always start by activating the project's virtual environment from the project root.
  ```bash
  source .venv/bin/activate
  ```
- [ ] **Install Dependencies from Root**: All `pip install` commands must be run from the project root (`/braid-ink/braid`).
- [ ] **Install Optional Tool Packages**: If your agent uses tools from `@/contrib` (like Google Workspace or MS365), install the required optional dependencies.
  ```bash
  # Example for Google Workspace tools
  pip install -e ".[gworkspace]"
  ```

### 2. Authentication & Authorization (The Google API Minefield)

The `@/contrib/gworkspace` tools are powerful but require careful setup.

- [ ] **Centralize API Scopes**: When adding a new Google tool, ensure its required permission scope is added to the main `ALL_SCOPES` list in `core/contrib/gworkspace/google_auth.py`. This ensures the user grants all permissions in a single step.
- [ ] **Verify User Permissions**: The Google account used to authorize the agent must have **explicit Editor access** to any Google Sheet the agent needs to modify. The "anyone with the link can edit" setting is not sufficient for API calls.
- [ ] **Delete Token on Scope Change**: If you ever change the `ALL_SCOPES` list in `google_auth.py`, you must delete the `credentials/google_token.json` file to force a re-authentication with the new permissions.

### 3. Agent Configuration & Prompting

This is the most critical part for ensuring your agent behaves as expected.

- [ ] **Load Environment Variables First**: In your agent's main script (e.g., `agent.py`), make sure `load_dotenv()` is called at the **very top of the file**, before any other application-specific imports. This prevents the agent from being configured with `None` values.
  ```python
  # agent.py
  import os
  from dotenv import load_dotenv

  # GOOD: Load env vars before any other code runs.
  load_dotenv()

  from core.contrib.slack.slack_tools import get_slack_tools
  # ... rest of your imports
  ```
- [ ] **Inject Context into the Prompt**: Don't just tell the agent *about* a variable; give it the actual variable. Use f-strings to inject critical information like IDs directly into the system prompt.
  ```python
  # BAD: Agent knows it needs an ID, but doesn't know what it is.
  # "When logging a project, use the spreadsheet ID from the environment variables."

  # GOOD: Agent is given the exact ID to use.
  system_prompt = f"""
  - Google Sheets ID: Use this spreadsheet ID: {os.environ.get('PROJECT_SPREADSHEET_ID')}
  - Google Sheets Range: Append all data to the range 'Sheet1!A1'.
  """
  ```
- [ ] **Use a Direct, Action-Oriented Prompt**: To prevent the agent from getting stuck in conversational loops, give it direct, unambiguous instructions.
  - **Give it a clear workflow**: List the tools it should use in order.
  - **Tell it not to ask for confirmation**: Explicitly instruct it to execute the steps sequentially.
  - **Tell it to be concise**: Instruct it to only provide a final summary after the full workflow is complete.

### 4. Testing & Debugging

- [ ] **Use the Right Script for the Job**:
  - `test_agent.py`: Use for single-shot, non-interactive tests.
  - `agent.py`: Use for interactive, conversational sessions.
- [ ] **Add Logging to Tools**: When a tool is failing, add `logging` to the tool's code (e.g., `gsheets_tools.py`) to see the *exact* inputs the agent is passing to it. This is the fastest way to diagnose configuration vs. logic errors.
  ```python
  # In your tool file
  import logging
  logger = logging.getLogger(__name__)

  @tool(...)
  def my_tool(param1: str, param2: str):
      logger.info(f"Attempting to run my_tool. Param1: '{param1}', Param2: '{param2}'")
      # ... rest of tool logic
  ```
  Then, add `logging.basicConfig(level=logging.INFO)` to your agent's `main()` function to see the output. 