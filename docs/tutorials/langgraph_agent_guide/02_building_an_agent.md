# Building an Agent with Tools

The core concepts of State, Nodes, and Edges can be combined to create a "ReAct" agent. ReAct stands for Reason and Act, a common agent architecture where the agent can:

1.  **Reason:** Use an LLM to decide on the next course of action.
2.  **Act:** Execute a tool to get more information or perform a task.
3.  **Observe:** Take the result of the tool and feed it back to the LLM to continue the process.

This creates a loop that allows the agent to perform multi-step tasks.

> **A Note on Observability**
> This ReAct loop can sometimes be difficult to debug. Tools like [LangSmith](https://smith.langchain.com/) are essential for visualizing the agent's step-by-step execution. Each step of the loop—the LLM's reasoning, the tool call, and the observation—is captured as a "trace," allowing you to see exactly what the agent is doing. This is covered in more detail in `08_production_best_practices.md`.

## Key Components for an Agent

### 1. Messages as State and Reducers

For a conversational agent, the state should hold the history of the conversation. Instead of overwriting the state at each step, we want to *append* new messages to the history.

-   **`MessagesState`**: LangGraph provides a pre-built `MessagesState` which is a `TypedDict` with a `messages` key.
-   **`add_messages` Reducer**: `MessagesState` automatically uses the `add_messages` reducer. A reducer is a function that specifies how a state key should be updated. `add_messages` appends new messages to the existing list instead of overwriting it.

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages, AnyMessage

# This is how you would define it manually, but MessagesState does this for you.
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

### 2. Tools and Tool Binding

Tools are functions that your agent can call to interact with the outside world (e.g., search the web, access a database, call an API).

-   **Define Tools**: Tools can be simple Python functions. It's crucial to include a clear docstring, as the LLM uses this to decide when to call the tool.
-   **Bind to LLM**: You "bind" your tools to an LLM using the `.bind_tools()` method. This tells the LLM about the available tools and their schemas.

```python
from langchain_openai import ChatOpenAI

# This is our tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([multiply])
```

When the LLM is invoked with a prompt that requires the tool (e.g., "What is 5 times 4?"), it will output an `AIMessage` containing a `tool_calls` attribute, rather than a natural language response.

### 3. The Agent Graph Structure (The ReAct Loop)

A typical agent graph has a cyclical structure:

1.  **Assistant Node**: This node contains the LLM with bound tools. It takes the current message history and "reasons" about what to do next. It either responds directly to the user or decides to call a tool.
2.  **Conditional Edge**: After the assistant node, a conditional edge checks the `AIMessage` from the LLM.
    -   If the message contains `tool_calls`, it routes to the `ToolNode`.
    -   If not, it means the agent is ready to respond to the user, and it routes to `END`.
3.  **Tool Node**: This node executes the tool(s) called by the LLM.
    -   `ToolNode` is a pre-built LangGraph node that takes a list of tools. It automatically executes the correct tool based on the `tool_calls` from the assistant and returns a `ToolMessage` with the result.
4.  **Edge back to Assistant**: After the `ToolNode` runs, an edge connects back to the `Assistant` node. This "observe" step adds the `ToolMessage` to the message history, closing the loop and allowing the LLM to reason about the tool's output.

This structure looks like this:

`START` -> `assistant` -> (conditional) -> `tools` -> `assistant`
                      |
                      v
                     `END`

This loop continues until the LLM decides it has a final answer and responds directly, breaking the loop.

> **A Note on `invoke()` and Input Types**
> When you create a chain with `prompt | llm`, the `.invoke()` method expects an input that directly matches the variables in your prompt. If your prompt has a single `{messages}` variable, you should pass the list of messages directly (e.g., `chain.invoke(list_of_messages)`). Passing a dictionary like `chain.invoke({"messages": list_of_messages})` can sometimes lead to a `ValueError`. Being explicit is always safer. 