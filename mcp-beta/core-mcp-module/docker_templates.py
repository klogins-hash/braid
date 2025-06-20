"""
Docker templates for MCP server containerization.
Provides standardized, reliable Docker configurations for different MCP types.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MCPDockerTemplate:
    """Template for MCP Docker configuration."""
    name: str
    base_image: str
    install_commands: List[str]
    run_command: List[str]
    health_check: Dict[str, Any]
    environment_vars: List[str]
    ports: List[str]
    volumes: List[str]
    dependencies: List[str]


class MCPDockerTemplates:
    """Manages Docker templates for different MCP server types."""
    
    def __init__(self):
        self.templates = {
            "nodejs": self._create_nodejs_template(),
            "python": self._create_python_template(),
            "custom": self._create_custom_template(),
            "xero": self._create_xero_template()
        }
    
    def _create_nodejs_template(self) -> MCPDockerTemplate:
        """Template for Node.js-based MCP servers."""
        return MCPDockerTemplate(
            name="nodejs_mcp",
            base_image="node:18-slim",
            install_commands=[
                "apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*",
                "npm config set fund false",
                "npm config set audit false"
            ],
            run_command=["node", "/app/server.js"],
            health_check={
                "test": ["CMD", "node", "-e", "process.exit(0)"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            environment_vars=["NODE_ENV=production"],
            ports=["3000"],
            volumes=["/app/data", "/app/cache"],
            dependencies=[]
        )
    
    def _create_python_template(self) -> MCPDockerTemplate:
        """Template for Python-based MCP servers."""
        return MCPDockerTemplate(
            name="python_mcp",
            base_image="python:3.11-slim",
            install_commands=[
                "apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*",
                "pip install --no-cache-dir --upgrade pip"
            ],
            run_command=["python", "/app/server.py"],
            health_check={
                "test": ["CMD", "python", "-c", "import sys; sys.exit(0)"],
                "interval": "30s", 
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            environment_vars=["PYTHONUNBUFFERED=1", "PYTHONDONTWRITEBYTECODE=1"],
            ports=["8000"],
            volumes=["/app/data", "/app/cache"],
            dependencies=[]
        )
    
    def _create_custom_template(self) -> MCPDockerTemplate:
        """Template for custom MCP servers."""
        return MCPDockerTemplate(
            name="custom_mcp",
            base_image="alpine:3.18",
            install_commands=[
                "apk add --no-cache curl"
            ],
            run_command=["sh", "/app/start.sh"],
            health_check={
                "test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
                "interval": "30s",
                "timeout": "10s", 
                "retries": 3,
                "start_period": "60s"
            },
            environment_vars=[],
            ports=["8080"],
            volumes=["/app/data"],
            dependencies=[]
        )
    
    def _create_xero_template(self) -> MCPDockerTemplate:
        """Template for Xero MCP server."""
        return MCPDockerTemplate(
            name="xero_mcp",
            base_image="node:18-alpine",
            install_commands=[
                "apk add --no-cache curl git python3 make g++",
                "npm config set fund false",
                "npm config set audit false"
            ],
            run_command=["node", "dist/index.js"],
            health_check={
                "test": ["CMD", "node", "-e", "console.log('Health check'); process.exit(0)"],
                "interval": "30s",
                "timeout": "15s",
                "retries": 3,
                "start_period": "90s"
            },
            environment_vars=[
                "NODE_ENV=production",
                "NODE_OPTIONS=--max-old-space-size=512"
            ],
            ports=["3004"],
            volumes=["/app/cache"],
            dependencies=["@xeroapi/xero-node", "mcp-server"]
        )
    
    def get_template(self, template_type: str) -> Optional[MCPDockerTemplate]:
        """Get a Docker template by type."""
        return self.templates.get(template_type)
    
    def detect_mcp_type(self, mcp_config: Dict[str, Any]) -> str:
        """Detect the appropriate template type for an MCP."""
        # Check for specific indicators
        dependencies = mcp_config.get("dependencies", [])
        command = mcp_config.get("command", [])
        
        # Check for specific MCP servers first
        if any("xero" in dep.lower() for dep in dependencies):
            return "xero"
        
        # Node.js indicators
        if any("npm" in dep or "@" in dep for dep in dependencies):
            return "nodejs"
        if any("npx" in cmd or "node" in cmd for cmd in command):
            return "nodejs"
        
        # Python indicators  
        if any("pip" in dep or "python" in dep for dep in dependencies):
            return "python"
        if any("python" in cmd for cmd in command):
            return "python"
        
        # Default to custom
        return "custom"
    
    def generate_dockerfile(self, mcp_config: Dict[str, Any], template_type: Optional[str] = None) -> str:
        """Generate a Dockerfile for an MCP server."""
        if template_type is None:
            template_type = self.detect_mcp_type(mcp_config)
        
        template = self.get_template(template_type)
        if not template:
            template = self.get_template("custom")
        
        dockerfile_content = f"""# Auto-generated Dockerfile for MCP Server
