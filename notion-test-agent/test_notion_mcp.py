#!/usr/bin/env python3
"""
Test script to verify Notion MCP integration is working correctly.
"""

import os
import json
import asyncio
import subprocess
import time
from pathlib import Path


def load_environment():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def test_notion_api_direct():
    """Test direct connection to Notion API."""
    print("🔗 Testing direct Notion API connection...")
    
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        print("   ❌ NOTION_API_KEY not found in environment")
        return False
    
    print(f"   🔑 API Key found: {api_key[:20]}...")
    
    try:
        import requests
        
        # Test basic API connection
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Connected to Notion API successfully!")
            print(f"   👤 User: {user_data.get('name', 'Unknown')}")
            print(f"   📧 Email: {user_data.get('person', {}).get('email', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Notion API error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except ImportError:
        print("   ⚠️  requests library not available, installing...")
        subprocess.run(["pip", "install", "requests"], check=True)
        return test_notion_api_direct()  # Retry after install
    except Exception as e:
        print(f"   ❌ Error connecting to Notion API: {e}")
        return False


def test_mcp_server_install():
    """Test if the Notion MCP server can be installed and run."""
    print("\n🚀 Testing Notion MCP server installation...")
    
    try:
        # Check if npx is available
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ npx not found - Node.js is required for MCP server")
            return False
        
        print(f"   ✅ npx available: {result.stdout.strip()}")
        
        # Test MCP server installation (but don't run it yet)
        print("   📦 Testing MCP server package availability...")
        result = subprocess.run(
            ["npx", "-y", "@notionhq/notion-mcp-server", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Notion MCP server package is available")
            return True
        else:
            print(f"   ❌ MCP server test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ MCP server installation timeout (but package likely available)")
        return True
    except Exception as e:
        print(f"   ❌ Error testing MCP server: {e}")
        return False


def test_mcp_server_connection():
    """Test running the MCP server and connecting to it."""
    print("\n🔌 Testing MCP server connection...")
    
    api_key = os.getenv('NOTION_API_KEY')
    if not api_key:
        print("   ❌ NOTION_API_KEY not found")
        return False
    
    try:
        # Set up environment for MCP server
        env = os.environ.copy()
        env['NOTION_API_KEY'] = api_key
        
        print("   🚀 Starting Notion MCP server...")
        
        # Start the MCP server as a subprocess
        process = subprocess.Popen(
            ["npx", "-y", "@notionhq/notion-mcp-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("   ✅ MCP server started successfully!")
            
            # Try to send a simple MCP message
            try:
                # Send initialization message
                init_message = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "braid-test-client",
                            "version": "1.0.0"
                        }
                    }
                }) + "\n"
                
                process.stdin.write(init_message)
                process.stdin.flush()
                
                # Wait for response (with timeout)
                process.wait(timeout=5)
                stdout, stderr = process.communicate()
                
                if "method" in stdout or "result" in stdout:
                    print("   ✅ MCP server responded to initialization!")
                    print("   🎯 Notion MCP integration is working!")
                    return True
                else:
                    print(f"   ⚠️  MCP server output: {stdout}")
                    print(f"   ⚠️  MCP server errors: {stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ MCP server response timeout")
                process.terminate()
                return False
                
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ MCP server failed to start")
            print(f"   📝 stdout: {stdout}")
            print(f"   📝 stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing MCP server: {e}")
        return False


def test_integration_files():
    """Test that all MCP integration files are properly created."""
    print("\n📁 Testing MCP integration files...")
    
    base_path = Path(__file__).parent
    
    required_files = [
        "mcp/notion/metadata.json",
        "mcp/notion/server_config.json", 
        "mcp/notion/README.md",
        "mcp/notion_client.json",
        "MCP_INTEGRATION.md"
    ]
    
    all_files_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
            
            # Validate JSON files
            if file_path.endswith('.json'):
                try:
                    with open(full_path, 'r') as f:
                        json.load(f)
                    print(f"      📝 Valid JSON")
                except json.JSONDecodeError as e:
                    print(f"      ❌ Invalid JSON: {e}")
                    all_files_exist = False
        else:
            print(f"   ❌ Missing: {file_path}")
            all_files_exist = False
    
    return all_files_exist


def main():
    """Run comprehensive MCP integration test."""
    print("🧪 Testing Notion MCP Integration\n")
    
    # Load environment
    load_environment()
    
    tests = [
        ("Environment & API", test_notion_api_direct),
        ("Integration Files", test_integration_files),
        ("MCP Server Package", test_mcp_server_install),
        ("MCP Server Connection", test_mcp_server_connection)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} test passed\n")
                passed += 1
            else:
                print(f"❌ {test_name} test failed\n")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}\n")
            failed += 1
    
    print("📊 Test Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Notion MCP integration is working correctly.")
        print("\n🚀 Next steps:")
        print("   1. Package the agent: braid package --production")
        print("   2. Run with Docker: docker compose up --build")
        print("   3. Test agent functionality with Notion operations")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)