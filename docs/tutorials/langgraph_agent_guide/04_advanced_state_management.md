# Advanced State Management

As your agents become more complex, you may need more sophisticated ways to manage the graph's state. This section covers advanced techniques for state management.

## 1. Custom Reducers

While the `add_messages` reducer is useful, you sometimes need custom logic for updating state. A reducer is a function that takes the current value of a state key and the new value, and returns the updated value.

For example, you could write a reducer that keeps a running count of something in the state.

```python
from typing import Annotated
from typing_extensions import TypedDict

def update_count(current_count: int, new_count_update: int) -> int:
    """A reducer to add to a running total."""
    return current_count + new_count_update

class AgentState(TypedDict):
    # Annotate the 'count' key with our custom reducer
    count: Annotated[int, update_count]
    messages: Annotated[list, add_messages]

# A node can now return a value for 'count', and it will be added
# to the existing value.
def my_node(state):
    return {"count": 1} # This will increment the total count by 1
```

## 2. Managing Message History

In long-running conversations, the message history can grow very large, exceeding the context window of the LLM. It's important to have a strategy for managing this.

A common technique is to trim the message history before passing it to the LLM. You can do this within your assistant node.

```python
from langgraph.graph.message import trim_messages

def assistant_node(state: AgentState):
    # Trim the messages to the last 10, keeping the system message.
    trimmed_messages = trim_messages(
        state['messages'],
        max_len=10,
        strategy="last",
        system_message=state['messages'][0] if state['messages'][0].type == "system" else None
    )
    
    result = llm_with_tools.invoke(trimmed_messages)
    return {"messages": [result]}
```

Other strategies include summarizing the conversation periodically and storing the summary in the state.

## 3. Multiple State Schemas

In very complex agents, you might have different parts of the agent that operate on different pieces of state. LangGraph allows you to use multiple state schemas.

You can define different `TypedDict` schemas for different parts of your graph. The overall state of the graph will be a union of these schemas. When a node is executed, it will only receive the keys that are relevant to its specific schema.

This can help in creating modular and maintainable agents, where different teams can work on different parts of the agent without interfering with each other's state.

## 4. External Memory

For very long-term memory (e.g., remembering user preferences across many conversations), storing everything in the graph state is not practical.

Instead, you can use an external memory store (like a vector database or a key-value store). The agent can then use tools to explicitly read from and write to this external memory.

-   **Write to Memory**: Create a tool that takes information and saves it to the database.
-   **Read from Memory**: Create a tool that takes a query and retrieves relevant information from the database.

The agent can then decide when to use these tools to recall past information or save new information for future use. 