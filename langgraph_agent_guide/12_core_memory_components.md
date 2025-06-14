# 12. Core Memory Components

This document outlines the production-ready, persistent memory system built into this repository. All new agents should use these core components to ensure consistency and robustness.

Our memory is a two-layer system built on a single SQLite database (`langgraph.db`), aligning with the patterns from the LangGraph guides.

---

### 1. Task Memory (Persistent Conversation History)

This layer remembers the back-and-forth of a single conversation, even if the application restarts.

-   **Component:** `core/memory.py`
-   **Technology:** `langgraph.checkpoint.sqlite.SqliteSaver`
-   **How it Works:** The `get_checkpointer()` function returns a checkpointer connected to the main `langgraph.db` file. LangGraph uses this to automatically save the agent's state after every step of a conversation.

#### How to Use

In your agent's graph-building file, compile your graph with the checkpointer from our core factory. This makes your agent's short-term memory persistent by default.

```python
# In your agent's graph.py
from langgraph.graph import StateGraph
from core.memory import get_checkpointer

# ... define your state and nodes ...
builder = StateGraph(AgentState)
# ... add nodes and edges ...

# Compile with the persistent checkpointer
graph = builder.compile(checkpointer=get_checkpointer())
```

---

### 2. Long-Term Memory (Persistent User Profiles)

This layer stores and recalls information about a user across many different conversations.

-   **Component:** `core/user_profile.py`
-   **Technology:** A custom tool-based API over a `user_profiles` table in the same `langgraph.db` SQLite database.
-   **How it Works:** We provide two tools that the agent's LLM can decide to use:
    -   `save_user_preferences(user_id: str, preferences: dict)`: Saves or updates a user's profile.
    -   `get_user_preferences(user_id: str) -> dict`: Retrieves a user's profile.

#### How to Use

1.  **Make Agent State Aware:** Your agent's `AgentState` `TypedDict` must include a `user_id: str` field so the agent knows *who* it's talking to.

    ```python
    # In your agent's graph.py
    class AgentState(TypedDict):
        messages: Annotated[list, add_messages]
        user_id: str # Crucial for identifying the user
        # ... other state fields ...
    ```

2.  **Equip the Agent with Tools:** Add the user profile tools to the list of tools your agent can use.

    ```python
    # In your agent's graph.py
    from core.user_profile import get_user_preferences, save_user_preferences
    from .my_other_tools import my_tool

    tools = [my_tool, get_user_preferences, save_user_preferences]
    tool_node = ToolNode(tools)
    ```

3.  **Guide the Agent:** Use a `SystemMessage` in your primary agent node to instruct the LLM on *how* and *when* to use these tools. The agent must be told to get the `user_id` from its state.

    ```python
    # In your agent's graph.py
    system_message = SystemMessage(
        content="You are a helpful assistant. The user_id for the current user is available in the state. "
                "When a user asks you to remember something, use the `save_user_preferences` tool. "
                "Do not ask the user for their ID."
    )
    # ... prepend this to your model call ...
    ```

By following these steps, any new agent can be instantly equipped with a robust, production-ready, and persistent memory system. 