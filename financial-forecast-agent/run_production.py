#!/usr/bin/env python3
"""
Production Financial Forecasting Agent
Connects to live Xero, Perplexity, and Notion APIs
"""

import sys
import os
sys.path.insert(0, 'src')

from langchain_core.messages import HumanMessage
from financial_forecast_agent.graph_simple import create_simple_forecast_agent
from financial_forecast_agent.configuration import Configuration

def run_production_agent():
    """Run the production agent with live API connections."""
    
    print("🚀 PRODUCTION FINANCIAL FORECASTING AGENT")
    print("=" * 60)
    print("⚠️  This will connect to live Xero, Perplexity, and Notion APIs")
    print("=" * 60)
    
    # Validate configuration
    config = Configuration()
    missing_vars = config.validate()
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nRequired for production:")
        print("- XERO_BEARER_TOKEN (for financial data)")
        print("- PERPLEXITY_API_KEY (for market research)")  
        print("- NOTION_API_KEY (for report generation)")
        return False
    
    print("✅ Configuration validated")
    
    # Check for production-specific variables
    required_production_vars = [
        'XERO_BEARER_TOKEN',
        'PERPLEXITY_API_KEY', 
        'NOTION_API_KEY'
    ]
    
    missing_production = [var for var in required_production_vars if not os.getenv(var)]
    
    if missing_production:
        print(f"\n⚠️  Missing production variables: {', '.join(missing_production)}")
        print("Running in DEMO mode with mock data...")
        use_live_apis = False
    else:
        print("✅ All production APIs configured")
        use_live_apis = True
    
    # Create the agent
    graph = create_simple_forecast_agent()
    print("✅ Production agent initialized")
    
    # Interactive loop
    print("\n💬 Production Financial Forecasting Agent Ready!")
    print("Commands:")
    print("  'forecast [user_id]' - Run complete forecast")
    print("  'demo' - Run with demo data")
    print("  'quit' - Exit")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\n👤 Enter command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == 'demo':
                user_id = 'user_123'
                message = "Run complete financial forecast with demo data"
            elif command == 'forecast':
                user_id = parts[1] if len(parts) > 1 else 'user_123'
                if use_live_apis:
                    message = f"Run complete financial forecast using live APIs for user {user_id}"
                else:
                    message = f"Run complete financial forecast with demo data for user {user_id}"
            else:
                message = user_input
                user_id = 'user_123'
            
            print(f"\n🤖 Processing: {message}")
            print("⏳ This may take 30-60 seconds for live API calls...")
            
            # Execute workflow
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_step": "start",
                "user_id": user_id,
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
            
            final_state = graph.invoke(initial_state)
            
            # Display results
            print("\n" + "="*50)
            print("📊 FORECAST COMPLETED")
            print("="*50)
            
            messages = final_state.get("messages", [])
            if messages:
                response = messages[-1]
                print(response.content)
            
            print("\n✅ Workflow completed successfully!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    run_production_agent()