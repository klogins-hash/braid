# Production Best Practices: Observability, Evaluation, and Robustness

Building a functional agent is the first step. Turning it into a reliable, production-ready system requires a focus on observability, evaluation, and robust design. This guide summarizes best practices, many of which are powered by [LangSmith](https://smith.langchain.com/).

## 1. Observability with LangSmith

You cannot improve what you cannot see. Observability is the practice of instrumenting your agent to get detailed insights into its internal operations.

-   **Tracing**: LangSmith provides detailed traces of your agent's execution. Each trace is a hierarchical view of the agent's runs, showing every LLM call, tool execution, and state change. This is invaluable for understanding the agent's decision-making process.
-   **Logging During Development**: For quick, real-time debugging, adding simple `print()` statements at the beginning of each node can be incredibly effective. Logging the current state or the result of a tool call helps verify the data flow within your graph without the overhead of a full tracing setup.
-   **Setup**: Tracing is often as simple as setting environment variables. This "observability-first" approach means you get insights from the very first run.
    -   `LANGCHAIN_TRACING_V2="true"`
    -   `LANGCHAIN_API_KEY="..."`
    -   `LANGCHAIN_PROJECT="..."` (To organize your traces)
-   **Debugging**: When an agent misbehaves, traces allow you to pinpoint the exact cause—was it a bad prompt, a faulty tool, or an unexpected LLM response? LangSmith's Playground feature even lets you re-run and tweak a specific LLM call directly from a trace to debug prompts interactively.

### 🚨 **CRITICAL: LangSmith Tracing Architecture**

**ISSUE**: Tool calls appear as isolated events instead of unified workflow traces.

**SYMPTOM**: In LangSmith dashboard, each tool call shows as separate isolated event rather than part of a waterfall workflow. Impossible to trace end-to-end agent execution.

**ROOT CAUSE**: Direct `tool.invoke()` calls bypass LangGraph's tracing system.

**REAL EXAMPLE FROM PRODUCTION**:
```python
# ❌ WRONG - This creates isolated traces (discovered in financial forecasting agent)
def run_workflow():
    # Each of these appears as separate, isolated event in LangSmith
    client_info = get_client_information.invoke({'user_id': 'user_123'})
    xero_data = get_live_xero_data.invoke({'user_id': 'user_123'}) 
    market_research = get_market_research.invoke({'industry': 'tech'})
    forecast = calculate_forecast.invoke({'data': xero_data})
    # No way to see these as connected workflow
```

**✅ SOLUTION**: Proper agent → tools → agent flow with unified tracing:

```python
def create_traced_agent():
    """Create agent with proper LangSmith tracing architecture."""
    tools = [get_client_information, get_live_xero_data, get_market_research, calculate_forecast]
    tool_map = {tool.name: tool for tool in tools}
    
    model = ChatOpenAI(model="gpt-4o", temperature=0.1)
    model = model.bind_tools(tools)  # Crucial: bind tools to model
    
    def agent_node(state: dict) -> dict:
        """Agent node that makes tool calls through LangGraph."""
        user_id = state.get("user_id", "user_123")
        step = state.get("step", 1)
        messages = state.get("messages", [])
        
        if step == 1:
            prompt = f"Get client information for user {user_id} using get_client_information tool."
        elif step == 2:
            prompt = f"Get live Xero data using get_live_xero_data tool."
        # ... more steps
        
        new_message = HumanMessage(content=prompt)
        updated_messages = messages + [new_message]
        
        # LLM decides which tools to call - this creates unified trace
        response = model.invoke(updated_messages)
        updated_messages.append(response)
        
        return {
            **state,
            "messages": updated_messages,
            "step": step
        }
    
    def tool_node(state: dict) -> dict:
        """Execute tools and create ToolMessage responses."""
        messages = state.get("messages", [])
        step = state.get("step", 1)
        
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return state
        
        # Execute each tool call and create ToolMessage
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_call_id = tool_call['id']
            
            print(f"🔧 Executing {tool_name} with args: {tool_args}")
            
            try:
                # Execute the tool
                result = tool_map[tool_name].invoke(tool_args)
                
                # Create ToolMessage with matching tool_call_id (CRITICAL)
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id
                )
                tool_messages.append(tool_message)
                
                print(f"✅ {tool_name} completed successfully")
                
            except Exception as e:
                print(f"❌ Error executing {tool_name}: {e}")
                error_message = ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call_id
                )
                tool_messages.append(error_message)
        
        # Add tool messages to conversation
        updated_messages = messages + tool_messages
        
        # Move to next step after tool execution
        next_step = step + 1 if step < 5 else step
        
        return {
            **state,
            "messages": updated_messages,
            "step": next_step
        }
    
    def should_continue(state: dict) -> str:
        """Router function for proper trace flow."""
        messages = state.get("messages", [])
        completed = state.get("completed", False)
        
        if completed:
            return END
        
        # Check if last message has tool calls
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
        
        # Continue to agent for next step
        return "agent"
    
    # Build the LangGraph with proper routing
    builder = StateGraph(dict)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    
    # Add edges for unified tracing
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_conditional_edges("tools", should_continue)
    
    return builder.compile()

# Execute with proper configuration
agent = create_traced_agent()
result = agent.invoke(
    {"messages": [HumanMessage(content="Run financial forecast")], "user_id": "user_123"},
    config={"recursion_limit": 50}
)
```

**CRITICAL REQUIREMENTS FOR UNIFIED TRACING**:
1. **Bind tools to model**: `model = model.bind_tools(tools)` 
2. **ToolMessage responses**: Must include exact `tool_call_id` from tool call
3. **Model decides tools**: Let LLM choose tools, don't call `tool.invoke()` directly
4. **Proper routing**: Use conditional edges for agent → tools → agent flow
5. **State management**: Pass all needed data through graph state

**VERIFICATION**: In LangSmith dashboard, you should see:
- One unified workflow run (not isolated events)
- Tool calls nested under LLM calls in waterfall view
- Complete trace showing agent → tools → agent flow
- All tool executions connected to parent workflow

**THIS PATTERN PREVENTS**: Isolated tool calls, broken traces, inability to debug workflows

## 2. Rigorous Evaluation

To systematically improve your agent, you must evaluate it on a consistent set of examples.

-   **Datasets**: Create datasets of test cases in LangSmith. These can be curated from interesting or problematic traces from your logs, or uploaded manually. A good dataset is the cornerstone of reliable evaluation.
-   **Evaluators**: An evaluator is a function that scores your agent's performance. LangSmith supports several types:
    -   **Custom Code**: Write your own logic to check the output.
    -   **LLM-as-Judge**: Use a separate LLM with a carefully crafted prompt to provide a qualitative score on aspects like "helpfulness" or "correctness."
    -   **Heuristics**: Simple checks, like "is the output valid JSON?"
-   **Experiments**: Run your agent against a dataset and track the results as an "Experiment." This allows you to compare different versions of your agent and quantitatively measure whether your changes are improvements or regressions.

## 3. Designing for Robustness

Production agents must be resilient to failures.

-   **Error Handling in Tools**: Your custom tools should have robust error handling. Use a `ToolException` to signal a failure condition back to the agent. The agent can then use this information to retry, or try a different approach.
-   **Data Type Mismatches**: Be especially careful with data returned from external libraries like `pandas` or `yfinance`. These libraries often return their own data types (e.g., `numpy.int64` instead of `int`). These custom types may not work with standard Python functions like string formatters. Always explicitly cast values to standard Python types (e.g., `int()`, `float()`, `str()`) before using them in downstream operations.
-   **LLM Fallbacks**: LLM calls can fail due to API errors or rate limits. Use LangChain's `Runnable.with_retry()` for transient issues, or `RunnableWithFallbacks` to define a backup model (e.g., a cheaper or faster one) if the primary LLM fails.
-   **Precise Tool Definitions**: The LLM's ability to use tools correctly depends heavily on the tool's `name` and `description`. Be clear and precise. Use the `args_schema` to define the expected inputs, which helps the model generate correct arguments.

By embracing these practices—observing your agent's behavior, evaluating its performance systematically, and designing it to be robust—you can confidently move your LangGraph agents from prototype to production. 