#!/usr/bin/env python3
"""
Test script for MCP discovery and integration system.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.mcp.discovery import MCPDiscovery
from core.mcp.registry import MCPRegistry
from core.mcp.integration import MCPIntegrator


def test_mcp_registry():
    """Test MCP registry functionality."""
    print("🧪 Testing MCP Registry...")
    
    registry = MCPRegistry()
    
    # Test getting all MCPs
    all_mcps = registry.get_all_mcps()
    print(f"   Found {len(all_mcps)} MCPs in registry")
    
    # Test getting specific MCP
    notion_mcp = registry.get_mcp_by_id("notion")
    if notion_mcp:
        print(f"   ✅ Found Notion MCP: {notion_mcp['name']}")
    else:
        print("   ❌ Notion MCP not found")
        return False
    
    # Test category search
    productivity_mcps = registry.get_mcps_by_category("productivity")
    print(f"   Found {len(productivity_mcps)} productivity MCPs")
    
    # Test validation
    issues = registry.validate_mcp_metadata("notion")
    if issues:
        print(f"   ⚠️  Validation issues: {issues}")
    else:
        print("   ✅ Notion MCP metadata is valid")
    
    return True


def test_mcp_discovery():
    """Test MCP discovery functionality."""
    print("\n🔍 Testing MCP Discovery...")
    
    discovery = MCPDiscovery()
    
    # Test task analysis with different scenarios
    test_tasks = [
        "I need to update my Notion workspace with project information",
        "Help me search through my knowledge base and create meeting notes",
        "I want to build a simple file processing agent",
        "Create a system to manage GitHub repositories and issues",
        "Need integration with team chat for notifications"
    ]
    
    for task in test_tasks:
        print(f"\n   📝 Task: '{task}'")
        analysis = discovery.analyze_task_description(task)
        
        print(f"      Requires MCP: {analysis['requires_mcp']}")
        print(f"      Confidence: {analysis['confidence']:.0%}")
        
        if analysis['suggested_mcps']:
            for suggestion in analysis['suggested_mcps']:
                mcp_name = suggestion['mcp_data']['name']
                score = suggestion['relevance_score']
                print(f"      📌 Suggested: {mcp_name} (score: {score:.1f})")
        else:
            print("      No MCP suggestions")
    
    return True


def test_mcp_integration():
    """Test MCP integration functionality."""
    print("\n🔧 Testing MCP Integration...")
    
    integrator = MCPIntegrator()
    
    # Test preparing integration (without actually creating files)
    print("   Testing integration preparation...")
    
    # Mock agent directory (we won't actually create it)
    test_agent_path = "/tmp/test-agent"
    
    # Test getting setup requirements
    requirements = integrator.registry.get_mcp_by_id("notion")
    if requirements:
        auth = requirements.get("authentication", {})
        env_vars = auth.get("required_env_vars", [])
        print(f"   📋 Notion MCP requires: {env_vars}")
        print(f"   🐳 Docker required: {requirements.get('docker_required', False)}")
    
    return True


def test_user_interaction_flow():
    """Test the complete user interaction flow."""
    print("\n👤 Testing User Interaction Flow...")
    
    discovery = MCPDiscovery()
    
    # Simulate user request
    user_task = "I want to create an agent that can search my Notion workspace and create new pages based on research"
    
    print(f"   User request: '{user_task}'")
    
    # Analyze task
    analysis = discovery.analyze_task_description(user_task)
    
    if analysis['requires_mcp'] and analysis['confidence'] > 0.6:
        print(f"   🎯 High confidence ({analysis['confidence']:.0%}) - should suggest MCP")
        
        for suggestion in analysis['suggested_mcps']:
            print(f"\n   💡 Suggestion:")
            formatted = discovery.format_mcp_suggestion(suggestion)
            print("   " + formatted.replace('\n', '\n   '))
            
            # Get setup requirements
            setup = discovery.get_setup_requirements(suggestion['mcp_id'])
            print(f"\n   📋 Setup requirements:")
            print(f"      Authentication: {setup['authentication']['type']}")
            print(f"      Environment vars: {setup['authentication']['required_env_vars']}")
            print(f"      Complexity: {setup['complexity']}")
    else:
        print(f"   ℹ️  Low confidence ({analysis['confidence']:.0%}) - would not suggest MCP")
    
    return True


def main():
    """Run all MCP system tests."""
    print("🚀 Testing Braid MCP Integration System\n")
    
    tests = [
        ("Registry", test_mcp_registry),
        ("Discovery", test_mcp_discovery),
        ("Integration", test_mcp_integration),
        ("User Flow", test_user_interaction_flow)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} test passed")
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All MCP system tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)