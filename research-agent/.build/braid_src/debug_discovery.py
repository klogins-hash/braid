#!/usr/bin/env python3
"""
Debug script to understand MCP discovery issues.
"""

import sys
from pathlib import Path

# Add braid root to path
braid_root = Path(__file__).parent
sys.path.insert(0, str(braid_root))

from core.mcp.discovery import MCPDiscovery
from core.mcp.registry import MCPRegistry

def debug_discovery():
    """Debug MCP discovery system."""
    print("🔍 Debugging MCP Discovery System\n")
    
    # Test registry
    registry = MCPRegistry()
    all_mcps = registry.get_all_mcps()
    
    print(f"📋 Available MCPs in registry: {len(all_mcps)}")
    for mcp_id, mcp_data in all_mcps.items():
        print(f"   - {mcp_id}: {mcp_data.get('name', 'Unknown')}")
    print()
    
    # Test discovery patterns
    discovery = MCPDiscovery()
    
    test_description = "Stock market analysis and portfolio tracking"
    print(f"📝 Testing: '{test_description}'")
    
    # Test individual components
    task_lower = test_description.lower()
    
    # Test pattern matching
    for mcp_id, patterns in discovery.task_patterns.items():
        for pattern in patterns:
            import re
            if re.search(pattern, task_lower):
                print(f"   ✅ Pattern match for {mcp_id}: {pattern}")
                break
        else:
            print(f"   ❌ No pattern match for {mcp_id}")
    
    print()
    
    # Test individual pattern matching
    pattern_matches = discovery._find_pattern_matches(task_lower)
    print(f"📝 Pattern matches: {len(pattern_matches)}")
    for match in pattern_matches:
        print(f"   - {match['mcp_id']}: {match['mcp_data'].get('name', 'Unknown')} (confidence: {match['confidence']})")
    print()
    
    # Test full analysis
    analysis = discovery.analyze_task_description(test_description)
    print(f"📊 Full analysis result:")
    print(f"   Suggested MCPs: {len(analysis.get('suggested_mcps', []))}")
    print(f"   Analysis: {analysis.get('analysis', {})}")
    
    for i, mcp in enumerate(analysis.get('suggested_mcps', [])):
        print(f"   {i+1}. MCP ID: {mcp.get('mcp_id', 'Unknown')}")
        print(f"      Name: {mcp.get('mcp_data', {}).get('name', 'Unknown')}")
        print(f"      Confidence: {mcp.get('confidence', 0):.2f}")
        print(f"      Relevance: {mcp.get('relevance_score', 0):.2f}")
        print(f"      Match Type: {mcp.get('match_type', 'Unknown')}")
        print(f"      Raw MCP: {mcp}")
        print()

if __name__ == "__main__":
    debug_discovery()