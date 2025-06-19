#!/usr/bin/env python3
"""
Test script to demonstrate MCP discovery for financial use cases.
"""

import sys
from pathlib import Path

# Add braid root to path
braid_root = Path(__file__).parent
sys.path.insert(0, str(braid_root))

from core.mcp.discovery import MCPDiscovery

def test_financial_discovery():
    """Test MCP discovery for financial use cases."""
    discovery = MCPDiscovery()
    
    test_cases = [
        "Stock market analysis and portfolio tracking",
        "Investment research with real-time financial data",
        "Trading bot with technical analysis",
        "Financial dashboard with market data",
        "Portfolio management and stock screening"
    ]
    
    print("🔍 Testing Financial MCP Discovery\n")
    
    for description in test_cases:
        print(f"📝 Description: '{description}'")
        analysis = discovery.analyze_task_description(description)
        
        suggested_mcps = analysis.get('suggested_mcps', [])
        high_confidence = [mcp for mcp in suggested_mcps if mcp.get('confidence', 0) > 0.7]
        
        if high_confidence:
            print(f"   ✅ Suggested MCPs:")
            for mcp in high_confidence:
                confidence_icon = "🔥" if mcp['confidence'] > 0.9 else "✨" if mcp['confidence'] > 0.8 else "💡"
                print(f"      {confidence_icon} {mcp['name']} ({mcp['confidence']:.0%})")
                if mcp.get('match_reasons'):
                    reasons = ', '.join(mcp['match_reasons'][:2])
                    print(f"         Reason: {reasons}")
        else:
            print("   ❌ No high-confidence MCPs suggested")
        
        print()

if __name__ == "__main__":
    test_financial_discovery()