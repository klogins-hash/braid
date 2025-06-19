#!/usr/bin/env python3
"""
Test enhanced braid new command with MCP discovery.
"""

import sys
from pathlib import Path

# Add braid root to path
braid_root = Path(__file__).parent
sys.path.insert(0, str(braid_root))

from core.mcp.discovery import MCPDiscovery

def test_enhanced_discovery():
    """Test enhanced MCP discovery scenarios."""
    discovery = MCPDiscovery()
    
    test_scenarios = [
        ("Notion knowledge management", "notion"),
        ("Web scraping for competitive intelligence", "agentql"), 
        ("Financial portfolio tracking", "alphavantage"),
        ("Stock market analysis bot", "alphavantage"),
        ("Trading assistant with technical analysis", "alphavantage")
    ]
    
    print("🧪 Testing Enhanced Braid New MCP Discovery\n")
    
    for description, expected_mcp in test_scenarios:
        print(f"📝 Testing: '{description}'")
        print(f"   Expected: {expected_mcp}")
        
        analysis = discovery.analyze_task_description(description)
        suggested_mcps = analysis.get('suggested_mcps', [])
        
        # Filter high confidence suggestions (like the braid new command does)
        high_confidence = [
            mcp for mcp in suggested_mcps 
            if mcp.get('relevance_score', 0) > 15.0  # Using relevance as proxy for confidence
        ]
        
        if high_confidence:
            top_suggestion = high_confidence[0]
            suggested_id = top_suggestion.get('mcp_id', 'unknown')
            print(f"   ✅ Top suggestion: {suggested_id}")
            print(f"      Name: {top_suggestion.get('mcp_data', {}).get('name', 'Unknown')}")
            print(f"      Relevance: {top_suggestion.get('relevance_score', 0):.1f}")
            
            if suggested_id == expected_mcp:
                print(f"   🎯 Correct suggestion!")
            else:
                print(f"   ⚠️  Expected {expected_mcp}, got {suggested_id}")
        else:
            print(f"   ❌ No high-confidence suggestions")
        
        print()

if __name__ == "__main__":
    test_enhanced_discovery()