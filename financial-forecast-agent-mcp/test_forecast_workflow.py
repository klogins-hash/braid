#!/usr/bin/env python3
"""
Simple test of the financial forecasting workflow
"""

import sys
import logging
from agent import FinancialForecastAgent

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_workflow():
    """Test the complete forecasting workflow"""
    print("🧪 Testing Financial Forecasting Workflow")
    print("=" * 50)
    
    try:
        # Create and start the agent
        agent = FinancialForecastAgent()
        
        if not agent.startup():
            print("❌ Failed to start agent")
            return False
        
        # Show MCP status
        print("\n📊 MCP Server Status:")
        agent.show_mcp_status()
        
        # Test individual tools first
        print("\n🔧 Testing individual tools...")
        
        # Test Xero data retrieval directly with MCP client
        from agent import mcp_manager
        xero_client = mcp_manager.get_client('xero')
        if xero_client:
            tools = xero_client.list_tools()
            print(f"✅ Xero MCP has {len(tools)} tools available")
            
            # Try to get profit and loss data
            try:
                result = xero_client.call_tool("list-xero-profit-and-loss", {})
                print(f"✅ Xero P&L test successful: {str(result)[:200]}...")
            except Exception as e:
                print(f"⚠️ Xero P&L test error: {e}")
        
        # Test Notion
        notion_client = mcp_manager.get_client('notion')
        if notion_client:
            tools = notion_client.list_tools()
            print(f"✅ Notion MCP has {len(tools)} tools available")
        
        print("\n🚀 Testing complete workflow...")
        
        # Run the complete workflow
        result = agent.run_forecast("test_user_123")
        print(f"\n✅ Workflow Result:\n{result}")
        
        # Cleanup
        agent.shutdown()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        if 'agent' in locals():
            agent.shutdown()
        return False

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)