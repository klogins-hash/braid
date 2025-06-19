#!/bin/bash

echo "🚀 Deploying Financial Forecast Agent to Production"
echo "=================================================="

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ No .env file found. Please create ../.env with all required API keys"
    exit 1
fi

# Load environment variables
set -a
source ../.env
set +a

# Validate required environment variables
required_vars=("OPENAI_API_KEY" "XERO_ACCESS_TOKEN" "PERPLEXITY_API_KEY" "NOTION_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create production directories
mkdir -p logs data ssl monitoring nginx

# Build and start production services
echo "🐳 Building production containers..."
docker-compose -f docker-compose.production.yml build

echo "🚀 Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

echo "📊 Financial Forecast Agent:"
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "  Status: Starting up..."

echo "📈 Prometheus Monitoring:"
curl -s http://localhost:9090/-/healthy 2>/dev/null && echo "  Status: Healthy" || echo "  Status: Starting up..."

echo "🌐 Nginx Proxy:"
curl -s http://localhost:80/health | head -1 2>/dev/null && echo "  Status: Healthy" || echo "  Status: Starting up..."

echo ""
echo "✅ Production Deployment Complete!"
echo "=================================================="
echo "🔗 Service URLs:"
echo "   Agent API:      http://localhost:80"
echo "   Direct Agent:   http://localhost:8000"
echo "   Health Check:   http://localhost:80/health"
echo "   Monitoring:     http://localhost:9090"
echo "   Metrics:        http://localhost:80/metrics"
echo ""
echo "📊 View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "🛑 Stop services: ./stop-production.sh"
echo "📋 Status: docker-compose -f docker-compose.production.yml ps"