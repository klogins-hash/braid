"""
A simple LangGraph example demonstrating core concepts.

This script builds a graph with three nodes and a conditional edge.
"""

import os
import random
from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START
from IPython.display import Image, display

# Set any necessary API keys here
# os.environ["OPENAI_API_KEY"] = "sk-..."

# 1. Define the state
class State(TypedDict):
    """The state of our graph."""
    graph_state: str

# 2. Define the nodes
def node_1(state: State):
    """The first node in our graph."""
    print("---Node 1---")
    # The return value is a dictionary that updates the state
    return {"graph_state": state['graph_state'] + " I am"}

def node_2(state: State):
    """The second node in our graph."""
    print("---Node 2---")
    return {"graph_state": state['graph_state'] + " happy!"}

def node_3(state: State):
    """The third node in our graph."""
    print("---Node 3---")
    return {"graph_state": state['graph_state'] + " sad!"}

# 3. Define the conditional edge
def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    """
    A conditional edge that decides the next node to visit based on a random choice.
    """
    # Here, we make a random choice, but in a real agent, this could
    # be based on the output of an LLM or a tool.
    if random.random() < 0.5:
        return "node_2"
    else:
        return "node_3"

# 4. Build the graph
def build_graph():
    """Builds the graph using StateGraph."""
    builder = StateGraph(State)

    # Add the nodes
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)

    # Set the entry point
    builder.add_edge(START, "node_1")

    # Add the conditional edge
    # The first argument is the source node
    # The second argument is the conditional function
    # The third argument is a dictionary mapping the output of the
    # conditional function to the destination nodes.
    builder.add_conditional_edges(
        "node_1",
        decide_mood,
        {
            "node_2": "node_2",
            "node_3": "node_3",
        },
    )

    # Add normal edges to the end
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)

    # Compile the graph
    return builder.compile()

def main():
    """
    Runs the simple graph and prints the final state.
    """
    graph = build_graph()

    # You can visualize the graph with the following code (requires graphviz)
    # try:
    #     display(Image(graph.get_graph().draw_mermaid_png()))
    # except Exception:
    #     # This requires some extra dependencies and is not essential
    #     pass

    # Invoke the graph with an initial state
    initial_input = {"graph_state": "Hi, this is Lance."}
    final_state = graph.invoke(initial_input)

    # Print the final state
    print("\n---Final State---")
    print(final_state)

if __name__ == "__main__":
    main() 