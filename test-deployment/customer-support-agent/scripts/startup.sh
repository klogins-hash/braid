#!/bin/bash
# Optimized startup script for Braid Agent with MCPs

set -e

echo "Starting Braid Agent with 2 MCPs..."
echo "Deployment Profile: production"

# Set environment variables
export LOG_LEVEL="info"
export MCP_TIMEOUT="60"
export RETRY_ATTEMPTS="5"

# Create necessary directories
mkdir -p data logs cache config monitoring

# Health monitoring setup
if [ "True" = "True" ]; then
    echo "Enabling health monitoring..."
    export HEALTH_MONITORING=true
    export HEALTH_CHECK_INTERVAL="30"
fi

# Parallel vs sequential startup
if [ "False" = "True" ]; then
    echo "Starting MCPs in parallel..."
    docker-compose up -d --build
else
    echo "Starting MCPs sequentially..."
    # Start MCPs in specified order
        docker-compose up -d twilio-mcp
    echo "Waiting for twilio to be ready..."
    sleep 10
    docker-compose up -d notion-mcp
    echo "Waiting for notion to be ready..."
    sleep 10
fi

# Wait for all services to be healthy
echo "Waiting for services to become healthy..."
python scripts/health_check.py --wait

echo "All services healthy. Agent ready!"
