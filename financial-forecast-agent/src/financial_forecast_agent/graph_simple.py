"""Simplified financial forecasting agent for testing."""

import logging
import json
from typing import Dict, List, Any

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from financial_forecast_agent.configuration import Configuration
from financial_forecast_agent.prompts import get_system_prompt
from financial_forecast_agent.state import AgentState
from financial_forecast_agent.tools import get_tools
from financial_forecast_agent.utils import load_chat_model


def create_simple_forecast_agent():
    """Create a simplified forecasting agent for testing."""
    config = Configuration()
    tools = get_tools()
    
    # Initialize model
    model = load_chat_model(config.model, config.temperature)
    if tools:
        model = model.bind_tools(tools)
    
    def agent_node(state: AgentState) -> Dict[str, Any]:
        """Main agent node that handles the forecasting workflow."""
        messages = state.get("messages", [])
        user_id = state.get("user_id", "user_123")
        
        # Get the latest human message
        if messages:
            last_message = messages[-1]
            user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            user_input = "Run financial forecast"
        
        # Create comprehensive prompt for the full workflow
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_system_prompt()),
            ("human", f"""Please execute the complete 6-step financial forecasting workflow for user {user_id}:

USER REQUEST: {user_input}

Execute these steps in sequence:

1. **Retrieve Historical Data**: Use get_historical_financial_data tool for user {user_id}
2. **Get Client Information**: Use get_client_information tool for user {user_id}  
3. **Market Research**: Based on the client's industry and location, provide market outlook analysis
4. **Generate Assumptions**: Create quantitative assumptions for revenue growth, margins, etc.
5. **Calculate Forecast**: Use calculate_financial_forecast tool with historical data and assumptions
6. **Generate Report**: Create a comprehensive financial forecast report structure

Please execute this complete workflow step by step, using the appropriate tools where indicated.""")
        ])
        
        # Format and invoke
        formatted_messages = prompt.format_messages()
        response = model.invoke(formatted_messages)
        
        return {
            "messages": [response],
            "current_step": "completed",
            "user_id": user_id
        }
    
    # Build simple graph
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    
    return builder.compile()


def main():
    """Test the financial forecasting agent."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🚀 Financial Forecasting Agent Test")
    print("=" * 50)
    
    config = Configuration()
    missing_vars = config.validate()
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return

    tools = get_tools()
    print(f"✅ Agent initialized with {len(tools)} tools")
    print("📊 Available forecast tools:")
    for tool in tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
    
    # Create the agent
    graph = create_simple_forecast_agent()
    print("✅ LangGraph workflow created")
    
    # Test the workflow
    print("\n🧪 Testing Financial Forecasting Workflow...")
    print("-" * 50)
    
    try:
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content="Please run a complete financial forecast for user_123")],
            "current_step": "start",
            "user_id": "user_123",
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
        
        print("🤖 Executing workflow...")
        
        # Run the workflow
        final_state = graph.invoke(initial_state)
        
        # Display results
        print("\n" + "="*60)
        print("📈 FINANCIAL FORECASTING WORKFLOW RESULTS")
        print("="*60)
        
        messages = final_state.get("messages", [])
        if messages:
            final_response = messages[-1]
            print("\n🤖 Agent Response:")
            print("-" * 40)
            print(final_response.content)
        
        print("\n✅ Workflow completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        logging.exception("Workflow execution error")
        
        # Let's also test the individual components
        print("\n🔧 Testing Individual Components...")
        
        # Test database
        try:
            from financial_forecast_agent.forecast_toolkit.database import ForecastDatabase
            with ForecastDatabase() as db:
                client = db.get_client_info('user_123')
                historical = db.get_historical_data('user_123')
                print(f"✅ Database: {client['business_name']} with {len(historical)} records")
        except Exception as db_error:
            print(f"❌ Database test failed: {db_error}")
        
        # Test forecasting engine
        try:
            from financial_forecast_agent.forecast_toolkit.forecasting_engine import PLForecastingEngine
            engine = PLForecastingEngine()
            assumptions = {'revenue_growth_rate': 0.25, 'tax_rate': 0.25}
            print("✅ Forecasting engine initialized")
        except Exception as engine_error:
            print(f"❌ Forecasting engine test failed: {engine_error}")


if __name__ == "__main__":
    main()