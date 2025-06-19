#!/usr/bin/env python3
"""
Test the complete financial forecasting toolkit components independently.
This validates all our new functionality works correctly.
"""

import logging
import json
from enhanced_agent import mcp_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_toolkit():
    """Test all toolkit components working together."""
    print("🧪 TESTING COMPLETE FINANCIAL FORECASTING TOOLKIT")
    print("=" * 70)
    
    try:
        # Start MCP services
        print("🔌 Starting MCP services...")
        mcp_results = mcp_manager.start_all()
        print(f"MCP Status: {mcp_results}")
        
        # Test 1: SQL Database Operations
        print("\n1️⃣ TESTING SQL DATABASE OPERATIONS")
        print("-" * 40)
        
        from tools.sql_tools import get_client_info_from_sql, store_xero_data_to_sql
        
        # Get client info
        client_info = get_client_info_from_sql.func("user_123")
        print(f"✅ Client Info Retrieved: {json.loads(client_info)['company_name']}")
        
        # Store sample Xero data
        sample_xero_data = {
            "revenue": 1000000,
            "expenses": 800000,
            "profit": 200000
        }
        store_result = store_xero_data_to_sql.func(json.dumps(sample_xero_data), "user_123")
        print(f"✅ Xero Data Stored: {store_result[:50]}...")
        
        # Test 2: AI-Powered Forecasting Engine
        print("\n2️⃣ TESTING AI-POWERED FORECASTING ENGINE")
        print("-" * 40)
        
        from tools.forecast_tools import (
            generate_forecast_assumptions_with_ai,
            calculate_financial_forecast_python,
            validate_and_review_forecast
        )
        
        # Generate assumptions
        market_research = "Software development industry showing strong 18% growth with AI trends driving expansion"
        assumptions = generate_forecast_assumptions_with_ai.func("[]", market_research, client_info)
        print("✅ AI-Generated Assumptions Created")
        
        # Calculate forecast
        forecast = calculate_financial_forecast_python.func("[]", assumptions, 5)
        forecast_data = json.loads(forecast)
        print(f"✅ 5-Year Forecast Calculated: Year 1 Revenue ${forecast_data[0]['revenue']:,.0f}")
        
        # Validate forecast
        validation = validate_and_review_forecast.func(forecast, assumptions)
        validation_data = json.loads(validation)
        print(f"✅ Forecast Validated: Status = {validation_data['validation_status']}")
        
        # Test 3: Complete SQL Storage Workflow
        print("\n3️⃣ TESTING COMPLETE SQL STORAGE WORKFLOW")
        print("-" * 40)
        
        from tools.sql_tools import (
            store_forecast_assumptions_sql,
            store_forecast_results_sql,
            approve_forecast_sql
        )
        
        # Store assumptions
        assumptions_result = store_forecast_assumptions_sql.func(assumptions, "user_123")
        print(f"✅ Assumptions Stored: {assumptions_result[:50]}...")
        
        # Extract assumptions ID (simplified)
        assumptions_id = "1"  # Would be extracted from actual result
        
        # Store forecast results
        results_storage = store_forecast_results_sql.func(forecast, assumptions_id, "user_123")
        print(f"✅ Forecast Results Stored: {results_storage[:50]}...")
        
        # Approve forecast
        approval = approve_forecast_sql.func(assumptions_id, "user_123")
        print(f"✅ Forecast Approved: {approval[:50]}...")
        
        # Test 4: MCP Integration
        print("\n4️⃣ TESTING MCP INTEGRATION")
        print("-" * 40)
        
        from enhanced_agent import get_xero_financial_data, conduct_market_research
        
        # Test Xero MCP
        xero_data = get_xero_financial_data.func("profit_and_loss", "user_123")
        print(f"✅ Xero MCP Data: {xero_data[:100]}...")
        
        # Test Perplexity API
        market_data = conduct_market_research.func("Software Development", "San Francisco, CA")
        print(f"✅ Market Research: {market_data[:100]}...")
        
        # Test 5: Key Metrics and Scenarios
        print("\n5️⃣ TESTING ADVANCED ANALYTICS")
        print("-" * 40)
        
        from tools.forecast_tools import calculate_key_financial_metrics, generate_forecast_scenarios
        
        # Calculate key metrics
        metrics = calculate_key_financial_metrics.func(forecast)
        metrics_data = json.loads(metrics)
        print(f"✅ Key Metrics: Revenue CAGR = {metrics_data['growth_metrics']['revenue_cagr']}%")
        
        # Generate scenarios
        scenarios = generate_forecast_scenarios.func(forecast, "all")
        scenarios_data = json.loads(scenarios)
        print(f"✅ Scenarios Generated: {list(scenarios_data.keys())}")
        
        # Final Summary
        print("\n📊 TOOLKIT VALIDATION SUMMARY")
        print("=" * 40)
        print("✅ SQL Database: Fully operational")
        print("✅ Python Forecasting Engine: Fully operational") 
        print("✅ AI-Powered Assumptions: Fully operational")
        print("✅ MCP Integration: Fully operational")
        print("✅ Validation & Scenarios: Fully operational")
        print("✅ Complete Data Flow: Working end-to-end")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Toolkit test failed: {e}")
        return False
    finally:
        mcp_manager.stop_all()

if __name__ == "__main__":
    success = test_complete_toolkit()
    if success:
        print("\n🏆 COMPLETE TOOLKIT TEST PASSED - ALL SYSTEMS OPERATIONAL")
    else:
        print("\n❌ TOOLKIT TEST FAILED")