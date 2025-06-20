"""
MCP Deployment Optimization and Workflow Enhancement
Provides optimized packaging, deployment strategies, and performance tuning for MCP integrations.
"""

import json
import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeploymentProfile:
    """Deployment profile configuration."""
    name: str
    description: str
    docker_optimization: bool
    parallel_startup: bool
    health_monitoring: bool
    resource_limits: Dict[str, Any]
    startup_order: List[str]
    environment_config: Dict[str, str]


class MCPDeploymentOptimizer:
    """Optimizes MCP deployment for different environments and use cases."""
    
    def __init__(self):
        """Initialize deployment optimizer."""
        self.deployment_profiles = {
            "development": DeploymentProfile(
                name="development",
                description="Fast startup, minimal resource usage, detailed logging",
                docker_optimization=False,
                parallel_startup=True,
                health_monitoring=False,
                resource_limits={
                    "memory": "512m",
                    "cpu": "0.5"
                },
                startup_order=[],
                environment_config={
                    "LOG_LEVEL": "debug",
                    "MCP_TIMEOUT": "30",
                    "RETRY_ATTEMPTS": "2"
                }
            ),
            "production": DeploymentProfile(
                name="production",
                description="High reliability, performance optimization, monitoring",
                docker_optimization=True,
                parallel_startup=False,
                health_monitoring=True,
                resource_limits={
                    "memory": "1g",
                    "cpu": "1.0"
                },
                startup_order=["data", "communication", "productivity", "development", "finance"],
                environment_config={
                    "LOG_LEVEL": "info",
                    "MCP_TIMEOUT": "60",
                    "RETRY_ATTEMPTS": "5",
                    "HEALTH_CHECK_INTERVAL": "30"
                }
            ),
            "high_performance": DeploymentProfile(
                name="high_performance",
                description="Maximum performance, resource allocation, parallel processing",
                docker_optimization=True,
                parallel_startup=True,
                health_monitoring=True,
                resource_limits={
                    "memory": "2g",
                    "cpu": "2.0"
                },
                startup_order=[],
                environment_config={
                    "LOG_LEVEL": "warn",
                    "MCP_TIMEOUT": "120",
                    "RETRY_ATTEMPTS": "3",
                    "PARALLEL_REQUESTS": "10"
                }
            )
        }
    
    def optimize_agent_structure(
        self,
        agent_path: Path,
        mcps: List[str],
        profile: str = "production"
    ) -> Dict[str, Any]:
        """Optimize agent structure for deployment.
        
        Args:
            agent_path: Path to agent directory
            mcps: List of MCP IDs to integrate
            profile: Deployment profile name
            
        Returns:
            Optimization results
        """
        deployment_profile = self.deployment_profiles.get(profile)
        if not deployment_profile:
            raise ValueError(f"Unknown deployment profile: {profile}")
        
        results = {
            "profile": profile,
            "optimizations_applied": [],
            "files_created": [],
            "performance_improvements": []
        }
        
        # Create optimized directory structure
        self._create_optimized_structure(agent_path, results)
        
        # Generate optimized Docker configurations
        if deployment_profile.docker_optimization:
            self._optimize_docker_configs(agent_path, mcps, deployment_profile, results)
        
        # Create startup orchestration
        self._create_startup_orchestration(agent_path, mcps, deployment_profile, results)
        
        # Generate environment optimization
        self._optimize_environment_config(agent_path, deployment_profile, results)
        
        # Create monitoring configuration
        if deployment_profile.health_monitoring:
            self._create_monitoring_config(agent_path, mcps, results)
        
        # Generate performance tuning configuration
        self._create_performance_config(agent_path, deployment_profile, results)
        
        return results
    
    def _create_optimized_structure(self, agent_path: Path, results: Dict[str, Any]):
        """Create optimized directory structure."""
        directories = [
            "config",
            "logs",
            "data",
            "cache",
            "scripts",
            "monitoring"
        ]
        
        for directory in directories:
            dir_path = agent_path / directory
            dir_path.mkdir(exist_ok=True)
            results["files_created"].append(str(dir_path))
        
        results["optimizations_applied"].append("optimized_directory_structure")
    
    def _optimize_docker_configs(
        self,
        agent_path: Path,
        mcps: List[str],
        profile: DeploymentProfile,
        results: Dict[str, Any]
    ):
        """Generate optimized Docker configurations."""
        
        # Enhanced docker-compose.yml with optimization
        docker_compose_content = self._generate_optimized_docker_compose(mcps, profile)
        
        docker_compose_path = agent_path / "docker-compose.yml"
        with open(docker_compose_path, 'w') as f:
            f.write(docker_compose_content)
        
        results["files_created"].append(str(docker_compose_path))
        
        # Production Dockerfile with multi-stage build
        dockerfile_content = self._generate_optimized_dockerfile(profile)
        
        dockerfile_path = agent_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        results["files_created"].append(str(dockerfile_path))
        results["optimizations_applied"].append("optimized_docker_configuration")
        results["performance_improvements"].append("multi_stage_docker_build")
    
    def _generate_optimized_docker_compose(
        self,
        mcps: List[str],
        profile: DeploymentProfile
    ) -> str:
        """Generate optimized docker-compose configuration."""
        
        compose_config = {
            "version": "3.8",
            "services": {},
            "networks": {
                "mcp_network": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [{"subnet": "172.20.0.0/16"}]
                    }
                }
            },
            "volumes": {}
        }
        
        # Add agent service
        compose_config["services"]["agent"] = {
            "build": {
                "context": ".",
                "dockerfile": "Dockerfile",
                "target": "production"
            },
            "container_name": "braid-agent",
            "restart": "unless-stopped",
            "environment": profile.environment_config,
            "networks": ["mcp_network"],
            "ports": ["8000:8000"],
            "volumes": [
                "./data:/app/data",
                "./logs:/app/logs",
                "./cache:/app/cache"
            ],
            "depends_on": {},
            "healthcheck": {
                "test": ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            }
        }
        
        if profile.resource_limits:
            compose_config["services"]["agent"]["deploy"] = {
                "resources": {
                    "limits": profile.resource_limits,
                    "reservations": {
                        "memory": "256m",
                        "cpu": "0.25"
                    }
                }
            }
        
        # Add MCP services based on requirements
        for mcp_id in mcps:
            mcp_config = self._get_mcp_docker_config(mcp_id, profile)
            if mcp_config:
                compose_config["services"][f"{mcp_id}-mcp"] = mcp_config
                compose_config["services"]["agent"]["depends_on"][f"{mcp_id}-mcp"] = {
                    "condition": "service_healthy"
                }
        
        # Add volumes for persistent data
        for mcp_id in mcps:
            compose_config["volumes"][f"{mcp_id}_data"] = None
            compose_config["volumes"][f"{mcp_id}_cache"] = None
        
        return self._dict_to_yaml(compose_config)
    
    def _get_mcp_docker_config(self, mcp_id: str, profile: DeploymentProfile) -> Optional[Dict[str, Any]]:
        """Get Docker configuration for a specific MCP."""
        # This would be loaded from MCP metadata
        # For now, return a basic configuration for Docker-required MCPs
        
        docker_mcps = ["notion", "agentql", "alphavantage", "perplexity", "mongodb"]
        
        if mcp_id not in docker_mcps:
            return None
        
        config = {
            "image": f"braid-mcp-{mcp_id}:latest",
            "container_name": f"{mcp_id}-mcp-server",
            "restart": "unless-stopped",
            "networks": ["mcp_network"],
            "environment": profile.environment_config.copy(),
            "volumes": [
                f"{mcp_id}_data:/app/data",
                f"{mcp_id}_cache:/app/cache"
            ],
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:3000/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "45s"
            }
        }
        
        if profile.resource_limits:
            config["deploy"] = {
                "resources": {
                    "limits": {
                        "memory": "512m",
                        "cpu": "0.5"
                    }
                }
            }
        
        return config
    
    def _generate_optimized_dockerfile(self, profile: DeploymentProfile) -> str:
        """Generate optimized Dockerfile for agent."""
        return f"""# Multi-stage optimized Dockerfile for Braid Agent
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1001 agent

# Stage 1: Dependencies
FROM base as dependencies
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM base as production
WORKDIR /app

# Copy installed packages from dependencies stage
COPY --from=dependencies /root/.local /home/agent/.local
ENV PATH=/home/agent/.local/bin:$PATH

# Copy application code
COPY --chown=agent:agent . .

# Set up directories
RUN mkdir -p data logs cache config monitoring \\
    && chown -R agent:agent /app

# Switch to non-root user
USER agent

# Environment configuration
ENV PYTHONPATH=/app
ENV LOG_LEVEL={profile.environment_config.get('LOG_LEVEL', 'info')}
ENV MCP_TIMEOUT={profile.environment_config.get('MCP_TIMEOUT', '60')}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "agent.py"]
"""
    
    def _create_startup_orchestration(
        self,
        agent_path: Path,
        mcps: List[str],
        profile: DeploymentProfile,
        results: Dict[str, Any]
    ):
        """Create startup orchestration scripts."""
        
        # Create startup script
        startup_script_content = self._generate_startup_script(mcps, profile)
        
        startup_script_path = agent_path / "scripts" / "startup.sh"
        with open(startup_script_path, 'w') as f:
            f.write(startup_script_content)
        
        startup_script_path.chmod(0o755)  # Make executable
        results["files_created"].append(str(startup_script_path))
        
        # Create health check script
        health_check_content = self._generate_health_check_script(mcps)
        
        health_check_path = agent_path / "scripts" / "health_check.py"
        with open(health_check_path, 'w') as f:
            f.write(health_check_content)
        
        results["files_created"].append(str(health_check_path))
        results["optimizations_applied"].append("startup_orchestration")
    
    def _generate_startup_script(self, mcps: List[str], profile: DeploymentProfile) -> str:
        """Generate optimized startup script."""
        return f"""#!/bin/bash
# Optimized startup script for Braid Agent with MCPs

set -e

echo "Starting Braid Agent with {len(mcps)} MCPs..."
echo "Deployment Profile: {profile.name}"

# Set environment variables
export LOG_LEVEL="{profile.environment_config.get('LOG_LEVEL', 'info')}"
export MCP_TIMEOUT="{profile.environment_config.get('MCP_TIMEOUT', '60')}"
export RETRY_ATTEMPTS="{profile.environment_config.get('RETRY_ATTEMPTS', '3')}"

# Create necessary directories
mkdir -p data logs cache config monitoring

# Health monitoring setup
if [ "{profile.health_monitoring}" = "True" ]; then
    echo "Enabling health monitoring..."
    export HEALTH_MONITORING=true
    export HEALTH_CHECK_INTERVAL="{profile.environment_config.get('HEALTH_CHECK_INTERVAL', '30')}"
fi

# Parallel vs sequential startup
if [ "{profile.parallel_startup}" = "True" ]; then
    echo "Starting MCPs in parallel..."
    docker-compose up -d --build
else
    echo "Starting MCPs sequentially..."
    # Start MCPs in specified order
    {self._generate_sequential_startup(mcps, profile.startup_order)}
fi

# Wait for all services to be healthy
echo "Waiting for services to become healthy..."
python scripts/health_check.py --wait

echo "All services healthy. Agent ready!"
"""
    
    def _generate_sequential_startup(self, mcps: List[str], startup_order: List[str]) -> str:
        """Generate sequential startup commands."""
        ordered_mcps = []
        
        # Add MCPs in specified category order
        for category in startup_order:
            ordered_mcps.extend([mcp for mcp in mcps if self._get_mcp_category(mcp) == category])
        
        # Add any remaining MCPs
        ordered_mcps.extend([mcp for mcp in mcps if mcp not in ordered_mcps])
        
        commands = []
        for mcp in ordered_mcps:
            commands.append(f'    docker-compose up -d {mcp}-mcp')
            commands.append(f'    echo "Waiting for {mcp} to be ready..."')
            commands.append(f'    sleep 10')
        
        return '\n'.join(commands)
    
    def _get_mcp_category(self, mcp_id: str) -> str:
        """Get category for an MCP (would normally query registry)."""
        category_mapping = {
            "notion": "productivity",
            "agentql": "development", 
            "alphavantage": "finance",
            "perplexity": "data",
            "mongodb": "data",
            "twilio": "communication"
        }
        return category_mapping.get(mcp_id, "unknown")
    
    def _create_monitoring_config(
        self,
        agent_path: Path,
        mcps: List[str],
        results: Dict[str, Any]
    ):
        """Create monitoring configuration."""
        
        monitoring_config = {
            "health_monitoring": {
                "enabled": True,
                "check_interval": 30,
                "timeout": 10,
                "retry_attempts": 3
            },
            "mcps": {
                mcp_id: {
                    "health_endpoint": f"http://{mcp_id}-mcp-server:3000/health",
                    "metrics_endpoint": f"http://{mcp_id}-mcp-server:3000/metrics"
                }
                for mcp_id in mcps
            },
            "alerting": {
                "slack_webhook": None,
                "email_notifications": False,
                "severity_threshold": "medium"
            },
            "logging": {
                "level": "info",
                "file": "/app/logs/monitoring.log",
                "max_size": "100MB",
                "backup_count": 5
            }
        }
        
        monitoring_path = agent_path / "config" / "monitoring.json"
        with open(monitoring_path, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        results["files_created"].append(str(monitoring_path))
        results["optimizations_applied"].append("health_monitoring_config")
    
    def _create_performance_config(
        self,
        agent_path: Path,
        profile: DeploymentProfile,
        results: Dict[str, Any]
    ):
        """Create performance tuning configuration."""
        
        performance_config = {
            "profile": profile.name,
            "resource_limits": profile.resource_limits,
            "optimization": {
                "parallel_processing": profile.parallel_startup,
                "connection_pooling": True,
                "request_batching": True,
                "caching_enabled": True,
                "compression": True
            },
            "timeouts": {
                "mcp_connection": int(profile.environment_config.get('MCP_TIMEOUT', '60')),
                "tool_execution": 120,
                "health_check": 10
            },
            "retry_policy": {
                "max_attempts": int(profile.environment_config.get('RETRY_ATTEMPTS', '3')),
                "backoff_strategy": "exponential",
                "base_delay": 1.0,
                "max_delay": 60.0
            },
            "scaling": {
                "auto_scaling": False,
                "min_replicas": 1,
                "max_replicas": 3,
                "cpu_threshold": 80,
                "memory_threshold": 85
            }
        }
        
        performance_path = agent_path / "config" / "performance.json"
        with open(performance_path, 'w') as f:
            json.dump(performance_config, f, indent=2)
        
        results["files_created"].append(str(performance_path))
        results["optimizations_applied"].append("performance_tuning_config")
        results["performance_improvements"].extend([
            "connection_pooling",
            "request_batching", 
            "caching_optimization"
        ])
    
    def _optimize_environment_config(
        self,
        agent_path: Path,
        profile: DeploymentProfile,
        results: Dict[str, Any]
    ):
        """Optimize environment configuration."""
        
        env_content = f"""# Optimized Environment Configuration
# Profile: {profile.name}

# Logging Configuration
LOG_LEVEL={profile.environment_config.get('LOG_LEVEL', 'info')}
LOG_FORMAT=json
LOG_FILE=/app/logs/agent.log

# MCP Configuration
MCP_TIMEOUT={profile.environment_config.get('MCP_TIMEOUT', '60')}
RETRY_ATTEMPTS={profile.environment_config.get('RETRY_ATTEMPTS', '3')}
CONNECTION_POOL_SIZE=10
MAX_CONCURRENT_REQUESTS=5

# Performance Optimization
ENABLE_CACHING=true
CACHE_TTL=3600
ENABLE_COMPRESSION=true
PARALLEL_PROCESSING={"true" if profile.parallel_startup else "false"}

# Health Monitoring
HEALTH_MONITORING={"true" if profile.health_monitoring else "false"}
HEALTH_CHECK_INTERVAL={profile.environment_config.get('HEALTH_CHECK_INTERVAL', '30')}
METRICS_COLLECTION=true

# Security
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=100
CORS_ENABLED=false

# Docker Optimization
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
"""
        
        env_path = agent_path / ".env.production"
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        results["files_created"].append(str(env_path))
        results["optimizations_applied"].append("environment_optimization")
    
    def _generate_health_check_script(self, mcps: List[str]) -> str:
        """Generate health check script."""
        return f"""#!/usr/bin/env python3
# Health check script for Braid Agent and MCPs

import requests
import time
import sys
import argparse
import json
from typing import Dict, List

def check_service_health(service_name: str, url: str, timeout: int = 10) -> Dict[str, any]:
    \"\"\"Check health of a single service.\"\"\"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return {{
                "service": service_name,
                "status": "healthy", 
                "response_time": response.elapsed.total_seconds(),
                "details": response.json() if response.headers.get('content-type', '').startswith('application/json') else {{}}
            }}
        else:
            return {{
                "service": service_name,
                "status": "unhealthy",
                "error": f"HTTP {{response.status_code}}"
            }}
    except Exception as e:
        return {{
            "service": service_name,
            "status": "unhealthy",
            "error": str(e)
        }}

def main():
    parser = argparse.ArgumentParser(description='Health check for Braid Agent')
    parser.add_argument('--wait', action='store_true', help='Wait for all services to become healthy')
    parser.add_argument('--timeout', type=int, default=300, help='Maximum wait time in seconds')
    args = parser.parse_args()
    
    services = {{
        "agent": "http://localhost:8000/health",
        {', '.join([f'"{mcp}": "http://{mcp}-mcp-server:3000/health"' for mcp in mcps])}
    }}
    
    start_time = time.time()
    
    while True:
        all_healthy = True
        results = {{}}
        
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
            print(f"Timeout waiting for services to become healthy after {{args.timeout}}s")
            sys.exit(1)
        
        print("Waiting for services to become healthy...")
        time.sleep(5)

if __name__ == "__main__":
    main()
"""
    
    def _dict_to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dictionary to YAML format (basic implementation)."""
        yaml_lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                yaml_lines.append(f"{'  ' * indent}{key}:")
                yaml_lines.append(self._dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                yaml_lines.append(f"{'  ' * indent}{key}:")
                for item in value:
                    if isinstance(item, str):
                        yaml_lines.append(f"{'  ' * (indent + 1)}- {item}")
                    else:
                        yaml_lines.append(f"{'  ' * (indent + 1)}- {item}")
            elif value is None:
                yaml_lines.append(f"{'  ' * indent}{key}:")
            else:
                yaml_lines.append(f"{'  ' * indent}{key}: {value}")
        
        return '\n'.join(yaml_lines)
    
    def analyze_deployment_requirements(self, mcps: List[str]) -> Dict[str, Any]:
        """Analyze deployment requirements for given MCPs.
        
        Args:
            mcps: List of MCP IDs
            
        Returns:
            Deployment analysis and recommendations
        """
        analysis = {
            "total_mcps": len(mcps),
            "docker_required": [],
            "subprocess_mcps": [],
            "resource_requirements": {
                "memory": "1g",
                "cpu": "1.0",
                "disk": "10g"
            },
            "network_requirements": {
                "external_apis": [],
                "ports": [8000]
            },
            "security_considerations": [],
            "recommended_profile": "production"
        }
        
        # Analyze each MCP (would normally query registry)
        docker_mcps = ["notion", "agentql", "alphavantage", "perplexity", "mongodb"]
        
        for mcp in mcps:
            if mcp in docker_mcps:
                analysis["docker_required"].append(mcp)
            else:
                analysis["subprocess_mcps"].append(mcp)
        
        # Calculate resource requirements
        base_memory = 512  # MB
        mcp_memory = len(analysis["docker_required"]) * 256  # 256MB per Docker MCP
        analysis["resource_requirements"]["memory"] = f"{base_memory + mcp_memory}m"
        
        # Determine recommended profile
        if len(mcps) <= 2:
            analysis["recommended_profile"] = "development"
        elif len(mcps) <= 4:
            analysis["recommended_profile"] = "production"
        else:
            analysis["recommended_profile"] = "high_performance"
        
        return analysis