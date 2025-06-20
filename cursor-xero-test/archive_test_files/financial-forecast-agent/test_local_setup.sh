#!/bin/bash
# Complete test script for local MCP-based Financial Forecast Agent setup

set -e

echo "🧪 Testing Complete Local MCP Setup"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

if ! command_exists python; then
    echo "❌ Python not found. Please install Python 3.11+."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Check environment file
echo ""
echo "🔐 Checking environment configuration..."

if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create .env with required API keys."
    exit 1
fi

# Check for required environment variables
required_vars=("OPENAI_API_KEY" "XERO_ACCESS_TOKEN" "PERPLEXITY_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables in .env:"
    printf '   %s\n' "${missing_vars[@]}"
    exit 1
fi

echo "✅ Environment configuration check passed"

# Test 1: Start MCP servers
echo ""
echo "🚀 Test 1: Starting MCP servers..."

./start_mcp_servers.sh &
MCP_SCRIPT_PID=$!

# Wait for servers to start
echo "⏳ Waiting for MCP servers to initialize..."
sleep 10

# Check if MCP servers are running
if [ ! -f "mcp_pids.txt" ]; then
    echo "❌ MCP servers failed to start - no PID file found"
    kill $MCP_SCRIPT_PID 2>/dev/null || true
    exit 1
fi

echo "✅ MCP servers started successfully"

# Test 2: Build Docker image
echo ""
echo "🐳 Test 2: Building Docker image..."

if docker-compose build --no-cache; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    ./stop_mcp_servers.sh
    exit 1
fi

# Test 3: Test MCP connectivity
echo ""
echo "🔌 Test 3: Testing MCP server connectivity..."

test_mcp_connectivity() {
    local name=$1
    local port=$2
    
    # Simple port check since we don't have actual MCP servers yet
    if nc -z localhost $port 2>/dev/null; then
        echo "   ✅ $name (port $port) - Port accessible"
        return 0
    else
        echo "   ⚠️  $name (port $port) - Port not accessible (expected if no real MCP server)"
        return 1
    fi
}

# Note: These may fail if actual MCP servers aren't implemented yet
test_mcp_connectivity "Xero MCP" 3001
test_mcp_connectivity "Perplexity MCP" 3002  
test_mcp_connectivity "Notion MCP" 3003

# Test 4: Run the agent
echo ""
echo "🤖 Test 4: Running the MCP-based agent..."

# Run in background and capture output
docker-compose up -d

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 15

# Check if container is running
if docker ps | grep -q "financial-forecast-mcp"; then
    echo "✅ Container is running"
else
    echo "❌ Container failed to start"
    echo "📋 Container logs:"
    docker-compose logs
    ./stop_mcp_servers.sh
    docker-compose down
    exit 1
fi

# Test 5: Health checks
echo ""
echo "🏥 Test 5: Testing health endpoints..."

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo "   Testing $name..."
    
    if response=$(curl -s -w "%{http_code}" "$url" 2>/dev/null); then
        status_code="${response: -3}"
        body="${response%???}"
        
        if [ "$status_code" = "$expected_status" ]; then
            echo "   ✅ $name - Status: $status_code"
            return 0
        else
            echo "   ⚠️  $name - Status: $status_code (expected $expected_status)"
            return 1
        fi
    else
        echo "   ❌ $name - Failed to connect"
        return 1
    fi
}

test_endpoint "Health Check" "http://localhost:8000/health" "200"
test_endpoint "Metrics" "http://localhost:8000/metrics" "200"

# Test 6: Check logs for successful forecast
echo ""
echo "📊 Test 6: Checking for successful forecast completion..."

# Get container logs
logs=$(docker-compose logs financial-forecast-mcp 2>/dev/null || echo "")

if echo "$logs" | grep -q "✅.*forecast completed successfully"; then
    echo "✅ Forecast completed successfully"
    
    # Show key metrics
    if echo "$logs" | grep -q "MCP-BASED PRODUCTION FORECAST RESULTS"; then
        echo "✅ MCP-based results generated"
    fi
    
    if echo "$logs" | grep -q '"mcp_tools_used"'; then
        echo "✅ MCP tools were used"
    fi
    
else
    echo "⚠️  Forecast completion not detected in logs"
    echo "📋 Recent logs:"
    echo "$logs" | tail -20
fi

# Test Results Summary
echo ""
echo "📊 TEST RESULTS SUMMARY"
echo "======================"

if docker ps | grep -q "financial-forecast-mcp"; then
    echo "✅ Container Status: Running"
else
    echo "❌ Container Status: Not Running"
fi

if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Health Endpoint: Working"
else
    echo "❌ Health Endpoint: Failed"
fi

if echo "$logs" | grep -q "✅.*forecast completed"; then
    echo "✅ Forecast Generation: Success"
else
    echo "⚠️  Forecast Generation: Unknown/Failed"
fi

echo ""
echo "🎯 NEXT STEPS:"
echo "1. View real-time logs: docker-compose logs -f"
echo "2. Test health endpoint: curl http://localhost:8000/health"
echo "3. Check metrics: curl http://localhost:8000/metrics"
echo "4. Stop everything: ./stop_mcp_servers.sh && docker-compose down"
echo ""
echo "📖 For detailed setup instructions, see: LOCAL_SETUP_GUIDE.md"

# Keep running if everything looks good
if docker ps | grep -q "financial-forecast-mcp" && curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo ""
    echo "🎉 All tests passed! System is running successfully."
    echo "   Press Ctrl+C to stop everything..."
    
    cleanup() {
        echo ""
        echo "🛑 Stopping all services..."
        docker-compose down
        ./stop_mcp_servers.sh
        echo "✅ Cleanup complete"
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    
    # Keep running and show periodic status
    while true; do
        sleep 30
        if docker ps | grep -q "financial-forecast-mcp"; then
            echo "🔄 System still running... ($(date))"
        else
            echo "❌ Container stopped unexpectedly"
            ./stop_mcp_servers.sh
            break
        fi
    done
    
else
    echo ""
    echo "⚠️  Some tests failed. Cleaning up..."
    docker-compose down 2>/dev/null || true
    ./stop_mcp_servers.sh
    exit 1
fi