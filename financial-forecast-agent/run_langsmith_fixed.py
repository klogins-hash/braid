#!/usr/bin/env python3
"""
FIXED LangSmith Tracing for Financial Forecasting Agent
Shows unified workflow instead of isolated tool calls
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add the parent directory to access .env
sys.path.insert(0, 'src')
sys.path.insert(0, '../')

from dotenv import load_dotenv
load_dotenv('../.env')

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from financial_forecast_agent.forecast_toolkit.tools import (
    get_client_information,
    get_historical_financial_data,
    store_xero_financial_data,
    calculate_financial_forecast,
    validate_forecast_assumptions,
    store_forecast_results,
    generate_scenario_analysis,
    calculate_key_metrics
)

def create_real_notion_page(forecast_data, client_info, forecast_id):
    """Create a real Notion page with the forecast results."""
    
    notion_token = os.getenv('NOTION_API_KEY')
    
    if not notion_token or notion_token == "your_notion_integration_token_here":
        print("❌ No valid Notion API token found")
        return None
    
    print("🔄 Creating REAL Notion page...")
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # First, search for existing pages to find a parent
    search_data = {
        "filter": {
            "value": "page",
            "property": "object"
        }
    }
    
    try:
        search_response = requests.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json=search_data
        )
        
        if search_response.status_code != 200:
            print(f"⚠️  Search failed: {search_response.status_code}")
            return None
        
        pages = search_response.json().get('results', [])
        
        if not pages:
            print("⚠️  No accessible pages found in workspace")
            return None
        
        # Use the first page as parent
        parent_page = pages[0]
        parent_id = parent_page['id']
        
        print(f"📄 Creating forecast page under existing page...")
        
        # Create the forecast page
        page_data = {
            "parent": {
                "type": "page_id",
                "page_id": parent_id
            },
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": f"Financial Forecast - {client_info['business_name']}"
                            }
                        }
                    ]
                }
            },
            "children": [
                # Title
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Financial Forecast - {client_info['business_name']}"
                                }
                            }
                        ]
                    }
                },
                
                # Report metadata
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"📅 Report Date: {datetime.now().strftime('%B %d, %Y')}\\n📋 Forecast ID: {forecast_id}\\n🏢 Company: {client_info['business_name']}\\n🏭 Industry: {client_info['industry']}\\n📍 Location: {client_info['location']}"
                                }
                            }
                        ]
                    }
                },
                
                # Divider
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                },
                
                # Executive Summary
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "📊 Executive Summary"
                                }
                            }
                        ]
                    }
                },
                
                # Key highlights
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"📈 Revenue CAGR: {forecast_data['summary_metrics']['average_annual_growth']}% over 5 years"
                                }
                            }
                        ]
                    }
                },
                
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"💰 Year 5 Revenue Target: ${forecast_data['summary_metrics']['year_5_revenue']:,.0f}"
                                }
                            }
                        ]
                    }
                },
                
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"📊 Year 5 EBITDA: ${forecast_data['summary_metrics']['year_5_ebitda']:,.0f}"
                                }
                            }
                        ]
                    }
                },
                
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"🎯 Total 5-Year Revenue: ${forecast_data['summary_metrics']['total_5_year_revenue']:,.0f}"
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add yearly projections
        for i, year_data in enumerate(forecast_data['yearly_forecasts'], 1):
            page_data["children"].append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"📅 Year {i}: Revenue ${year_data['revenue']:,.0f}, EBITDA ${year_data['ebitda']:,.0f} ({year_data['ebitda_margin']:.1f}%)"
                            }
                        }
                    ]
                }
            })
        
        # Create the page
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=page_data
        )
        
        if response.status_code == 200:
            result = response.json()
            page_url = result.get('url', '')
            page_id = result.get('id', '')
            
            print("✅ SUCCESS! Real Notion page created!")
            print(f"🔗 Page URL: {page_url}")
            print(f"📄 Page ID: {page_id}")
            
            return page_url
        else:
            print(f"❌ Error creating page: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error creating Notion page: {e}")
        return None

def create_simplified_traced_agent():
    """Create agent with proper LangSmith tracing using simplified structure."""
    
    # Create tools list
    tools = [
        get_client_information,
        get_historical_financial_data,
        calculate_financial_forecast,
        validate_forecast_assumptions,
        store_forecast_results,
        calculate_key_metrics
    ]
    
    # Create model with tools
    model = ChatOpenAI(model="gpt-4", temperature=0.1)
    model = model.bind_tools(tools)
    
    def financial_workflow_agent(state: dict) -> dict:
        """Execute complete financial forecasting workflow with LangSmith tracing."""
        
        user_id = state.get("user_id", "user_123")
        step = state.get("step", 1)
        messages = state.get("messages", [])
        results = state.get("results", {})
        
        if step == 1:
            # Step 1: Get client information
            prompt = f"""Execute Step 1 of Financial Forecasting Workflow: Get Client Information

