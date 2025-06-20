#!/usr/bin/env python3
"""
Test MCP Server Setup
Validates that all MCP servers are running and accessible
"""

import requests
import json
import time
import sys

def test_mcp_server(name, port, endpoint="/health"):
    """Test if an MCP server is running and healthy."""
    try:
        url = f"http://localhost:{port}{endpoint}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {name} MCP Server: HEALTHY (port {port})")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   Status: {data.get('status', 'Unknown')}")
            except:
                pass
            return True
        else:
            print(f"❌ {name} MCP Server: UNHEALTHY (port {port}) - Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} MCP Server: NOT RUNNING (port {port})")
        return False
    except Exception as e:
        print(f"❌ {name} MCP Server: ERROR (port {port}) - {e}")
        return False

def test_mcp_gateway():
    """Test the MCP gateway."""
    try:
        response = requests.get("http://localhost:3000/health", timeout=10)
        if response.status_code == 200:
            print("✅ MCP Gateway: HEALTHY")
            data = response.json()
            print(f"   Services configured: {list(data.get('services', {}).keys())}")
            return True
        else:
            print(f"❌ MCP Gateway: UNHEALTHY - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Gateway: ERROR - {e}")
        return False

def main():
    print("🧪 Testing MCP Server Setup")
    print("=" * 40)
    
    # Test individual MCP servers
    servers = [
        ("Xero", 3002),
        ("Perplexity", 3003), 
        ("Notion", 3001)
    ]
    
    results = []
    for name, port in servers:
        result = test_mcp_server(name, port)
        results.append(result)
        time.sleep(1)
    
    print("\n🌐 Testing MCP Gateway...")
    gateway_result = test_mcp_gateway()
    
    print("\n" + "=" * 40)
    print("📊 MCP Setup Test Results")
    print("=" * 40)
    
    if all(results) and gateway_result:
        print("✅ ALL MCP SERVERS ARE RUNNING!")
        print("🎉 Ready to run MCP-based financial forecast agent")
        print("\n🚀 Next steps:")
        print("   1. Update your agent to use MCP tools")
        print("   2. Run: python run_mcp_agent.py")
        return 0
    else:
        print("❌ SOME MCP SERVERS ARE NOT RUNNING")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Docker is running")
        print("   2. Check .env file has all API keys")
        print("   3. Run: ./start-mcp-servers.sh")
        print("   4. Check logs: docker-compose -f docker-compose.mcp.yml logs")
        return 1

if __name__ == "__main__":
    sys.exit(main())