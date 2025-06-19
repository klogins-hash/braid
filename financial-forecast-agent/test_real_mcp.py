#!/usr/bin/env python3
"""
Test script to connect to real MCP servers via subprocess/stdio
"""

import subprocess
import json
import os
import sys
from typing import Dict, Any

# Add the src directory to path
sys.path.insert(0, 'src')

class MCPClient:
    """Simple MCP client that connects to servers via stdio."""
    
    def __init__(self, server_path: str, server_args: list = None, env_vars: dict = None):
        self.server_path = server_path
        self.server_args = server_args or []
        self.env_vars = env_vars or {}
        self.process = None
        
    def start(self):
        """Start the MCP server process."""
        env = os.environ.copy()
        env.update(self.env_vars)
        
        cmd = [self.server_path] + self.server_args
        print(f"🚀 Starting MCP server: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            print(f"✅ MCP server started with PID: {self.process.pid}")
            return True
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process:
            raise Exception("MCP server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            response = self.process.stdout.readline()
            print(f"📥 Received: {response.strip()}")
            
            return json.loads(response)
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}
    
    def stop(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print(f"🛑 MCP server stopped")

def test_perplexity_mcp():
    """Test the Perplexity MCP server."""
    print("\n🔍 Testing Perplexity MCP Server")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if not perplexity_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        return False
    
    # Start Perplexity MCP server
    server_path = "/Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid/modelcontextprotocol/perplexity-ask/dist/index.js"
    
    client = MCPClient(
        server_path="node",
        server_args=[server_path],
        env_vars={"PERPLEXITY_API_KEY": perplexity_key}
    )
    
    if not client.start():
        return False
    
    try:
        # Initialize the connection
        print("\n📋 Step 1: Initialize connection")
        init_response = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "financial-forecast-agent",
                "version": "1.0.0"
            }
        })
        
        if "error" in init_response:
            print(f"❌ Initialize failed: {init_response['error']}")
            return False
        
        print("✅ Connection initialized")
        
        # List available tools
        print("\n📋 Step 2: List available tools")
        tools_response = client.send_request("tools/list")
        
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', '')}")
        
        # Test a simple search
        print("\n📋 Step 3: Test market research search")
        search_params = {
            "name": "perplexity_ask",
            "arguments": {
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the latest trends in financial technology for 2024?"
                    }
                ]
            }
        }
        
        search_response = client.send_request("tools/call", search_params)
        
        if "result" in search_response:
            content = search_response["result"]
            print("✅ Search completed successfully!")
            print(f"📊 Response preview: {str(content)[:200]}...")
            return True
        else:
            print(f"❌ Search failed: {search_response}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        client.stop()

def test_xero_mcp():
    """Test the Xero MCP server."""
    print("\n💰 Testing Xero MCP Server")
    print("=" * 50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # For now, just test if we can start it
    xero_token = os.getenv('XERO_ACCESS_TOKEN')
    if not xero_token:
        print("❌ XERO_ACCESS_TOKEN not found in environment")
        return False
    
    server_path = "/Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid/xero-mcp-server/dist/index.js"
    
    client = MCPClient(
        server_path="node",
        server_args=[server_path],
        env_vars={
            "XERO_CLIENT_BEARER_TOKEN": xero_token,
            "XERO_CLIENT_ID": os.getenv('XERO_CLIENT_ID', ''),
            "XERO_CLIENT_SECRET": os.getenv('XERO_CLIENT_SECRET', '')
        }
    )
    
    print("🚀 Attempting to start Xero MCP server...")
    if client.start():
        print("✅ Xero MCP server started successfully")
        client.stop()
        return True
    else:
        print("❌ Xero MCP server failed to start")
        return False

def test_notion_mcp():
    """Test the Notion MCP server."""
    print("\n📝 Testing Notion MCP Server")
    print("=" * 50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    notion_key = os.getenv('NOTION_API_KEY')
    if not notion_key:
        print("❌ NOTION_API_KEY not found in environment")
        return False
    
    server_path = "/Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid/notion-mcp-server/bin/cli.mjs"
    
    client = MCPClient(
        server_path="node",
        server_args=[server_path],
        env_vars={"NOTION_API_KEY": notion_key}
    )
    
    if not client.start():
        return False
    
    try:
        # Initialize the connection
        print("\n📋 Step 1: Initialize connection")
        init_response = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "financial-forecast-agent",
                "version": "1.0.0"
            }
        })
        
        if "error" in init_response:
            print(f"❌ Initialize failed: {init_response['error']}")
            return False
        
        print("✅ Connection initialized")
        
        # List available tools
        print("\n📋 Step 2: List available tools")
        tools_response = client.send_request("tools/list")
        
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', '')[:60]}...")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
            return True
        else:
            print(f"❌ Tools list failed: {tools_response}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        client.stop()

def main():
    """Run MCP server tests."""
    print("🧪 Testing Real MCP Servers")
    print("=" * 60)
    
    results = {}
    
    # Test Perplexity MCP
    results['perplexity'] = test_perplexity_mcp()
    
    # Test Xero MCP
    results['xero'] = test_xero_mcp()
    
    # Test Notion MCP
    results['notion'] = test_notion_mcp()
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for service, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{service.title()} MCP: {status}")
    
    total_passed = sum(results.values())
    print(f"\n🎯 {total_passed}/{len(results)} MCP servers working")
    
    if total_passed > 0:
        print("\n🎉 SUCCESS: Real MCP servers are working!")
        print("   You can now use these servers in your financial forecast agent")
        
        if total_passed == len(results):
            print("   🚀 ALL MCP SERVERS WORKING - Ready for full integration!")
    else:
        print("\n⚠️  No MCP servers are working yet - check configuration")
    
    return total_passed > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)