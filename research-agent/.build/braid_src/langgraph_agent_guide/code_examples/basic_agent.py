"""
A basic ReAct agent example using LangGraph.

This script demonstrates how to build a cyclical graph that can use tools
to answer questions.
"""

import os
from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# Set any necessary API keys here
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls_..."


# 1. Define the tools
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

tools = [multiply, add]

# The ToolNode will execute the tools
tool_node = ToolNode(tools)

# 2. Define the model and bind the tools
# We use a system prompt to give the agent instructions
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. "
            "Use the provided tools to answer the user's question.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

def assistant_node(state: MessagesState):
    """
    The 'assistant' node. This is the LLM that decides what to do next.
    """
    result = llm_with_tools.invoke(state)
    return {"messages": [result]}


# 3. Build the graph
def build_graph():
    """Builds the ReAct agent graph."""
    builder = StateGraph(MessagesState)

    # Add the nodes
    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tool_node)

    # Set the entry point
    builder.add_edge(START, "assistant")

    # Add the conditional edge.
    # This checks the "tool_calls" attribute of the AIMessage.
    # If it exists, it routes to the "tools" node.
    # Otherwise, it routes to END.
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )

    # Add an edge from the tools node back to the assistant node.
    # This closes the loop and allows the agent to continue reasoning.
    builder.add_edge("tools", "assistant")

    # Compile the graph
    return builder.compile()

def main():
    """
    Runs the ReAct agent and prints the conversation history.
    """
    graph = build_graph()
    
    # A list to store the conversation
    conversation: List[BaseMessage] = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        conversation.append(HumanMessage(content=user_input))

        # Invoke the graph
        result = graph.invoke({"messages": conversation})
        
        # The final response is the last message in the list
        final_response = result["messages"][-1]
        
        # Add the final response to the conversation history
        conversation.append(final_response)
        
        print("Assistant:", final_response.content)


if __name__ == "__main__":
    main() 