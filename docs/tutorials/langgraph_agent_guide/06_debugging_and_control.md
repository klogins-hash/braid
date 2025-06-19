# Debugging and Control Flow

LangGraph provides powerful features for debugging your agents and controlling their execution, including adding breakpoints and allowing for human-in-the-loop feedback. These capabilities are enabled by the checkpointer.

## 1. Breakpoints

You can pause a graph's execution at any node by setting a breakpoint. This is incredibly useful for debugging, as it allows you to inspect the state of the graph at a specific point.

To set a breakpoint, you pass a list of node names to the `interrupt_before` argument when compiling the graph.

```python
# The graph will pause before executing the 'tools' node.
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]
)

# When you invoke the graph, it will run until it's about to execute
# the 'tools' node, then save its state and exit.
result = graph.invoke(input_messages, config=config)

# You can now inspect the state of the graph
current_state = graph.get_state(config)
print(current_state)
```

## 2. Time Travel and Resuming Execution

Once a graph is interrupted at a breakpoint, you can "time travel" to inspect the state at any previous step in the conversation using `graph.get_state_history(config)`.

After inspecting the state, you can make changes and then resume execution. To resume, you simply call `.invoke()` again with the same config. The graph will pick up where it left off.

## 3. Human-in-the-Loop

The ability to interrupt, inspect, and resume execution is the foundation for human-in-the-loop workflows. You can build applications where an agent performs some steps, pauses for human review or input, and then continues.

To get input from a human, you can update the state of the graph with the human's feedback before resuming.

```python
# After the graph is interrupted...
current_state = graph.get_state(config)

# Get feedback from the human
human_feedback = input("Please provide your feedback: ")

# Update the state with the feedback
# This might be a ToolMessage, a HumanMessage, or any other state update
feedback_message = HumanMessage(content=human_feedback)
graph.update_state(config, {"messages": [feedback_message]})

# Resume execution
resumed_result = graph.invoke(None, config=config)
```

This allows you to build powerful, collaborative agents where humans and AI can work together to solve problems. It's also an excellent way to debug and steer your agent's behavior during development. 