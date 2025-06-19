# Advanced Graph Patterns

For complex tasks, a single, monolithic graph can become difficult to manage. LangGraph supports several patterns for creating more modular, scalable, and efficient agents.

## 1. Sub-graphs

You can embed one graph within another as a node. This is a powerful way to create modular and reusable components.

For example, you could have a main "Orchestrator" graph that routes tasks to specialized "Worker" sub-graphs. One sub-graph might be an expert at web search, while another is an expert at data analysis.

```python
# Create a worker graph
worker_graph = build_worker_graph()

# Create the main orchestrator graph
builder = StateGraph(OrchestratorState)
# ... add nodes for the orchestrator ...

# Add the worker graph as a node in the orchestrator
builder.add_node("web_search_worker", worker_graph)

# Now you can create edges to and from the worker node
builder.add_edge("start_node", "web_search_worker")
builder.add_edge("web_search_worker", "end_node")

orchestrator = builder.compile()
```

This allows you to encapsulate complexity and build agents that are easier to reason about and maintain.

## 2. Parallel Execution

By default, LangGraph executes one node at a time. However, if you have multiple tasks that can be performed independently, you can run them in parallel to speed up your agent.

You can achieve this by having a node that returns a list of `Runnable` objects. LangGraph will execute these runnables in parallel.

```python
from langchain_core.runnables import RunnableLambda

def parallel_node(state):
    # This node will execute two functions in parallel
    return [
        RunnableLambda(some_long_running_task).with_config(run_name="task_1"),
        RunnableLambda(another_long_running_task).with_config(run_name="task_2"),
    ]

# The results will be collected and passed to the next node.
```

This is particularly useful for tasks like calling multiple APIs or performing multiple searches at the same time.

## 3. Map-Reduce

Map-reduce is a common pattern for processing large amounts of data.

-   **Map**: In the "map" step, you apply the same operation to many pieces of data in parallel. For example, you could pass a list of documents to an LLM to summarize each one.
-   **Reduce**: In the "reduce" step, you take the outputs of the "map" step and combine them into a single result. For example, you could take all the individual summaries and create a final, consolidated summary.

LangGraph's support for parallel execution makes the "map" step straightforward. The "reduce" step can then be implemented in a subsequent node that aggregates the results.

This pattern is essential for building agents that can perform research, analyze large datasets, or process information from multiple sources. 