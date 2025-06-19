#!/usr/bin/env python3
# Health check script for Braid Agent and MCPs

import requests
import time
import sys
import argparse
import json
from typing import Dict, List

def check_service_health(service_name: str, url: str, timeout: int = 10) -> Dict[str, any]:
    """Check health of a single service."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return {
                "service": service_name,
                "status": "healthy", 
                "response_time": response.elapsed.total_seconds(),
                "details": response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            }
        else:
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Health check for Braid Agent')
    parser.add_argument('--wait', action='store_true', help='Wait for all services to become healthy')
    parser.add_argument('--timeout', type=int, default=300, help='Maximum wait time in seconds')
    args = parser.parse_args()
    
    services = {
        "agent": "http://localhost:8000/health",
        "notion": "http://notion-mcp-server:3000/health", "twilio": "http://twilio-mcp-server:3000/health"
    }
    
    start_time = time.time()
    
    while True:
        all_healthy = True
        results = {}
        
        for service_name, health_url in services.items():
            result = check_service_health(service_name, health_url)
            results[service_name] = result
            
            if result["status"] != "healthy":
                all_healthy = False
        
        # Print results
        print(json.dumps(results, indent=2))
        
        if all_healthy:
            print("All services are healthy!")
            sys.exit(0)
        
        if not args.wait:
            print("Some services are unhealthy.")
            sys.exit(1)
        
        if time.time() - start_time > args.timeout:
            print(f"Timeout waiting for services to become healthy after {args.timeout}s")
            sys.exit(1)
        
        print("Waiting for services to become healthy...")
        time.sleep(5)

if __name__ == "__main__":
    main()
