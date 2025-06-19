#!/usr/bin/env python3
"""
Simple MCP connection test for debugging
"""

import os
import json
import subprocess
from dotenv import load_dotenv
from config import config

load_dotenv()

def test_node_version():
    """Test Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Node.js not found: {e}")
        return False

def test_mcp_server_files():
    """Test if MCP server files exist"""
    servers = {
        'xero': 'mcp_servers/xero/dist/index.js',
        'notion': 'mcp_servers/notion/bin/cli.mjs', 
        'perplexity': 'mcp_servers/perplexity/dist/index.js'
    }
    
    for name, path in servers.items():
        if os.path.exists(path):
            print(f"✅ {name} MCP server found: {path}")
        else:
            print(f"❌ {name} MCP server missing: {path}")

def test_config_validation():
    """Test config validation"""
    missing = config.validate_required_env_vars()
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
    else:
        print("✅ All required environment variables set")

def test_simple_mcp_connection():
    """Test a simple MCP server connection"""
    print("\n🧪 Testing simple MCP connection...")
    
    # Try to start the Xero MCP server (if available)
    xero_path = "mcp_servers/xero/dist/index.js"
    if os.path.exists(xero_path):
        try:
            env = os.environ.copy()
            env.update({
                "XERO_CLIENT_BEARER_TOKEN": config.XERO_ACCESS_TOKEN or "test-token",
                "XERO_CLIENT_ID": config.XERO_CLIENT_ID or "test-id",
                "XERO_CLIENT_SECRET": config.XERO_CLIENT_SECRET or "test-secret"
            })
            
            process = subprocess.Popen(
                ['node', xero_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read response with timeout
            import select
            ready, _, _ = select.select([process.stdout], [], [], 5.0)
            
            if ready:
                response = process.stdout.readline()
                if response:
                    data = json.loads(response)
                    if "result" in data:
                        print("✅ Xero MCP server initialized successfully")
                    else:
                        print(f"❌ Xero MCP initialization failed: {data}")
                else:
                    print("❌ No response from Xero MCP server")
            else:
                print("❌ Xero MCP server timeout")
            
            process.terminate()
            process.wait()
            
        except Exception as e:
            print(f"❌ Xero MCP test failed: {e}")
            if 'process' in locals():
                process.terminate()
    else:
        print("⚠️ Xero MCP server not found for testing")

def main():
    print("🧪 MCP Connection Test")
    print("=" * 50)
    
    # Test prerequisites
    print("\n📋 Prerequisites:")
    test_node_version()
    test_mcp_server_files()
    test_config_validation()
    
    # Test MCP connection
    test_simple_mcp_connection()
    
    print("\n✅ Test completed")

if __name__ == "__main__":
    main()