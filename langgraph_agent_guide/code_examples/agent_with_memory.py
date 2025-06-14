"""
An example of a ReAct agent with memory using LangGraph.

This script demonstrates how to add persistence to a graph, allowing it
to have multi-turn conversations.
"""

import os

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

# Import the base agent graph builder
from basic_agent import build_graph as build_basic_agent_graph

# Set any necessary API keys here
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls_..."

def build_graph_with_memory():
    """
    Builds the ReAct agent graph and adds a checkpointer for memory.
    """
    # 1. Build the base graph
    builder = build_basic_agent_graph()

    # 2. Add a checkpointer
    # The MemorySaver is a simple in-memory checkpointer.
    # We pass it directly to the .compile() method for compatibility.
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


def main():
    """
    Runs a conversational agent with memory.
    """
    graph = build_graph_with_memory()

    # A unique thread_id for the conversation
    config = {"configurable": {"thread_id": "user-123"}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # The input to the graph is a dictionary with a "messages" key.
        input_messages = {"messages": [HumanMessage(content=user_input)]}

        # Invoke the graph
        result = graph.invoke(input_messages, config=config)

        # The final response is the last AI message in the list
        final_response = result["messages"][-1]

        print("Assistant:", final_response.content)


if __name__ == "__main__":
    main() 