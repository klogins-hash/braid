#!/bin/bash
# Automated MCP Server Setup Script
# Sets up and configures all MCP servers for a Braid agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MCP_SERVERS_DIR="mcp_servers"
SCRIPTS_DIR="scripts"
LOGS_DIR="logs/mcp"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment variables
validate_env_vars() {
    print_section "Validating Environment Variables"
    
    # Load .env file if it exists
    if [ -f .env ]; then
        print_status "Loading .env file..."
        source .env
    else
        print_warning ".env file not found. Creating template..."
        create_env_template
    fi
    
    # Check required variables
    local missing_vars=()
    
    # Core variables
    if [ -z "$OPENAI_API_KEY" ]; then
        missing_vars+=("OPENAI_API_KEY")
    fi
    
    # MCP-specific variables
    
    if [ -z "$XERO_ACCESS_TOKEN" ]; then
        missing_vars+=("XERO_ACCESS_TOKEN")
    fi
    
    if [ -z "$NOTION_API_KEY" ]; then
        missing_vars+=("NOTION_API_KEY")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please update your .env file and run again."
        exit 1
    fi
    
    print_status "All required environment variables found"
}

# Function to create .env template
create_env_template() {
    cat > .env << 'EOF'
# Core LLM API (Required)
OPENAI_API_KEY=your_openai_key_here

# LangSmith Tracing (Optional but recommended)
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your_project_name

# Xero MCP (Required for financial data)
XERO_ACCESS_TOKEN=your_xero_bearer_token_here
XERO_CLIENT_ID=your_xero_client_id_here
XERO_CLIENT_SECRET=your_xero_client_secret_here

# Notion MCP (Required for report generation)
NOTION_API_KEY=your_notion_integration_token_here

# MongoDB MCP (Optional)
MONGODB_CONNECTION_STRING=your_mongodb_connection_string

# AlphaVantage MCP (Optional)
ALPHAVANTAGE_API_KEY=your_alphavantage_key

# Twilio MCP (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_API_KEY=your_twilio_key
TWILIO_API_SECRET=your_twilio_secret
EOF
    
    print_status ".env template created. Please update with your actual API keys."
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    local node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_status "Node.js $(node --version) found"
    
    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm and try again."
        exit 1
    fi
    
    print_status "npm $(npm --version) found"
    
    # Check git
    if ! command_exists git; then
        print_error "git is not installed. Please install git and try again."
        exit 1
    fi
    
    print_status "git found"
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
    
    print_status "Python $(python3 --version) found"
}

# Function to setup directory structure
setup_directories() {
    print_section "Setting Up Directory Structure"
    
    # Create directories
    mkdir -p "$MCP_SERVERS_DIR"
    mkdir -p "$SCRIPTS_DIR"
    mkdir -p "$LOGS_DIR"
    
    print_status "Directory structure created"
}

# Function to clone MCP repositories
clone_mcp_repositories() {
    print_section "Cloning MCP Server Repositories"
    
    cd "$MCP_SERVERS_DIR"
    
    
    # Clone Xero MCP
    if [ ! -d "xero" ]; then
        print_status "Cloning Xero MCP..."
        git clone https://github.com/XeroAPI/xero-mcp-server.git xero
    else
        print_status "Xero MCP already exists, updating..."
        cd xero && git pull && cd ..
    fi
    
    # Clone Notion MCP
    if [ ! -d "notion" ]; then
        print_status "Cloning Notion MCP..."
        git clone https://github.com/makenotion/notion-mcp-server.git notion
    else
        print_status "Notion MCP already exists, updating..."
        cd notion && git pull && cd ..
    fi
    
    cd ..
    print_status "MCP repositories cloned/updated"
}

