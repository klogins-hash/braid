#!/usr/bin/env python3
"""
Financial Forecasting Agent with PROPER LangSmith Tracing
Fixed to show unified workflow instead of isolated tool calls
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, 'src')
sys.path.insert(0, '../')

from dotenv import load_dotenv
load_dotenv('../.env')

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from financial_forecast_agent.configuration import Configuration
from financial_forecast_agent.state import AgentState
from financial_forecast_agent.tools import get_tools
from financial_forecast_agent.utils import load_chat_model

def create_proper_langsmith_agent():
    """Create agent that properly traces in LangSmith as unified workflow."""
    
    config = Configuration()
    tools = get_tools()
    
    # Initialize model with tools
    model = load_chat_model(config.model, config.temperature)
    if tools:
        model = model.bind_tools(tools)
    
    # Create tool node for proper tracing
    tool_node = ToolNode(tools) if tools else None
    
    def agent_node(state: AgentState) -> dict:
        """Main agent node that handles the complete forecasting workflow."""
        
        user_id = state.get("user_id", "user_123")
        messages = state.get("messages", [])
        
        # Get the user's request
        if messages:
            user_request = messages[-1].content
        else:
            user_request = f"Run complete financial forecast for {user_id}"
        
        # Create comprehensive workflow prompt
        system_prompt = f"""You are a Financial Forecasting Agent. Execute the complete 6-step workflow:

1. **Get Client Information**: Use get_client_information tool for user {user_id}
2. **Get Historical Data**: Use get_historical_financial_data tool for user {user_id}  
3. **Generate Assumptions**: Create forecast assumptions based on data
4. **Calculate Forecast**: Use calculate_financial_forecast tool with historical data and assumptions
5. **Validate Results**: Use validate_forecast_assumptions and calculate_key_metrics tools
6. **Store Results**: Use store_forecast_results tool to save the forecast

Execute these steps in sequence using the available tools. For each step, explain what you're doing and use the appropriate tool.

USER REQUEST: {user_request}

Begin with step 1: Get client information for user {user_id}."""

        # Create a comprehensive message that will trigger tool usage
        messages = [
            AIMessage(content="I'll execute the complete financial forecasting workflow. Let me start by getting the client information."),
            HumanMessage(content=system_prompt)
        ]
        
        # Invoke the model with the workflow prompt
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "user_id": user_id,
            "current_step": "workflow_executing"
        }
    
    def should_continue(state: AgentState) -> str:
        """Determine if we should continue to tools or end."""
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            # Check if the agent wants to use tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
        return END
    
    # Build the graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("agent", agent_node)
    if tool_node:
        builder.add_node("tools", tool_node)
    
    # Add edges
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    
    if tool_node:
        builder.add_edge("tools", "agent")
    
    return builder.compile()

def create_step_by_step_agent():
    """Create an agent that executes each step explicitly for better tracing."""
    
    config = Configuration()
    tools = get_tools()
    
    model = load_chat_model(config.model, config.temperature)
    if tools:
        model = model.bind_tools(tools)
    
    tool_node = ToolNode(tools) if tools else None
    
    def step_1_client_info(state: AgentState) -> dict:
        """Step 1: Get client information."""
        user_id = state.get("user_id", "user_123")
        
        prompt = f"""Step 1 of Financial Forecasting Workflow: Get Client Information

Please use the get_client_information tool to retrieve client details for user {user_id}.
This will provide the company name, industry, location, and business strategy needed for the forecast."""

        response = model.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": state.get("messages", []) + [response],
            "current_step": "step_1_complete" if hasattr(response, 'tool_calls') and response.tool_calls else "step_1_waiting",
            "user_id": user_id
        }
    
    def step_2_historical_data(state: AgentState) -> dict:
        """Step 2: Get historical financial data."""
        user_id = state.get("user_id", "user_123")
        
        prompt = f"""Step 2 of Financial Forecasting Workflow: Get Historical Financial Data

Please use the get_historical_financial_data tool to retrieve historical financials for user {user_id}.
This will provide the revenue, EBITDA, and other metrics needed for trend analysis."""

        response = model.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": state.get("messages", []) + [response],
            "current_step": "step_2_complete" if hasattr(response, 'tool_calls') and response.tool_calls else "step_2_waiting",
            "user_id": user_id
        }
    
    def step_3_calculate_forecast(state: AgentState) -> dict:
        """Step 3: Calculate the forecast."""
        user_id = state.get("user_id", "user_123")
        
        # Create sample assumptions for the forecast
        assumptions = {
            "revenue_growth_rate": 0.20,
            "cogs_percentage": 0.30,
            "opex_as_percent_revenue": 0.58,
            "tax_rate": 0.25
        }
        
        prompt = f"""Step 3 of Financial Forecasting Workflow: Calculate Financial Forecast

Use the calculate_financial_forecast tool with these assumptions:
{json.dumps(assumptions, indent=2)}

