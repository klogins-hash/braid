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

**COMMON ISSUE**: Tool calls appear as isolated events instead of unified workflow traces.

**ROOT CAUSE**: Direct `tool.invoke()` calls bypass LangGraph's tracing system.

**SOLUTION**: Always route tool calls through LangGraph nodes:

```python
# ❌ WRONG - Creates isolated traces
def run_workflow():
    client_info = get_client_information.invoke({'user_id': 'user_123'})
    forecast = calculate_forecast.invoke({'data': client_info})
    
# ✅ CORRECT - Creates unified trace  
def agent_node(state: dict) -> dict:
    """Agent makes tool calls through LangGraph."""
    response = model.invoke(messages)  # Model decides which tools to call
    return {"messages": messages + [response]}

def tool_node(state: dict) -> dict:
    """Execute tools and create ToolMessage responses."""
    last_message = state["messages"][-1]
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        result = tool_map[tool_call['name']].invoke(tool_call['args'])
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call['id']
        ))
    
    return {"messages": state["messages"] + tool_messages}

# Build graph: agent → tools → agent (creates unified trace)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_conditional_edges("agent", lambda s: "tools" if has_tool_calls(s) else END)
builder.add_edge("tools", "agent")
```

**KEY REQUIREMENTS**:
1. Tool calls must be made by the LLM through `model.bind_tools()`
2. Tool responses must be `ToolMessage` objects with matching `tool_call_id`
3. All execution must flow through LangGraph nodes for unified tracing

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