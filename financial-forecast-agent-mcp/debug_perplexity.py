#!/usr/bin/env python3
"""
Debug Perplexity MCP server connection
"""

import os
import json
import subprocess
import time
from config import config

def debug_perplexity_mcp():
    """Debug why Perplexity MCP is failing"""
    print("🔍 Debugging Perplexity MCP Server")
    print("=" * 50)
    
    # Check if the server file exists
    server_path = "mcp_servers/perplexity/dist/index.js"
    print(f"📁 Server path: {server_path}")
    print(f"📁 File exists: {os.path.exists(server_path)}")
    
    if os.path.exists(server_path):
        # Check file size
        size = os.path.getsize(server_path)
        print(f"📁 File size: {size} bytes")
    
    # Check environment variable
    api_key = config.PERPLEXITY_API_KEY
    print(f"🔑 API Key set: {'Yes' if api_key else 'No'}")
    print(f"🔑 API Key length: {len(api_key) if api_key else 0}")
    
    # Check Node.js and try to run the server directly
    print(f"\n🟡 Attempting to start Perplexity MCP server...")
    
    try:
        env = os.environ.copy()
        env["PERPLEXITY_API_KEY"] = api_key
        
        cmd = ["node", server_path]
        print(f"🚀 Command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Process started successfully")
            
            # Try to send initialization
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "debug-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print(f"📤 Sending init request: {json.dumps(init_request)}")
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Try to read response with timeout
            import select
            ready, _, _ = select.select([process.stdout], [], [], 10.0)
            
            if ready:
                response = process.stdout.readline()
                print(f"📥 Response: {response.strip()}")
                
                if response.strip():
                    try:
                        data = json.loads(response)
                        print(f"✅ Valid JSON response: {data}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON response: {e}")
                        print(f"Raw response: {repr(response)}")
                else:
                    print("❌ Empty response")
            else:
                print("❌ No response within timeout")
            
            # Check stderr
            stderr_ready, _, _ = select.select([process.stderr], [], [], 1.0)
            if stderr_ready:
                stderr_output = process.stderr.read()
                if stderr_output:
                    print(f"🚨 Stderr: {stderr_output}")
                    
        else:
            # Process exited
            return_code = process.returncode
            stdout, stderr = process.communicate()
            print(f"❌ Process exited with code: {return_code}")
            print(f"📤 Stdout: {stdout}")
            print(f"🚨 Stderr: {stderr}")
        
        # Cleanup
        if process.poll() is None:
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

    # Also check the actual symlink
    print(f"\n🔗 Checking symlink...")
    if os.path.islink("mcp_servers/perplexity"):
        target = os.readlink("mcp_servers/perplexity")
        print(f"🔗 Symlink target: {target}")
        print(f"🔗 Target exists: {os.path.exists(target)}")
        
        # Check the actual target structure
        if os.path.exists(target):
            print(f"🔗 Contents of {target}:")
            try:
                contents = os.listdir(target)
                for item in contents[:10]:  # Show first 10 items
                    print(f"  - {item}")
            except Exception as e:
                print(f"  Error listing: {e}")

if __name__ == "__main__":
    debug_perplexity_mcp()