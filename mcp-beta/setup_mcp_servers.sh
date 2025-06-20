#!/bin/bash
# Setup MCP servers for this agent
# This is a lightweight version of the main setup script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MCP_SERVERS_DIR="mcp_servers"

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
}

# Function to check if we're in the main braid directory
check_main_setup() {
    local main_setup_script="../../scripts/setup_mcp_servers.sh"
    
    if [ -f "$main_setup_script" ]; then
        print_section "Main MCP Setup Available"
        print_status "Found main MCP setup script at $main_setup_script"
        
        read -p "Use main setup script instead? (recommended) (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            print_status "Running main MCP setup script..."
            cd ../..
            ./scripts/setup_mcp_servers.sh
            exit 0
        fi
    fi
}

# Function to setup MCP servers locally
setup_local_mcp() {
    print_section "Setting Up Local MCP Servers"
    
    # Create MCP servers directory
    mkdir -p "$MCP_SERVERS_DIR"
    cd "$MCP_SERVERS_DIR"
    
    
    # Clone and setup Xero MCP
    if [ ! -z "$XERO_ACCESS_TOKEN" ]; then
        print_status "Setting up Xero MCP..."
        if [ ! -d "xero" ]; then
            git clone https://github.com/XeroAPI/xero-mcp-server.git xero
        fi
        cd xero
        npm install >/dev/null 2>&1
        cd ..
        print_status "✅ Xero MCP ready"
    fi
    
    # Clone and setup Notion MCP
    if [ ! -z "$NOTION_API_KEY" ]; then
        print_status "Setting up Notion MCP..."
        if [ ! -d "notion" ]; then
            git clone https://github.com/makenotion/notion-mcp-server.git notion
        fi
        cd notion
        npm install >/dev/null 2>&1
        npm run build >/dev/null 2>&1
        cd ..
        print_status "✅ Notion MCP ready"
    fi
    
    cd ..
}

# Function to validate environment
validate_environment() {
    print_section "Validating Environment"
    
    # Load .env file if it exists
    if [ -f .env ]; then
        print_status "Loading .env file..."
        source .env
    else
        print_warning ".env file not found. Some MCP servers may not be available."
        print_warning "Copy .env.example to .env and configure your API keys."
    fi
    
    # Check for at least one MCP server configuration
    local mcp_count=0
    
    
    if [ ! -z "$XERO_ACCESS_TOKEN" ]; then
        print_status "✅ Xero access token found"
        ((mcp_count++))
    fi
    
    if [ ! -z "$NOTION_API_KEY" ]; then
        print_status "✅ Notion API key found"
        ((mcp_count++))
    fi
    
    if [ $mcp_count -eq 0 ]; then
        print_warning "No MCP API keys found. Agent will run with limited functionality."
    else
        print_status "Found configuration for $mcp_count MCP server(s)"
    fi
}

# Function to test setup
test_setup() {
    print_section "Testing Setup"
    
    if [ -f "test_agent.py" ]; then
        print_status "Running agent tests..."
        if python test_agent.py --test-mcp; then
            print_status "✅ MCP setup test passed"
        else
            print_warning "⚠️  MCP setup test had issues (this may be normal if API keys are not configured)"
        fi
    else
        print_warning "test_agent.py not found, skipping tests"
    fi
}

# Main function
main() {
    print_section "MCP Agent Setup"
    
    echo "This script will set up MCP servers for your agent."
    echo ""
    
    # Parse arguments
    local NO_TEST=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-test)
                NO_TEST=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_prerequisites
    check_main_setup  # Check if we should use main setup instead
    validate_environment
    setup_local_mcp
    
    if [ "$NO_TEST" = false ]; then
        test_setup
    fi
    
    print_section "Setup Complete!"
    
    echo -e "${GREEN}✅ MCP agent setup completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure your .env file with actual API keys"
    echo "  2. Test the agent: python test_agent.py"
    echo "  3. Run the agent: python agent.py"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"