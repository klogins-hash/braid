# Core LangGraph Concepts

A LangGraph is constructed from three fundamental components: State, Nodes, and Edges.

## 1. State

The **State** is a data structure that is passed between all nodes in the graph. It represents the current "state" of your application at any given point.

-   It is typically defined as a `TypedDict` from Python's `typing` module.
-   Each key in the `TypedDict` represents a piece of data that can be read from or written to by the nodes.
-   The state is initialized when you first invoke the graph and is updated by each node as the graph executes.

### Example:
```python
from typing_extensions import TypedDict

class MyState(TypedDict):
    # The 'messages' key will hold the list of messages in our conversation
    messages: list
```

## 2. Nodes

**Nodes** are the workhorses of the graph. They are Python functions or any other [LangChain Runnable](https://python.langchain.com/v0.2/docs/concepts/#langchain-expression-language-lcel) that perform the primary logic of your application.

-   Each node receives the current `State` as its first argument.
-   It performs some computation (e.g., calling an LLM, executing a tool, etc.).
-   It returns a dictionary where the keys match keys in the `State` object. The values in this dictionary will update the corresponding values in the state. By default, the new value *overrides* the old one.

### Example:
```python
def my_node(state: MyState):
    print("This is my first node.")
    # This will update the 'messages' key in the state
    return {"messages": ["Hello from my_node!"]}
```

## 3. Edges

**Edges** connect the nodes, defining the flow of control. They determine which node to execute next.

There are two main types of edges:

-   **Normal Edges:** These are unconditional. They always direct the flow from one node to another. You define them by specifying the source node and the destination node.
-   **Conditional Edges:** These allow for dynamic routing. A conditional edge is a function that receives the current `State` and returns the string name of the next node to visit. This allows you to create branches and loops in your graph based on the current state.

### Example:
```python
from typing import Literal

def should_i_continue(state: MyState) -> Literal["continue_node", "__end__"]:
    if len(state['messages']) > 5:
        # If we have more than 5 messages, end the graph
        return "__end__"
    else:
        # Otherwise, go to the 'continue_node'
        return "continue_node"
```

## Graph Construction

You build your graph using the `StateGraph` class.

1.  **Instantiate:** Create an instance of `StateGraph`, passing your `State` definition.
2.  **Add Nodes:** Add your nodes using `builder.add_node("node_name", node_function)`.
3.  **Set Entry Point:** Define the starting node of your graph using `builder.add_edge(START, "entry_node_name")`.
4.  **Add Edges:** Add normal edges (`builder.add_edge(...)`) and conditional edges (`builder.add_conditional_edges(...)`).
5.  **Compile:** Compile the graph into a runnable object using `graph = builder.compile()`.

### Example:
```python
from langgraph.graph import StateGraph, START

# (State and node definitions from above)

builder = StateGraph(MyState)
builder.add_node("entry_node", my_node)
builder.add_node("continue_node", ...) # Another node
builder.add_edge(START, "entry_node")
builder.add_conditional_edges(
    "entry_node",
    should_i_continue,
    {
        "continue_node": "continue_node",
        "__end__": "__end__"
    }
)
# ... other edges ...

graph = builder.compile()

# You can now invoke the graph:
# graph.invoke({"messages": ["Initial message"]})
```

This covers the fundamental components. The next section will show how to combine these to build a functional agent. 