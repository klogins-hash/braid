#!/usr/bin/env python3
"""
Test the complete enhanced 6-step financial forecasting workflow.
"""

import logging
from enhanced_agent import EnhancedFinancialForecastAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_workflow():
    """Test the complete enhanced workflow."""
    print("🧪 TESTING ENHANCED FINANCIAL FORECASTING WORKFLOW")
    print("=" * 70)
    
    # Create agent
    agent = EnhancedFinancialForecastAgent()
    
    try:
        # Start agent
        if not agent.startup():
            print("❌ Agent startup failed")
            return False
        
        print("\n✅ Agent started successfully")
        
        # Show system status
        agent.show_system_status()
        
        # Test workflow execution
        print("\n🚀 Testing complete 6-step workflow...")
        result = agent.run_forecast("user_123")
        print(f"\n📊 Workflow Result: {result}")
        
        # Test database integration
        print("\n🗄️ Testing database integration...")
        from database.database import db_manager
        
        # Check stored data
        client = db_manager.get_client("user_123")
        print(f"Client data: {client['company_name'] if client else 'None'}")
        
        historical_data = db_manager.get_historical_data("user_123")
        print(f"Historical records: {len(historical_data)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    finally:
        agent.shutdown()

if __name__ == "__main__":
    success = test_enhanced_workflow()
    if success:
        print("\n✅ ENHANCED WORKFLOW TEST PASSED")
    else:
        print("\n❌ ENHANCED WORKFLOW TEST FAILED")