Also use the historical data from step 2 to generate the 5-year forecast."""

        response = model.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": state.get("messages", []) + [response],
            "current_step": "step_3_complete" if hasattr(response, 'tool_calls') and response.tool_calls else "step_3_waiting",
            "user_id": user_id
        }
    
    def step_4_finalize(state: AgentState) -> dict:
        """Step 4: Store results and calculate metrics."""
        user_id = state.get("user_id", "user_123")
        
        prompt = f"""Step 4 of Financial Forecasting Workflow: Finalize Results

1. Use calculate_key_metrics tool to calculate important ratios and growth metrics
2. Use store_forecast_results tool to save the forecast to the database

Complete the financial forecasting workflow."""

        response = model.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": state.get("messages", []) + [response],
            "current_step": "workflow_complete",
            "user_id": user_id
        }
    
    def should_continue_steps(state: AgentState) -> str:
        """Route to next step or tools."""
        current_step = state.get("current_step", "start")
        messages = state.get("messages", [])
        
        # Check if last message has tool calls
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
        
        # Route based on current step
        if current_step == "start":
            return "step_1_client_info"
        elif current_step == "step_1_complete":
            return "step_2_historical_data"
        elif current_step == "step_2_complete":
            return "step_3_calculate_forecast"
        elif current_step == "step_3_complete":
            return "step_4_finalize"
        elif current_step == "workflow_complete":
            return END
        else:
            # If waiting for tools, continue current step
            return "tools"
    
    def tool_completion_router(state: AgentState) -> str:
        """Route after tool execution."""
        current_step = state.get("current_step", "start")
        
        if "step_1" in current_step:
            return "step_2_historical_data"
        elif "step_2" in current_step:
            return "step_3_calculate_forecast"
        elif "step_3" in current_step:
            return "step_4_finalize"
        else:
            return END
    
    # Build the step-by-step graph
    builder = StateGraph(AgentState)
    
    # Add step nodes
    builder.add_node("step_1_client_info", step_1_client_info)
    builder.add_node("step_2_historical_data", step_2_historical_data)
    builder.add_node("step_3_calculate_forecast", step_3_calculate_forecast)
    builder.add_node("step_4_finalize", step_4_finalize)
    
    if tool_node:
        builder.add_node("tools", tool_node)
    
    # Add edges
    builder.add_edge(START, "step_1_client_info")
    
    # Add conditional edges from each step
    for step in ["step_1_client_info", "step_2_historical_data", "step_3_calculate_forecast", "step_4_finalize"]:
        builder.add_conditional_edges(step, should_continue_steps)
    
    if tool_node:
        builder.add_conditional_edges("tools", tool_completion_router)
    
    return builder.compile()

def test_langsmith_tracing():
    """Test LangSmith tracing with proper workflow visibility."""
    
    print("🔍 Testing LangSmith Tracing - Step-by-Step Workflow")
    print("=" * 60)
    
    # Create the step-by-step agent for better tracing
    agent = create_step_by_step_agent()
    
    print("✅ Agent created with proper LangSmith tracing")
    print("🔄 Executing workflow - check LangSmith for unified trace...")
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content="Run complete financial forecast for user_123")],
        "current_step": "start",
        "user_id": "user_123",
        "client_info": None,
        "historical_data": None,
        "forecast_results": None
    }
    
    try:
        # Execute the workflow
        final_state = agent.invoke(initial_state)
        
        print("\n📊 Workflow Results:")
        print(f"   Final Step: {final_state.get('current_step', 'unknown')}")
        print(f"   Messages: {len(final_state.get('messages', []))}")
        print(f"   User ID: {final_state.get('user_id', 'unknown')}")
        
        print("\n✅ Check LangSmith dashboard - you should see:")
        print("   🔗 One unified run with waterfall of steps")
        print("   📊 Each tool call as part of the same trace")
        print("   🎯 Clear step-by-step progression")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function."""
    print("🚀 LANGSMITH TRACING FIX TEST")
    print("=" * 50)
    
    # Check LangSmith configuration
    langsmith_key = os.getenv('LANGCHAIN_API_KEY')
    langsmith_tracing = os.getenv('LANGCHAIN_TRACING_V2')
    
    print(f"🔐 LangSmith Status:")
    print(f"   API Key: {'✅ Set' if langsmith_key else '❌ Missing'}")
    print(f"   Tracing: {'✅ Enabled' if langsmith_tracing == 'true' else '❌ Disabled'}")
    
    if not langsmith_key or langsmith_tracing != 'true':
        print("\n⚠️  LangSmith not properly configured")
        print("   Set LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2=true in .env")
        return
    
    print(f"\n🔄 Starting traced workflow...")
    print(f"📊 Monitor in LangSmith: https://smith.langchain.com/")
    
    result = test_langsmith_tracing()
    
    if result:
        print(f"\n🎉 Workflow completed!")
        print(f"📈 Check LangSmith for unified trace with waterfall view")
    else:
        print(f"\n❌ Workflow failed - check errors above")

if __name__ == "__main__":
    main()