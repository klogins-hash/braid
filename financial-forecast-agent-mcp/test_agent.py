#!/usr/bin/env python3
"""
Test utilities for MCP-enabled agent
"""

import os
import sys
import argparse
import asyncio
from typing import Dict, Any, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import MCPAgent, mcp_manager

class AgentTester:
    """Test framework for MCP-enabled agents."""
    
    def __init__(self):
        self.test_results = {}
        
    def test_mcp_connections(self) -> Dict[str, bool]:
        """Test MCP server connections."""
        print("🧪 Testing MCP Server Connections")
        print("=" * 50)
        
        results = mcp_manager.start_all()
        
        for server, status in results.items():
            if status:
                print(f"✅ {server.title()} MCP: Connected")
                self.test_results[f"mcp_{server}"] = True
            else:
                print(f"❌ {server.title()} MCP: Failed")
                self.test_results[f"mcp_{server}"] = False
        
        # Stop all clients
        mcp_manager.stop_all()
        
        return results
    
    def test_agent_workflow(self) -> bool:
        """Test basic agent workflow."""
        print("\n🤖 Testing Agent Workflow")
        print("=" * 50)
        
        try:
            # Create agent
            agent = MCPAgent()
            
            # Test startup
            print("📋 Testing agent startup...")
            if not agent.startup():
                print("❌ Agent startup failed")
                return False
            print("✅ Agent started successfully")
            
            # Test simple query
            print("📋 Testing simple query...")
            response = agent.run("Hello, how are you?")
            if response and len(response) > 0:
                print("✅ Agent responded successfully")
                print(f"   Response preview: {response[:100]}...")
                self.test_results["workflow_basic"] = True
            else:
                print("❌ Agent failed to respond")
                self.test_results["workflow_basic"] = False
                return False
            
            # Test shutdown
            print("📋 Testing agent shutdown...")
            agent.shutdown()
            print("✅ Agent shutdown completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Agent workflow test failed: {e}")
            self.test_results["workflow_basic"] = False
            return False
    
    def test_mcp_tools(self) -> Dict[str, bool]:
        """Test MCP-powered tools."""
        print("\n🔧 Testing MCP Tools")
        print("=" * 50)
        
        tool_results = {}
        
        try:
            agent = MCPAgent()
            if not agent.startup():
                print("❌ Could not start agent for tool testing")
                return {}
            
            # Test web research (if Perplexity is available)
            if 'perplexity' in mcp_manager.clients:
                print("📋 Testing web research tool...")
                try:
                    response = agent.run("Research the weather today")
                    if response and "error" not in response.lower():
                        print("✅ Web research tool working")
                        tool_results["web_research"] = True
                    else:
                        print("❌ Web research tool failed")
                        tool_results["web_research"] = False
                except Exception as e:
                    print(f"❌ Web research test error: {e}")
                    tool_results["web_research"] = False
            
            # Test financial data (if Xero is available)
            if 'xero' in mcp_manager.clients:
                print("📋 Testing financial data tool...")
                try:
                    response = agent.run("Get a simple financial report")
                    if response and "error" not in response.lower():
                        print("✅ Financial data tool working")
                        tool_results["financial_data"] = True
                    else:
                        print("❌ Financial data tool failed")
                        tool_results["financial_data"] = False
                except Exception as e:
                    print(f"❌ Financial data test error: {e}")
                    tool_results["financial_data"] = False
            
            # Test Notion integration (if Notion is available)
            if 'notion' in mcp_manager.clients:
                print("📋 Testing Notion integration...")
                try:
                    response = agent.run("Search for any existing pages in the workspace")
                    if response and "error" not in response.lower():
                        print("✅ Notion integration working")
                        tool_results["notion_integration"] = True
                    else:
                        print("❌ Notion integration failed")
                        tool_results["notion_integration"] = False
                except Exception as e:
                    print(f"❌ Notion integration test error: {e}")
                    tool_results["notion_integration"] = False
            
            agent.shutdown()
            
        except Exception as e:
            print(f"❌ Tool testing failed: {e}")
        
        self.test_results.update(tool_results)
        return tool_results
    
    def test_environment_setup(self) -> Dict[str, bool]:
        """Test environment configuration."""
        print("\n⚙️  Testing Environment Setup")
        print("=" * 50)
        
        env_results = {}
        
        # Check required environment variables
        required_vars = [
            "OPENAI_API_KEY",
            "PERPLEXITY_API_KEY", 
            "XERO_ACCESS_TOKEN",
            "NOTION_API_KEY"
        ]
        
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var}: Set")
                env_results[f"env_{var.lower()}"] = True
            else:
                print(f"❌ {var}: Not set")
                env_results[f"env_{var.lower()}"] = False
        
        # Check optional variables
        optional_vars = [
            "LANGCHAIN_API_KEY",
            "LANGCHAIN_TRACING_V2",
            "XERO_CLIENT_ID",
            "XERO_CLIENT_SECRET"
        ]
        
        print("\nOptional environment variables:")
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var}: Set")
            else:
                print(f"⚠️  {var}: Not set (optional)")
        
        self.test_results.update(env_results)
        return env_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite."""
        print("🚀 Running Complete Test Suite")
        print("=" * 60)
        
        # Test environment
        self.test_environment_setup()
        
        # Test MCP connections
        self.test_mcp_connections()
        
        # Test agent workflow
        self.test_agent_workflow()
        
        # Test MCP tools
        self.test_mcp_tools()
        
        return self.test_results
    
    def print_summary(self):
        """Print test results summary."""
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        print(f"Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed:")
            for test, result in self.test_results.items():
                if not result:
                    print(f"  ❌ {test}")
            return False

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Test MCP-enabled agent')
    parser.add_argument('--test-mcp', action='store_true', help='Test MCP connections only')
    parser.add_argument('--test-workflow', action='store_true', help='Test agent workflow only')
    parser.add_argument('--test-tools', action='store_true', help='Test MCP tools only')
    parser.add_argument('--test-env', action='store_true', help='Test environment setup only')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    tester = AgentTester()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if args.test_mcp:
        tester.test_mcp_connections()
    elif args.test_workflow:
        tester.test_agent_workflow()
    elif args.test_tools:
        tester.test_mcp_tools()
    elif args.test_env:
        tester.test_environment_setup()
    elif args.all:
        tester.run_all_tests()
    else:
        # Default: run all tests
        tester.run_all_tests()
    
    # Print summary
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()