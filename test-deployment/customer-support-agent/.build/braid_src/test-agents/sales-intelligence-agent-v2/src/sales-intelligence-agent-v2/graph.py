"""Main graph definition for the sales-intelligence-agent-v2 agent."""

import logging
from typing import Dict, List

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from sales-intelligence-agent-v2.configuration import Configuration
from sales-intelligence-agent-v2.prompts import get_system_prompt
from sales-intelligence-agent-v2.state import AgentState
from sales-intelligence-agent-v2.tools import get_tools
from sales-intelligence-agent-v2.utils import load_chat_model


def create_agent_graph():
    """Create and return the agent graph."""
    config = Configuration()
    tools = get_tools()
    
    # Initialize model
    model = load_chat_model(config.model, config.temperature)
    if tools:
        model = model.bind_tools(tools)
    
    # Create tool node
    tool_node = ToolNode(tools) if tools else None
    
    # Define agent node
    def agent_node(state: AgentState) -> Dict[str, List[AnyMessage]]:
        """The main agent node that processes messages."""
        # Create prompt with system message
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Format and invoke
        messages = prompt.format_messages(messages=state["messages"])
        response = model.invoke(messages)
        
        return {"messages": [response]}
    
    # Build graph
    builder = StateGraph(AgentState)
    builder.add_node("assistant", agent_node)
    
    if tool_node:
        builder.add_node("tools", tool_node)
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
    else:
        builder.add_edge(START, "assistant")
    
    return builder.compile()


# Create the graph instance
graph = create_agent_graph()


def main():
    """Interactive conversation loop for testing the agent."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    config = Configuration()
    missing_vars = config.validate()
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return

    tools = get_tools()
    print("✅ sales-intelligence-agent-v2 Agent is ready!")
    print(f"🔧 Tools available: {len(tools)}")
    print("💬 Type 'quit' to exit\n")
    
    conversation: List[BaseMessage] = []
    
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
            
        conversation.append(HumanMessage(content=user_input))
        print("🤖 Processing...")
        
        try:
            result = graph.invoke({"messages": conversation})
            final_response = result["messages"][-1]
            conversation.append(final_response)
            
            print(f"🤖 Assistant: {final_response.content}")
            print("---")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---")


if __name__ == "__main__":
    main()