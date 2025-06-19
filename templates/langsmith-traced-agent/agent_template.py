#!/usr/bin/env python3
"""
LangSmith Traced Agent Template
Ensures unified workflow tracing instead of isolated tool calls

This template demonstrates the CORRECT way to build LangGraph agents
that show unified traces in LangSmith, avoiding the common issue where
tool calls appear as isolated events.
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Import your custom tools here
# from your_module.tools import your_tool_1, your_tool_2

class AgentState(Dict):
    """State schema for the agent."""
    messages: List[Any]
    user_id: str
    step: int
    completed: bool
    results: Dict[str, Any]

def create_traced_agent():
    """
    Create a LangGraph agent with PROPER LangSmith tracing.
    
    CRITICAL: This template ensures unified workflow traces by:
    1. Routing all tool calls through LangGraph nodes
    2. Properly handling ToolMessage responses
    3. Maintaining conversation flow through the graph
    """
    
    # Define your tools here
    tools = [
        # your_tool_1,
        # your_tool_2,
    ]
    
    # Create tool lookup for execution
    tool_map = {tool.name: tool for tool in tools}
    
    # Create model with tools bound
    model = ChatOpenAI(model="gpt-4o", temperature=0.1)
    model = model.bind_tools(tools)
    
    def agent_node(state: AgentState) -> AgentState:
        """
        Agent node that makes tool calls.
        
        IMPORTANT: This is where the LLM decides which tools to call.
        The actual tool execution happens in the tool_node.
        """
        
        user_id = state.get("user_id", "default_user")
        step = state.get("step", 1)
        messages = state.get("messages", [])
        
        # Create step-specific prompts
        if step == 1:
            prompt = f"""Execute Step 1 of the workflow:
            
            Use the appropriate tools to complete the first step for user {user_id}.
            [Customize this prompt for your specific workflow]"""
            
        elif step == 2:
            prompt = f"""Execute Step 2 of the workflow:
            
            Use the appropriate tools to complete the second step for user {user_id}.
            [Customize this prompt for your specific workflow]"""
            
        # Add more steps as needed
        else:
            return {
                **state,
                "completed": True
            }
        
        # Add message and get LLM response
        new_message = HumanMessage(content=prompt)
        updated_messages = messages + [new_message]
        
        # LLM decides which tools to call
        response = model.invoke(updated_messages)
        updated_messages.append(response)
        
        return {
            **state,
            "messages": updated_messages,
            "step": step
        }
    
    def tool_node(state: AgentState) -> AgentState:
        """
        Tool execution node that creates proper ToolMessage responses.
        
        CRITICAL: This is what makes LangSmith tracing work correctly.
        Each tool call gets a corresponding ToolMessage with the same tool_call_id.
        """
        
        messages = state.get("messages", [])
        step = state.get("step", 1)
        
        # Get the last message (should contain tool calls)
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return state
        
        # Execute each tool call
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_call_id = tool_call['id']
            
            print(f"🔧 Executing {tool_name} with args: {tool_args}")
            
            if tool_name in tool_map:
                try:
                    # Execute the tool
                    result = tool_map[tool_name].invoke(tool_args)
                    
                    # Create ToolMessage with matching tool_call_id
                    tool_message = ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(tool_message)
                    
                    print(f"✅ {tool_name} completed successfully")
                    
                except Exception as e:
                    print(f"❌ Error executing {tool_name}: {e}")
                    error_message = ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(error_message)
            else:
                print(f"❌ Unknown tool: {tool_name}")
                error_message = ToolMessage(
                    content=f"Error: Unknown tool {tool_name}",
                    tool_call_id=tool_call_id
                )
                tool_messages.append(error_message)
        
        # Add tool messages to conversation
        updated_messages = messages + tool_messages
        
        # Move to next step after tool execution
        next_step = step + 1
        
        return {
            **state,
            "messages": updated_messages,
            "step": next_step
        }
    
    def should_continue(state: AgentState) -> str:
        """
        Router function that decides the next step.
        
        This creates the agent → tools → agent flow that ensures
        unified tracing in LangSmith.
        """
        messages = state.get("messages", [])
        completed = state.get("completed", False)
        
        if completed:
            return END
        
        # Check if last message has tool calls
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
        
        # Continue to agent for next step
        return "agent"
    
    # Build the LangGraph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    
    # Add edges for proper flow
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_conditional_edges("tools", should_continue)
    
    return builder.compile()

def run_traced_workflow(user_id: str = "test_user"):
    """
    Run the workflow with proper LangSmith tracing.
    
    This will show as ONE unified trace in LangSmith with a clear
    waterfall of agent → tools → agent execution.
    """
    
    print("🚀 LANGSMITH TRACED AGENT")
    print("=" * 50)
    print(f"User: {user_id}")
    print("Features: Unified LangSmith Workflow Trace")
    print("=" * 50)
    
    # Check LangSmith configuration
    langsmith_key = os.getenv('LANGCHAIN_API_KEY')
    langsmith_tracing = os.getenv('LANGCHAIN_TRACING_V2')
    
    print(f"🔐 LangSmith Status:")
    print(f"   API Key: {'✅ Set' if langsmith_key else '❌ Missing'}")
    print(f"   Tracing: {'✅ Enabled' if langsmith_tracing == 'true' else '❌ Disabled'}")
    
    if not langsmith_key or langsmith_tracing != 'true':
        print("\n⚠️  LangSmith not properly configured")
        print("Set LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2=true in .env")
        return None
    
    try:
        # Create the traced agent
        agent = create_traced_agent()
        
        print("\n✅ LangGraph agent created with proper tracing")
        print("🔄 Executing workflow - check LangSmith for unified trace...")
        print("📊 Monitor at: https://smith.langchain.com/")
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content=f"Run workflow for {user_id}")],
            "user_id": user_id,
            "step": 1,
            "completed": False,
            "results": {}
        }
        
        # Execute the traced workflow
        final_state = agent.invoke(initial_state)
        
        print("\n✅ LangGraph workflow completed successfully!")
        print("📈 Check LangSmith dashboard - you should see:")
        print("   🔗 One unified run with waterfall of steps")
        print("   📊 Each tool call as part of the same trace")
        print("   🎯 Proper agent → tools → agent flow")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function for testing the traced agent."""
    
    print("🚀 LANGSMITH TRACED AGENT TEMPLATE")
    print("=" * 45)
    
    user_id = input("\nEnter user_id (or press Enter for 'test_user'): ").strip()
    if not user_id:
        user_id = "test_user"
    
    print(f"\n🚀 Running traced workflow for: {user_id}")
    
    try:
        results = run_traced_workflow(user_id)
        
        if results:
            print("\n✅ LangSmith traced workflow completed!")
            print("📈 Check LangSmith for unified trace")
        else:
            print("\n❌ Workflow failed")
        
        return results
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()