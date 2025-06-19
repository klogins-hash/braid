# Adding Memory to an Agent

By default, the state of a LangGraph is **transient**. This means that the state only exists for a single run (`.invoke()` call). If you want your agent to remember past interactions and have a continuous conversation, you need to add **persistence**.

LangGraph's persistence layer works by using a **Checkpointer**. A checkpointer automatically saves the state of the graph after each step. When you invoke the graph again with the same identifier, it will load the saved state and continue the conversation from where it left off.

## How Checkpointers Work

1.  **Compile with a Checkpointer**: You enable persistence by passing a checkpointer instance to the `.compile()` method of your graph.
2.  **Provide a `thread_id`**: When you invoke the graph, you must provide a `thread_id` in the `configurable` dictionary of the config. This `thread_id` acts as a unique identifier for a specific conversation or user session.
3.  **State is Saved**: At each step of the graph's execution, the checkpointer saves the current state to its backend (e.g., in-memory, SQLite, Redis, etc.), associated with the `thread_id`.
4.  **State is Loaded**: On subsequent invocations with the same `thread_id`, the checkpointer first loads the last saved state for that thread. The new input is added to that state, and the graph continues execution.

## Using `MemorySaver`

The simplest checkpointer is the `MemorySaver`. It stores the conversation history in memory. While not suitable for production (as it's not persistent across application restarts), it's perfect for development and understanding the concept.

The most compatible way to add a checkpointer is to pass it directly to the `.compile()` method of your graph builder.

### Example:

```python
from langgraph.checkpoint.memory import MemorySaver

# ... (your graph builder code from the previous section) ...

# Instantiate an in-memory checkpointer
memory = MemorySaver()

# Pass the checkpointer directly to the compile method
graph_with_memory = builder.compile(checkpointer=memory)
```

## Invoking a Graph with Memory

To use the memory, you invoke the graph with a `config` object that specifies the `thread_id`.

> **Observing Memory with LangSmith**
> When using a checkpointer, LangSmith tracing becomes even more powerful. It allows you to inspect the full state of the graph at each step of a conversation, clearly showing how memory is being loaded and updated across multiple invocations within the same thread.

```python
# A unique ID for this conversation
config = {"configurable": {"thread_id": "user_123"}}

# First turn
initial_input = {"messages": [HumanMessage(content="What is 5 + 5?")]}
result = graph_with_memory.invoke(initial_input, config=config)
# The agent responds: "The answer is 10."

# Second turn
# The agent will now remember the previous turn because we are using the same thread_id.
follow_up_input = {"messages": [HumanMessage(content="What was my last question?")]}
result = graph_with_memory.invoke(follow_up_input, config=config)
# The agent can now answer: "Your last question was 'What is 5 + 5?'"
```

By using a checkpointer and a `thread_id`, your agent can maintain conversational history, making it far more useful and interactive. For production use cases, you can swap `MemorySaver` with more robust backends like `SqliteSaver` or a custom checkpointer for databases like Redis or Postgres. 