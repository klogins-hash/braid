"""Main graph definition for the financial_forecast_agent with 6-step workflow."""

import logging
import json
from typing import Dict, List, Any, Optional

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from financial_forecast_agent.configuration import Configuration
from financial_forecast_agent.prompts import get_system_prompt
from financial_forecast_agent.state import AgentState
from financial_forecast_agent.tools import get_tools
from financial_forecast_agent.utils import load_chat_model


def create_forecast_workflow():
    """Create the 6-step financial forecasting workflow."""
    config = Configuration()
    tools = get_tools()
    
    # Initialize model
    model = load_chat_model(config.model, config.temperature)
    if tools:
        model = model.bind_tools(tools)
    
    # Create tool node
    tool_node = ToolNode(tools) if tools else None
    
    def should_continue(state: AgentState) -> str:
        """Determine the next step in the workflow."""
        current_step = state.get("current_step", "start")
        
        # Check if we have the data needed for next step
        if current_step == "start" or current_step == "step_1":
            return "step_1_xero_data"
        elif current_step == "step_1_complete":
            return "step_2_client_info"
        elif current_step == "step_2_complete":
            return "step_3_market_research"
        elif current_step == "step_3_complete":
            return "step_4_assumptions"
        elif current_step == "step_4_complete":
            return "step_5_forecast"
        elif current_step == "step_5_complete":
            return "step_6_report"
        elif current_step == "step_6_complete":
            return END
        else:
            return "coordinator"
    
    # Step 1: Retrieve Xero Data
    def step_1_retrieve_xero_data(state: AgentState) -> Dict[str, Any]:
        """Step 1: Retrieve financial data from Xero and store in SQL database."""
        user_id = state.get("user_id", "user_123")  # Default for testing
        
        # Create message for Xero data retrieval
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", f"""Step 1: Retrieve Xero Data for user {user_id}
            
Please retrieve the necessary financial information from Xero using the Xero MCP. 
Since we're in testing mode, we'll simulate this by using our mock database historical data.

1. Get the historical financial data for user {user_id}
2. Store this as if it came from Xero
3. Confirm the data has been retrieved successfully

Use the get_historical_financial_data tool to retrieve the mock Xero data.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_1_tools",
            "user_id": user_id
        }
    
    # Step 2: Get Client Information
    def step_2_get_client_info(state: AgentState) -> Dict[str, Any]:
        """Step 2: Retrieve client information from database."""
        user_id = state.get("user_id", "user_123")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", f"""Step 2: Get Client Information for user {user_id}
            
Now retrieve the client information including:
- Industry and business type
- Business age
- Location
- Business strategy for the forecast period

Use the get_client_information tool to retrieve this data.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_2_tools"
        }
    
    # Step 3: Market Research
    def step_3_market_research(state: AgentState) -> Dict[str, Any]:
        """Step 3: Conduct market research using Perplexity."""
        client_info = state.get("client_info")
        
        if client_info:
            industry = client_info.get("industry", "Software Development")
            location = client_info.get("location", "San Francisco, CA")
        else:
            industry = "Software Development" 
            location = "San Francisco, CA"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", f"""Step 3: Market Research
            
Conduct market research for the {industry} industry in {location}.
Focus on:
- Industry growth outlook for the next 5 years
- Market trends and opportunities
- Economic factors affecting the industry
- Regional market conditions

Since we're in testing mode and may not have Perplexity MCP active, 
you can simulate this research or use HTTP tools to gather market information.
Provide a comprehensive industry outlook summary.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_3_tools"
        }
    
    # Step 4: Generate Assumptions
    def step_4_generate_assumptions(state: AgentState) -> Dict[str, Any]:
        """Step 4: Generate forecast assumptions based on data gathered."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", """Step 4: Generate Forecast Assumptions
            
Based on the historical data, client information, and market research, 
generate comprehensive forecast assumptions including:

Quantitative Assumptions:
- Annual revenue growth rate
- Cost of goods sold percentage
- Operating expense growth rate
- Tax rate
- Depreciation rate

Qualitative Assumptions:
- Market conditions impact
- Business strategy effects
- Risk factors
- Growth drivers

Create a structured set of assumptions that will be used for the 5-year forecast.
Use the validate_forecast_assumptions tool to check the reasonableness of your assumptions.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_4_tools"
        }
    
    # Step 5: Calculate Forecast with Feedback Loop
    def step_5_calculate_forecast(state: AgentState) -> Dict[str, Any]:
        """Step 5: Calculate P&L forecast with validation and feedback."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", """Step 5: Calculate Financial Forecast
            
Now calculate the 5-year P&L forecast using:
1. The historical financial data retrieved in Step 1
2. The forecast assumptions generated in Step 4

Process:
1. Use calculate_financial_forecast tool with historical data and assumptions
2. Review the results for reasonableness
3. If needed, adjust assumptions and recalculate (feedback loop)
4. Calculate key metrics and ratios
5. Generate scenario analysis (optimistic, base, pessimistic)
6. Store the final forecast results

This step should include validation and iterative refinement.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_5_tools"
        }
    
    # Step 6: Create Notion Report
    def step_6_create_report(state: AgentState) -> Dict[str, Any]:
        """Step 6: Generate comprehensive Notion report."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", """Step 6: Create Annual Financial Forecast Report
            