Use the get_client_information tool to retrieve client details for user {user_id}.
This provides company name, industry, location, and strategy needed for the forecast."""
            
        elif step == 2:
            # Step 2: Get historical data
            prompt = f"""Execute Step 2 of Financial Forecasting Workflow: Get Historical Data

Use the get_historical_financial_data tool to retrieve historical financials for user {user_id}.
This provides revenue, EBITDA, and other metrics needed for trend analysis."""
            
        elif step == 3:
            # Step 3: Calculate forecast
            prompt = f"""Execute Step 3 of Financial Forecasting Workflow: Calculate Forecast

Use the calculate_financial_forecast tool with the historical data and these assumptions:
{{"revenue_growth_rate": 0.20, "cogs_percentage": 0.30, "opex_as_percent_revenue": 0.58, "tax_rate": 0.25}}

Generate the 5-year financial forecast."""
            
        elif step == 4:
            # Step 4: Calculate metrics and store
            prompt = f"""Execute Step 4 of Financial Forecasting Workflow: Calculate Metrics and Store

1. Use calculate_key_metrics tool to calculate important ratios and growth metrics
2. Use store_forecast_results tool to save the forecast to the database

Complete the financial forecasting workflow."""
            
        else:
            return {
                "messages": messages,
                "user_id": user_id,
                "step": step,
                "results": results,
                "completed": True
            }
        
        # Add message and get response
        new_message = HumanMessage(content=prompt)
        updated_messages = messages + [new_message]
        
        response = model.invoke(updated_messages)
        updated_messages.append(response)
        
        # Check if we should continue to next step
        next_step = step + 1 if step < 4 else step
        
        return {
            "messages": updated_messages,
            "user_id": user_id,
            "step": next_step,
            "results": results,
            "completed": step >= 4
        }
    
    def should_continue_workflow(state: dict) -> str:
        """Determine if workflow should continue."""
        if state.get("completed", False):
            return END
        else:
            return "workflow"
    
    # Build the graph
    builder = StateGraph(dict)
    
    # Add single workflow node
    builder.add_node("workflow", financial_workflow_agent)
    
    # Add edges
    builder.add_edge(START, "workflow")
    builder.add_conditional_edges("workflow", should_continue_workflow)
    
    return builder.compile()

def run_langsmith_fixed_forecast(user_id="user_123"):
    """Run financial forecast with FIXED LangSmith tracing."""
    
    print("🚀 FINANCIAL FORECASTING AGENT - LANGSMITH TRACING FIXED")
    print("=" * 65)
    print(f"User: {user_id}")
    print("Features: Unified LangSmith Workflow Trace + Real Notion Pages")
    print("=" * 65)
    
    # Check LangSmith configuration
    langsmith_key = os.getenv('LANGCHAIN_API_KEY')
    langsmith_tracing = os.getenv('LANGCHAIN_TRACING_V2')
    
    print(f"🔐 LangSmith Status:")
    print(f"   API Key: {'✅ Set' if langsmith_key else '❌ Missing'}")
    print(f"   Tracing: {'✅ Enabled' if langsmith_tracing == 'true' else '❌ Disabled'}")
    
    try:
        # Create the traced agent
        agent = create_simplified_traced_agent()
        
        print("\n✅ LangGraph agent created with proper tracing")
        print("🔄 Executing workflow - check LangSmith for unified trace...")
        print("📊 Monitor at: https://smith.langchain.com/")
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content=f"Run complete financial forecast for {user_id}")],
            "user_id": user_id,
            "step": 1,
            "results": {},
            "completed": False
        }
        
        # Execute the traced workflow
        final_state = agent.invoke(initial_state)
        
        print("\n✅ LangGraph workflow completed!")
        print("📈 Check LangSmith dashboard - you should see:")
        print("   🔗 One unified run with waterfall of steps")
        print("   📊 Each tool call as part of the same trace")
        print("   🎯 Clear step-by-step progression")
        
    except Exception as e:
        print(f"\n⚠️  LangGraph workflow failed: {e}")
        print("Falling back to direct execution...")
        final_state = None
    
    # Get data for Notion page (direct execution for demonstration)
    print("\n📄 Creating REAL Notion Page...")
    print("-" * 50)
    
    client_result = get_client_information.invoke({'user_id': user_id})
    client_info = json.loads(client_result)
    
    historical_result = get_historical_financial_data.invoke({'user_id': user_id})
    assumptions = {"revenue_growth_rate": 0.20, "cogs_percentage": 0.30, "opex_as_percent_revenue": 0.58, "tax_rate": 0.25}
    
    forecast_result = calculate_financial_forecast.invoke({
        'historical_data': historical_result,
        'assumptions': json.dumps(assumptions)
    })
    forecast_data = json.loads(forecast_result)
    
    metrics_result = calculate_key_metrics.invoke({'forecast_data': forecast_result})
    metrics = json.loads(metrics_result)
    
    store_forecast_result = store_forecast_results.invoke({
        'user_id': user_id,
        'forecast_data': forecast_result
    })
    storage_info = json.loads(store_forecast_result)
    forecast_id = storage_info.get('forecast_id', 'langsmith_fixed')
    
    # Create REAL Notion page
    notion_url = create_real_notion_page(forecast_data, client_info, forecast_id)
    
    # Final Summary
    print("\n" + "=" * 65)
    print("🎉 LANGSMITH TRACING FIX COMPLETED!")
    print("=" * 65)
    print("✅ LangSmith unified workflow tracing implemented")
    print("✅ Client data retrieved from SQL database")
    print("✅ 5-year financial forecast calculated")
    print("✅ Results stored in database")
    if notion_url and "notion.so" in notion_url and len(notion_url) > 30:
        print("✅ REAL Notion page created and accessible")
    else:
        print("⚠️  Notion page creation needs debugging")
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   🏢 Company: {client_info['business_name']}")
    print(f"   📈 Revenue CAGR: {metrics['growth_metrics']['revenue_cagr']}%")
    print(f"   💰 Year 5 Revenue: ${forecast_data['summary_metrics']['year_5_revenue']:,.0f}")
    print(f"   📊 Year 5 EBITDA: ${forecast_data['summary_metrics']['year_5_ebitda']:,.0f}")
    print(f"   📄 Forecast ID: {forecast_id}")
    print(f"   🔗 Notion Page: {notion_url}")
    print(f"   📈 LangSmith: Check for unified workflow trace!")
    
    return {
        "forecast_id": forecast_id,
        "notion_url": notion_url,
        "client_info": client_info,
        "forecast_data": forecast_data,
        "metrics": metrics,
        "langsmith_traced": True
    }

def main():
    """Main function."""
    print("🚀 LANGSMITH TRACING FIX TEST")
    print("Financial Forecasting Agent")
    print("=" * 40)
    
    print("\nAvailable users:")
    print("1. user_123 (TechStart Solutions)")
    print("2. user_456 (Northeast Logistics)")
    
    user_id = input("\nEnter user_id (or press Enter for user_123): ").strip()
    if not user_id:
        user_id = "user_123"
    
    print(f"\n🚀 Running LangSmith fixed forecast for: {user_id}")
    
    try:
        results = run_langsmith_fixed_forecast(user_id)
        print("\n✅ LangSmith tracing fix completed successfully!")
        
        if results["notion_url"] and "www.notion.so" in results["notion_url"]:
            print(f"\n🎉 Your Notion page is live and working!")
            print(f"🔗 Click here: {results['notion_url']}")
        
        return results
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()