# Template: {template.name}
FROM {template.base_image}

# Create non-root user for security
RUN adduser --disabled-password --gecos '' mcp

# Install system dependencies
"""
        
        for cmd in template.install_commands:
            dockerfile_content += f"RUN {cmd}\n"
        
        dockerfile_content += """
# Set working directory
WORKDIR /app
RUN chown mcp:mcp /app

# Copy MCP server files
COPY --chown=mcp:mcp . /app/

# Install MCP dependencies
"""
        
        # Add specific installation based on MCP type
        if template_type == "nodejs":
            dockerfile_content += "RUN npm ci --only=production\n"
        elif template_type == "python":
            dockerfile_content += "RUN pip install --no-cache-dir -r requirements.txt\n"
        elif template_type == "xero":
            dockerfile_content += """# Clone and build Xero MCP server
RUN git clone https://github.com/XeroAPI/xero-mcp-server.git .
RUN npm ci --only=production
RUN npm run build
"""
        
        # Add environment variables
        for env_var in template.environment_vars:
            dockerfile_content += f"ENV {env_var}\n"
        
        # Add health check
        health_cmd = " ".join(template.health_check["test"])
        dockerfile_content += f"""
# Health check
HEALTHCHECK --interval={template.health_check["interval"]} \\
            --timeout={template.health_check["timeout"]} \\
            --start-period={template.health_check["start_period"]} \\
            --retries={template.health_check["retries"]} \\
    {health_cmd}

# Switch to non-root user
USER mcp

# Expose ports
"""
        
        for port in template.ports:
            dockerfile_content += f"EXPOSE {port}\n"
        
        # Add run command
        cmd_str = '", "'.join(template.run_command)
        dockerfile_content += f'\nCMD ["{cmd_str}"]\n'
        
        return dockerfile_content
    
    def generate_docker_compose_service(self, mcp_id: str, mcp_config: Dict[str, Any], 
                                      template_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate docker-compose service configuration for an MCP."""
        if template_type is None:
            template_type = self.detect_mcp_type(mcp_config)
        
        template = self.get_template(template_type)
        if not template:
            template = self.get_template("custom")
        
        # Extract environment variables from MCP config
        env_vars = []
        auth_config = mcp_config.get("authentication", {})
        if auth_config.get("required_env_vars"):
            for var in auth_config["required_env_vars"]:
                env_vars.append(f"{var}=${{{var}}}")
        
        # Add template environment variables
        env_vars.extend(template.environment_vars)
        
        service_config = {
            "build": {
                "context": f"./mcp/{mcp_id}",
                "dockerfile": "Dockerfile"
            },
            "container_name": f"{mcp_id}-mcp-server",
            "environment": env_vars,
            "restart": "unless-stopped",
            "networks": ["braid-mcp-network"],
            "healthcheck": {
                "test": template.health_check["test"],
                "interval": template.health_check["interval"],
                "timeout": template.health_check["timeout"],
                "retries": template.health_check["retries"],
                "start_period": template.health_check["start_period"]
            }
        }
        
        # Add ports if needed (usually not exposed externally)
        # MCPs communicate via internal network
        
        # Add volumes for data persistence
        if template.volumes:
            volumes = []
            for vol_path in template.volumes:
                vol_name = f"{mcp_id}-{vol_path.split('/')[-1]}"
                volumes.append(f"{vol_name}:{vol_path}")
            service_config["volumes"] = volumes
        
        return service_config