Create a comprehensive Notion report that includes:

1. Executive Summary
   - Key forecast highlights
   - Major assumptions
   - Risk factors

2. Historical Analysis Table
   - 3-5 years of historical data
   - Trend analysis

3. Forecast Results Table
   - 5-year projections
   - Year-over-year growth rates
   - Key financial ratios

4. Methodology Section
   - Data sources (Xero integration)
   - Assumptions rationale
   - Market research insights

5. Key Assumptions (Bulleted List)
   - Revenue growth drivers
   - Cost structure assumptions
   - Market factors
   - Risk considerations

6. Scenario Analysis
   - Base, optimistic, pessimistic cases
   - Sensitivity analysis

Since we're in testing mode, simulate the Notion report creation by generating 
the structured content that would be posted to Notion.""")
        ])
        
        messages = prompt.format_messages()
        response = model.invoke(messages)
        
        return {
            "messages": [response],
            "current_step": "step_6_complete",
            "workflow_complete": True
        }
    
    # Coordinator node to manage workflow
    def coordinator(state: AgentState) -> Dict[str, Any]:
        """Coordinate the workflow and handle step transitions."""
        current_step = state.get("current_step", "start")
        
        if current_step == "start":
            return {"current_step": "step_1", "messages": [AIMessage(content="Starting financial forecasting workflow...")]}
        
        # Handle step completions based on tool results
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                # Tool was called, mark step as progressing
                if current_step == "step_1_tools":
                    return {"current_step": "step_1_complete"}
                elif current_step == "step_2_tools":
                    return {"current_step": "step_2_complete"}
                elif current_step == "step_3_tools":
                    return {"current_step": "step_3_complete"}
                elif current_step == "step_4_tools":
                    return {"current_step": "step_4_complete"}
                elif current_step == "step_5_tools":
                    return {"current_step": "step_5_complete"}
        
        return {"current_step": current_step}
    
    # Build the workflow graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("coordinator", coordinator)
    builder.add_node("step_1_xero_data", step_1_retrieve_xero_data)
    builder.add_node("step_2_client_info", step_2_get_client_info)
    builder.add_node("step_3_market_research", step_3_market_research)
    builder.add_node("step_4_assumptions", step_4_generate_assumptions)
    builder.add_node("step_5_forecast", step_5_calculate_forecast)
    builder.add_node("step_6_report", step_6_create_report)
    
    if tool_node:
        builder.add_node("tools", tool_node)
    
    # Add edges
    builder.add_edge(START, "coordinator")
    builder.add_conditional_edges("coordinator", should_continue)
    
    # Tool edges for each step
    if tool_node:
        def tools_condition(state: AgentState) -> str:
            """Check if tools should be called."""
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "tools"
            return "coordinator"
        
        # Add conditional edges for tool usage
        for step in ["step_1_xero_data", "step_2_client_info", "step_3_market_research", 
                    "step_4_assumptions", "step_5_forecast", "step_6_report"]:
            builder.add_conditional_edges(step, tools_condition)
        
        builder.add_edge("tools", "coordinator")
    else:
        # Direct edges if no tools
        for step in ["step_1_xero_data", "step_2_client_info", "step_3_market_research",
                    "step_4_assumptions", "step_5_forecast", "step_6_report"]:
            builder.add_edge(step, "coordinator")
    
    return builder.compile()


# Create the graph instance
graph = create_forecast_workflow()


def main():
    """Interactive conversation loop for testing the forecasting workflow."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    config = Configuration()
    missing_vars = config.validate()
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return

    tools = get_tools()
    print("✅ Financial Forecasting Agent is ready!")
    print(f"🔧 Tools available: {len(tools)}")
    print("📊 6-Step Workflow: Xero → Client Info → Market Research → Assumptions → Forecast → Report")
    print("💬 Start by providing a user_id to begin forecasting, or type 'demo' for a demo\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle demo mode
        if user_input.lower() == "demo":
            user_input = "Please run a complete financial forecast for user_123"
        
        print("🤖 Starting Financial Forecasting Workflow...")
        
        try:
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "current_step": "start",
                "user_id": "user_123",  # Default for demo
                "xero_data": None,
                "client_info": None,
                "historical_data": None,
                "market_research": None,
                "forecast_assumptions": None,
                "forecast_results": None,
                "validation_feedback": None,
                "notion_report_url": None,
                "forecast_id": None
            }
            
            # Run the workflow
            final_state = graph.invoke(initial_state)
            
            # Display results
            print("\n" + "="*60)
            print("📈 FINANCIAL FORECASTING WORKFLOW COMPLETE")
            print("="*60)
            
            if final_state.get("workflow_complete"):
                print("✅ All 6 steps completed successfully!")
                print("📋 Forecast ID:", final_state.get("forecast_id", "Generated"))
                print("📄 Report:", "Created" if final_state.get("notion_report_url") else "Generated")
            
            # Show the final assistant response
            messages = final_state.get("messages", [])
            if messages:
                final_response = messages[-1]
                print("\n🤖 Final Result:")
                print(final_response.content)
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.exception("Workflow error")


if __name__ == "__main__":
    main()