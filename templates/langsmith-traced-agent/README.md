# LangSmith Traced Agent Template

This template demonstrates the **CORRECT** way to build LangGraph agents that show unified workflow traces in LangSmith, avoiding the common issue where tool calls appear as isolated events.

## 🚨 Common LangSmith Tracing Issue

**PROBLEM**: Tool calls appear as isolated events instead of unified workflow traces.

**ROOT CAUSE**: Direct `tool.invoke()` calls bypass LangGraph's tracing system.

## ✅ Solution

This template ensures proper LangSmith tracing by:

1. **Routing all tool calls through LangGraph nodes**
2. **Creating proper ToolMessage responses with matching tool_call_id**
3. **Maintaining agent → tools → agent flow**

## Architecture

```
START → agent_node → tool_node → agent_node → ... → END
             ↓           ↓           ↓
         LLM decides   Executes    Next step
         tools to      tools and   decision
         call          creates
                      ToolMessages
```

## Key Components

### 1. Agent Node
- Contains the LLM that decides which tools to call
- Uses `model.bind_tools()` to make tools available
- Creates workflow-specific prompts for each step

### 2. Tool Node
- Executes the actual tools
- Creates `ToolMessage` objects with matching `tool_call_id`
- Handles errors gracefully

### 3. Router Function
- Determines if we should continue to tools or next step
- Creates the unified trace flow

## Usage

1. **Customize the tools**:
```python
tools = [
    your_custom_tool_1,
    your_custom_tool_2,
]
```

2. **Customize the workflow steps**:
```python
if step == 1:
    prompt = "Your step 1 prompt..."
elif step == 2:
    prompt = "Your step 2 prompt..."
```

3. **Set up LangSmith**:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=your_project_name
```

4. **Run the agent**:
```python
python agent_template.py
```

## What You'll See in LangSmith

✅ **One unified run** with clear step progression  
✅ **Waterfall view** of agent → tools → agent flow  
✅ **All tool calls** as part of the same trace  
✅ **Clear conversation flow** with proper message types  

## Key Requirements

1. **Tool calls must be made by the LLM** through `model.bind_tools()`
2. **Tool responses must be ToolMessage objects** with matching `tool_call_id`
3. **All execution must flow through LangGraph nodes** for unified tracing

## Anti-Patterns to Avoid

❌ **Direct tool invocation**:
```python
# This creates isolated traces
result = my_tool.invoke({"arg": "value"})
```

❌ **Missing ToolMessage responses**:
```python
# This causes "tool_calls must be followed by tool messages" error
response = model.invoke(messages_with_tool_calls)
# Missing: ToolMessage creation
```

❌ **Bypassing LangGraph**:
```python
# This doesn't show in unified trace
def run_workflow():
    step1 = tool1.invoke(args)
    step2 = tool2.invoke(step1)
```

## Benefits

- **Perfect observability**: See exactly how your agent makes decisions
- **Easy debugging**: Unified traces show the complete workflow
- **Production ready**: Proper error handling and state management
- **Scalable**: Template works for any number of tools and steps

Use this template as the foundation for all LangGraph agents to ensure proper LangSmith tracing from day one!