# Function to install dependencies
install_dependencies() {
    print_section "Installing MCP Server Dependencies"
    
    cd "$MCP_SERVERS_DIR"
    
    
    # Install Xero MCP dependencies
    print_status "Installing Xero MCP dependencies..."
    cd xero
    npm install > ../logs/mcp/xero_install.log 2>&1
    if [ $? -eq 0 ]; then
        print_status "Xero MCP dependencies installed"
    else
        print_error "Failed to install Xero MCP dependencies. Check logs/mcp/xero_install.log"
    fi
    cd ..
    
    # Install Notion MCP dependencies
    print_status "Installing Notion MCP dependencies..."
    cd notion
    npm install > ../logs/mcp/notion_install.log 2>&1
    npm run build > ../logs/mcp/notion_build.log 2>&1
    if [ $? -eq 0 ]; then
        print_status "Notion MCP dependencies installed and built"
    else
        print_error "Failed to install/build Notion MCP dependencies. Check logs/mcp/notion_*.log"
    fi
    cd ..
    
    cd ..
    print_status "All MCP server dependencies installed"
}

# Function to generate startup scripts
generate_startup_scripts() {
    print_section "Generating MCP Server Startup Scripts"
    
    # Generate individual server scripts
    generate_xero_script
    generate_notion_script
    generate_master_script
    generate_stop_script
    
    # Make scripts executable
    chmod +x "$SCRIPTS_DIR"/*.sh
    
    print_status "Startup scripts generated and made executable"
}

# Generate Xero startup script
generate_xero_script() {
    cat > "$SCRIPTS_DIR/start_xero_mcp.sh" << 'EOF'
#!/bin/bash
# Start Xero MCP Server

echo "💰 Starting Xero MCP Server..."

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Check for required variables
if [ -z "$XERO_ACCESS_TOKEN" ]; then
    echo "❌ XERO_ACCESS_TOKEN not set"
    exit 1
fi

# Start server
cd mcp_servers/xero
XERO_CLIENT_BEARER_TOKEN=$XERO_ACCESS_TOKEN \
XERO_CLIENT_ID=$XERO_CLIENT_ID \
XERO_CLIENT_SECRET=$XERO_CLIENT_SECRET \
node dist/index.js 2>&1 | tee ../../logs/mcp/xero.log &
PID=$!
echo $PID > ../../logs/mcp/xero.pid
echo "✅ Xero MCP started with PID: $PID"
EOF
}

# Generate Notion startup script
generate_notion_script() {
    cat > "$SCRIPTS_DIR/start_notion_mcp.sh" << 'EOF'
#!/bin/bash
# Start Notion MCP Server

echo "📝 Starting Notion MCP Server..."

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Check for API key
if [ -z "$NOTION_API_KEY" ]; then
    echo "❌ NOTION_API_KEY not set"
    exit 1
fi

# Start server
cd mcp_servers/notion
NOTION_API_KEY=$NOTION_API_KEY node bin/cli.mjs 2>&1 | tee ../../logs/mcp/notion.log &
PID=$!
echo $PID > ../../logs/mcp/notion.pid
echo "✅ Notion MCP started with PID: $PID"
EOF
}

# Generate master startup script
generate_master_script() {
    cat > "$SCRIPTS_DIR/start_all_mcp_servers.sh" << 'EOF'
#!/bin/bash
# Start All MCP Servers

echo "🚀 Starting All MCP Servers..."

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found"
    exit 1
fi

# Create logs directory
mkdir -p logs/mcp

# Start servers based on available API keys
STARTED_SERVERS=()

if [ ! -z "$XERO_ACCESS_TOKEN" ]; then
    ./scripts/start_xero_mcp.sh
    STARTED_SERVERS+=("xero")
    sleep 2
fi

if [ ! -z "$NOTION_API_KEY" ]; then
    ./scripts/start_notion_mcp.sh
    STARTED_SERVERS+=("notion")
    sleep 2
fi

echo "✅ Started ${#STARTED_SERVERS[@]} MCP servers: ${STARTED_SERVERS[*]}"
echo "📊 Server logs available in logs/mcp/"
echo "🛑 To stop all servers: ./scripts/stop_all_mcp_servers.sh"

# Wait a moment for servers to fully start
sleep 5

# Test connections
echo "🧪 Testing MCP server connections..."
if command -v python3 >/dev/null 2>&1; then
    if [ -f test_mcp_connections.py ]; then
        python3 test_mcp_connections.py --quick
    else
        echo "ℹ️  test_mcp_connections.py not found - skipping connection test"
    fi
else
    echo "ℹ️  Python 3 not found - skipping connection test"
fi

echo "✅ MCP servers startup complete!"
EOF
}

# Generate stop script
generate_stop_script() {
    cat > "$SCRIPTS_DIR/stop_all_mcp_servers.sh" << 'EOF'
#!/bin/bash
# Stop All MCP Servers

echo "🛑 Stopping All MCP Servers..."

# Function to stop server by PID file
stop_server() {
    local service=$1
    local pid_file="logs/mcp/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $service MCP (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $service MCP..."
                kill -9 "$pid"
            fi
        fi
        rm -f "$pid_file"
        echo "✅ $service MCP stopped"
    else
        echo "ℹ️  No PID file found for $service MCP"
    fi
}

# Stop individual servers
stop_server "xero"
stop_server "notion"

# Kill any remaining node processes that might be MCP servers
echo "🧹 Cleaning up any remaining MCP processes..."
pkill -f "xero.*dist/index.js" 2>/dev/null || true
pkill -f "notion.*bin/cli.mjs" 2>/dev/null || true

echo "✅ All MCP servers stopped"
EOF
}

# Function to generate test script
generate_test_script() {
    print_section "Generating MCP Connection Test Script"
    
    cat > test_mcp_connections.py << 'EOF'
#!/usr/bin/env python3
"""
MCP Connection Test Script
Tests connectivity to all configured MCP servers
"""

import subprocess
import json
import os
import sys
import argparse
from typing import Dict, Any

class MCPConnectionTester:
    def __init__(self):
        self.load_env_vars()
    
    def load_env_vars(self):
        """Load environment variables from .env file if it exists."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # dotenv not available, rely on system environment
            pass
    
    def test_server_connection(self, server_name: str, server_path: str, env_vars: dict) -> bool:
        """Test connection to a single MCP server."""
        print(f"\n🧪 Testing {server_name} MCP Server...")
        
        try:
            # Start the server process
            env = os.environ.copy()
            env.update(env_vars)
            
            process = subprocess.Popen(
                ['node', server_path],
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
                        "name": "mcp-connection-tester",
                        "version": "1.0.0"
                    }
                }
            }
            
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    print(f"✅ {server_name} MCP: Connection successful")
                    
                    # Get tools list if possible
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    process.stdin.write(json.dumps(tools_request) + "\n")
                    process.stdin.flush()
                    
                    tools_response_line = process.stdout.readline()
                    if tools_response_line:
                        tools_response = json.loads(tools_response_line)
                        if "result" in tools_response:
                            tools = tools_response["result"].get("tools", [])
                            print(f"   📊 Available tools: {len(tools)}")
                        
                    process.terminate()
                    return True
                else:
                    print(f"❌ {server_name} MCP: Initialization failed - {response}")
            else:
                print(f"❌ {server_name} MCP: No response received")
            
            process.terminate()
            return False
            
        except Exception as e:
            print(f"❌ {server_name} MCP: Connection failed - {e}")
            return False
    
    def test_all_servers(self, quick: bool = False) -> Dict[str, bool]:
        """Test all configured MCP servers."""
        print("🧪 Testing MCP Server Connections")
        print("=" * 50)
        
        results = {}
        
        
        # Test Xero MCP
        if os.getenv('XERO_ACCESS_TOKEN'):
            results['xero'] = self.test_server_connection(
                "Xero",
                "mcp_servers/xero/dist/index.js",
                {
                    "XERO_CLIENT_BEARER_TOKEN": os.getenv('XERO_ACCESS_TOKEN'),
                    "XERO_CLIENT_ID": os.getenv('XERO_CLIENT_ID', ''),
                    "XERO_CLIENT_SECRET": os.getenv('XERO_CLIENT_SECRET', '')
                }
            )
        else:
            print("\n⏭️  Skipping Xero MCP (no access token)")
            results['xero'] = None
        
        # Test Notion MCP
        if os.getenv('NOTION_API_KEY'):
            results['notion'] = self.test_server_connection(
                "Notion",
                "mcp_servers/notion/bin/cli.mjs",
                {"NOTION_API_KEY": os.getenv('NOTION_API_KEY')}
            )
        else:
            print("\n⏭️  Skipping Notion MCP (no API key)")
            results['notion'] = None
        
        # Print summary
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        working_count = 0
        total_tested = 0
        
        for server, result in results.items():
            if result is not None:
                total_tested += 1
                if result:
                    working_count += 1
                    print(f"✅ {server.title()} MCP: Working")
                else:
                    print(f"❌ {server.title()} MCP: Failed")
            else:
                print(f"⏭️  {server.title()} MCP: Skipped (no credentials)")
        
        print(f"\n🎯 {working_count}/{total_tested} MCP servers working")
        
        if working_count == total_tested and total_tested > 0:
            print("🎉 All configured MCP servers are working!")
        elif working_count > 0:
            print("⚠️  Some MCP servers are working, but not all")
        else:
            print("❌ No MCP servers are working")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Test MCP server connections')
    parser.add_argument('--quick', action='store_true', help='Quick test mode')
    parser.add_argument('--server', help='Test specific server only')
    args = parser.parse_args()
    
    tester = MCPConnectionTester()
    
    if args.server:
        # Test specific server only
        print(f"🧪 Testing {args.server} MCP server only...")
        # Implementation for specific server testing
    else:
        # Test all servers
        results = tester.test_all_servers(quick=args.quick)
        
        # Exit with appropriate code
        working_servers = sum(1 for r in results.values() if r is True)
        total_tested = sum(1 for r in results.values() if r is not None)
        
        if working_servers == total_tested and total_tested > 0:
            sys.exit(0)  # All good
        else:
            sys.exit(1)  # Some failures

if __name__ == "__main__":
    main()
EOF
    
    chmod +x test_mcp_connections.py
    print_status "MCP connection test script generated"
}

# Function to test MCP servers
test_mcp_servers() {
    print_section "Testing MCP Server Setup"
    
    # Generate test script if it doesn't exist
    if [ ! -f test_mcp_connections.py ]; then
        generate_test_script
    fi
    
    # Start servers for testing
    print_status "Starting MCP servers for testing..."
    ./scripts/start_all_mcp_servers.sh &
    
    # Wait for servers to start
    sleep 10
    
    # Run tests
    print_status "Running connection tests..."
    python3 test_mcp_connections.py --quick
    
    # Stop test servers
    print_status "Stopping test servers..."
    ./scripts/stop_all_mcp_servers.sh
}

# Main setup function
main() {
    print_section "Automated MCP Server Setup"
    
    echo "This script will set up MCP servers for your Braid agent."
    echo "It will:"
    echo "  1. Validate prerequisites and environment variables"
    echo "  2. Clone MCP server repositories"
    echo "  3. Install dependencies"
    echo "  4. Generate startup scripts"
    echo "  5. Test the setup"
    echo ""
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    
    # Run setup steps
    check_prerequisites
    validate_env_vars
    setup_directories
    clone_mcp_repositories
    install_dependencies
    generate_startup_scripts
    generate_test_script
    
    print_section "Setup Complete!"
    
    echo -e "${GREEN}✅ MCP server setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Update your .env file with actual API keys if needed"
    echo "  2. Start all MCP servers: ./scripts/start_all_mcp_servers.sh"
    echo "  3. Test connections: python3 test_mcp_connections.py"
    echo "  4. Integrate MCP clients into your agent code"
    echo ""
    echo "Documentation:"
    echo "  - MCP Setup Guide: docs/guides/mcp-integration/MCP_SETUP_GUIDE.md"
    echo "  - Server logs: logs/mcp/"
    echo "  - Stop servers: ./scripts/stop_all_mcp_servers.sh"
    
    # Ask if user wants to test now
    echo ""
    read -p "Run connection test now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_mcp_servers
    fi
}

# Run main function
main "$@"