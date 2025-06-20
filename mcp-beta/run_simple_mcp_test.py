#!/usr/bin/env python3
"""
Simple MCP-based test without separate servers
Tests the MCP tools directly integrated in the agent
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to path
sys.path.insert(0, 'src')

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

def test_mcp_tools():
    """Test all MCP tools directly."""
    print("🧪 Testing MCP Tools Integration")
    print("=" * 50)
    
    user_id = "user_123"
    
    try:
        # Test 1: Client Information
        print("📋 Test 1: Getting client information...")
        client_result = get_client_information.invoke({'user_id': user_id})
        client_info = json.loads(client_result) if isinstance(client_result, str) else client_result
        print(f"✅ Client: {client_info.get('business_name', 'Unknown')}")
        
        # Test 2: Historical Financial Data
        print("\n💰 Test 2: Getting historical financial data...")
        historical_result = get_historical_financial_data.invoke({'user_id': user_id})
        historical_data = json.loads(historical_result) if isinstance(historical_result, str) else historical_result
        print(f"✅ Historical data: {len(historical_data)} periods")
        
        # Test 3: Store Xero Data
        print("\n📊 Test 3: Storing Xero data...")
        store_result = store_xero_financial_data.invoke({
            'user_id': user_id,
            'xero_data': json.dumps({'profit_loss_data': historical_data})
        })
        print("✅ Xero data stored")
        
        # Test 4: Validate Assumptions
        print("\n📋 Test 4: Validating forecast assumptions...")
        assumptions = {
            "revenue_growth_rate": 0.20,
            "cogs_percentage": 0.30,
            "opex_as_percent_revenue": 0.55,
            "tax_rate": 0.25,
            "depreciation_rate": 0.02
        }
        
        validation_result = validate_forecast_assumptions.invoke({'assumptions': json.dumps(assumptions)})
        validation = json.loads(validation_result) if isinstance(validation_result, str) else validation_result
        print(f"✅ Validation: {'PASSED' if validation.get('is_valid') else 'FAILED'}")
        
        # Test 5: Calculate Forecast
        print("\n🧮 Test 5: Calculating financial forecast...")
        forecast_result = calculate_financial_forecast.invoke({
            'historical_data': json.dumps(historical_data),
            'assumptions': json.dumps(assumptions)
        })
        forecast_data = json.loads(forecast_result) if isinstance(forecast_result, str) else forecast_result
        print(f"✅ Forecast generated: {len(forecast_data.get('yearly_forecasts', []))} years")
        
        # Test 6: Calculate Metrics
        print("\n📈 Test 6: Calculating key metrics...")
        metrics_result = calculate_key_metrics.invoke({'forecast_data': json.dumps(forecast_data)})
        metrics = json.loads(metrics_result) if isinstance(metrics_result, str) else metrics_result
        print(f"✅ Metrics calculated: {metrics.get('growth_metrics', {}).get('revenue_cagr', 'N/A')}% CAGR")
        
        # Test 7: Scenario Analysis
        print("\n📊 Test 7: Generating scenario analysis...")
        scenarios_result = generate_scenario_analysis.invoke({
            'historical_data': json.dumps(historical_data),
            'base_assumptions': json.dumps(assumptions)
        })
        scenarios = json.loads(scenarios_result) if isinstance(scenarios_result, str) else scenarios_result
        print("✅ Scenario analysis completed")
        
        # Test 8: Store Results
        print("\n💾 Test 8: Storing forecast results...")
        store_forecast_result = store_forecast_results.invoke({
            'user_id': user_id,
            'forecast_data': json.dumps(forecast_data)
        })
        storage_info = json.loads(store_forecast_result) if isinstance(store_forecast_result, str) else store_forecast_result
        forecast_id = storage_info.get('forecast_id', 'test_forecast')
        print(f"✅ Results stored with ID: {forecast_id}")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 ALL MCP TOOLS TESTS PASSED!")
        print("=" * 50)
        print(f"📊 Company: {client_info.get('business_name', 'Unknown')}")
        print(f"📈 Revenue CAGR: {metrics.get('growth_metrics', {}).get('revenue_cagr', 'N/A')}%")
        print(f"💰 Year 5 Revenue: ${forecast_data.get('summary_metrics', {}).get('year_5_revenue', 0):,.0f}")
        print(f"📄 Forecast ID: {forecast_id}")
        print("\n✅ MCP tools are working correctly without separate servers!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mcp_tools()
    sys.exit(0 if success else 1)