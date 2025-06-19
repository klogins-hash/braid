#!/usr/bin/env python3
"""
Simple test of financial forecasting tools without the complex workflow
"""

import logging
from agent import mcp_manager, get_xero_financial_data, get_client_information

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_tools():
    """Test individual tools directly"""
    print("🧪 Testing Individual Financial Forecasting Tools")
    print("=" * 60)
    
    try:
        # Start MCP services
        results = mcp_manager.start_all()
        print(f"MCP Status: {results}")
        
        # Test 1: Client Information (no MCP dependency)
        print("\n1️⃣ Testing Client Information...")
        client_result = get_client_information.func("test_user_123")
        print(f"✅ Client Info: {client_result[:200]}...")
        
        # Test 2: Xero Financial Data (with MCP)
        print("\n2️⃣ Testing Xero Financial Data...")
        xero_result = get_xero_financial_data.func("profit_and_loss", "test_user_123")
        print(f"✅ Xero Result: {xero_result[:200]}...")
        
        # Test 3: Direct MCP call
        print("\n3️⃣ Testing Direct Xero MCP Call...")
        xero_client = mcp_manager.get_client('xero')
        if xero_client:
            # Try organization details first (simpler)
            org_result = xero_client.call_tool("list-organisation-details", {})
            print(f"✅ Org Details: {str(org_result)[:200]}...")
            
            # Now try profit and loss
            pl_result = xero_client.call_tool("list-profit-and-loss", {})
            print(f"✅ P&L Direct: {str(pl_result)[:200]}...")
        
        print("\n✅ All tool tests completed!")
        
        # Cleanup
        mcp_manager.stop_all()
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool test failed: {e}")
        if hasattr(mcp_manager, 'stop_all'):
            mcp_manager.stop_all()
        return False

if __name__ == "__main__":
    test_simple_tools()