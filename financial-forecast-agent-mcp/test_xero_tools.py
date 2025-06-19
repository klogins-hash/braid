#!/usr/bin/env python3
"""
Test Xero MCP tools directly
"""

import json
from agent import mcp_manager
from config import config

def test_xero_tools():
    """Test what tools are available in Xero MCP"""
    print("🧪 Testing Xero MCP Tools")
    print("=" * 40)
    
    # Start the MCP manager
    results = mcp_manager.start_all()
    
    xero_client = mcp_manager.get_client('xero')
    if not xero_client:
        print("❌ Xero MCP client not available")
        return
    
    # List all available tools
    tools = xero_client.list_tools()
    print(f"✅ Xero MCP has {len(tools)} tools available:")
    
    for i, tool in enumerate(tools[:10]):  # Show first 10 tools
        print(f"  {i+1}. {tool.get('name', 'Unknown')}")
        
    if len(tools) > 10:
        print(f"  ... and {len(tools) - 10} more tools")
    
    # Find P&L related tools
    profit_tools = [t for t in tools if 'profit' in t.get('name', '').lower()]
    print(f"\n📊 Profit & Loss related tools:")
    for tool in profit_tools:
        print(f"  - {tool.get('name', 'Unknown')}")
    
    # Test organization details first (simpler)
    org_tools = [t for t in tools if 'organisation' in t.get('name', '').lower()]
    if org_tools:
        print(f"\n🏢 Testing organization details...")
        try:
            result = xero_client.call_tool(org_tools[0]['name'], {})
            print(f"✅ Organization test successful")
            print(f"Result type: {type(result)}")
            if isinstance(result, dict) and 'content' in result:
                print(f"Content preview: {str(result['content'])[:200]}...")
            else:
                print(f"Raw result preview: {str(result)[:200]}...")
        except Exception as e:
            print(f"❌ Organization test failed: {e}")
    
    # Cleanup
    mcp_manager.stop_all()

if __name__ == "__main__":
    test_xero_tools()