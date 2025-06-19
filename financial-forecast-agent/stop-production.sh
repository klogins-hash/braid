#!/bin/bash

echo "🛑 Stopping Production Financial Forecast Agent..."
echo "================================================"

# Stop and remove containers
docker-compose -f docker-compose.production.yml down

# Optional: Remove volumes (uncomment to clean data)
# docker-compose -f docker-compose.production.yml down -v

echo "✅ Production services stopped successfully!"
echo ""
echo "💡 To restart: ./deploy-production.sh"
echo "🗑️  To clean data: docker-compose -f docker-compose.production.yml down -v"
echo "📋 View containers: docker ps -a"