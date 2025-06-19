"""
MCP Integration system for adding MCPs to Braid agent builds.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from .registry import MCPRegistry
from .docker_templates import MCPDockerTemplates


class MCPIntegrator:
    """Handle integration of MCP servers into Braid agent builds."""
    
    def __init__(self, registry: Optional[MCPRegistry] = None):
        """Initialize MCP integrator.
        
        Args:
            registry: MCPRegistry instance. If None, creates default registry.
        """
        self.registry = registry or MCPRegistry()
        self.docker_templates = MCPDockerTemplates()
    
    def prepare_mcp_integration(self, agent_root: str, mcp_ids: List[str]) -> Dict[str, Any]:
        """Prepare MCP integration files for an agent.
        
        Args:
            agent_root: Path to agent root directory
            mcp_ids: List of MCP IDs to integrate
            
        Returns:
            Integration result with success status and details
        """
        agent_path = Path(agent_root)
        
        if not agent_path.exists():
            return {"success": False, "error": f"Agent directory not found: {agent_root}"}
        
        results = {
            "success": True,
            "integrated_mcps": [],
            "failed_mcps": [],
            "files_created": [],
            "environment_vars": [],
            "docker_services": []
        }
        
        # Create MCP directory in agent
        mcp_dir = agent_path / "mcp"
        mcp_dir.mkdir(exist_ok=True)
        
        for mcp_id in mcp_ids:
            try:
                integration_result = self._integrate_single_mcp(agent_path, mcp_id)
                if integration_result["success"]:
                    results["integrated_mcps"].append(mcp_id)
                    results["files_created"].extend(integration_result["files_created"])
                    results["environment_vars"].extend(integration_result["environment_vars"])
                    results["docker_services"].extend(integration_result["docker_services"])
                else:
                    results["failed_mcps"].append({
                        "mcp_id": mcp_id,
                        "error": integration_result["error"]
                    })
            except Exception as e:
                results["failed_mcps"].append({
                    "mcp_id": mcp_id,
                    "error": str(e)
                })
        
        # Update overall success status
        results["success"] = len(results["failed_mcps"]) == 0
        
        # Generate integration summary
        if results["integrated_mcps"]:
            self._generate_mcp_summary(agent_path, results)
        
        return results
    
    def _integrate_single_mcp(self, agent_path: Path, mcp_id: str) -> Dict[str, Any]:
        """Integrate a single MCP into the agent build.
        
        Args:
            agent_path: Path to agent directory
            mcp_id: MCP identifier to integrate
            
        Returns:
            Integration result for this MCP
        """
        mcp_data = self.registry.get_mcp_by_id(mcp_id)
        if not mcp_data:
            return {"success": False, "error": f"MCP '{mcp_id}' not found in registry"}
        
        # Validate MCP metadata
        validation_issues = self.registry.validate_mcp_metadata(mcp_id)
        if validation_issues:
            return {
                "success": False,
                "error": f"MCP validation failed: {'; '.join(validation_issues)}"
            }
        
        result = {
            "success": True,
            "files_created": [],
            "environment_vars": [],
            "docker_services": []
        }
        
        # Copy MCP configuration to agent
        mcp_source_dir = self._get_mcp_source_dir(mcp_id, mcp_data)
        if mcp_source_dir and mcp_source_dir.exists():
            agent_mcp_dir = agent_path / "mcp" / mcp_id
            shutil.copytree(mcp_source_dir, agent_mcp_dir, dirs_exist_ok=True)
            result["files_created"].append(f"mcp/{mcp_id}/")
        
        # Extract environment variables
        auth = mcp_data.get("authentication", {})
        env_vars = auth.get("required_env_vars", [])
        result["environment_vars"] = env_vars
        
        # Prepare Docker service configuration
        if mcp_data.get("docker_required", False):
            docker_service = self._create_docker_service_config(mcp_id, mcp_data)
            result["docker_services"].append(docker_service)
        
        # Create MCP client configuration
        client_config = self._create_mcp_client_config(mcp_id, mcp_data)
        client_config_path = agent_path / "mcp" / f"{mcp_id}_client.json"
        
        with open(client_config_path, 'w', encoding='utf-8') as f:
            json.dump(client_config, f, indent=2)
        result["files_created"].append(f"mcp/{mcp_id}_client.json")
        
        return result
    
    def _get_mcp_source_dir(self, mcp_id: str, mcp_data: Dict[str, Any]) -> Optional[Path]:
        """Get the source directory for an MCP."""
        # Get the Braid root directory
        braid_root = Path(__file__).parent.parent.parent
        category = mcp_data.get("category", "")
        
        mcp_source_dir = braid_root / "mcp" / category / mcp_id
        return mcp_source_dir if mcp_source_dir.exists() else None
    
    def _create_docker_service_config(self, mcp_id: str, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Docker service configuration for an MCP."""
        auth = mcp_data.get("authentication", {})
        env_vars = auth.get("required_env_vars", [])
        
        # Load server config if available
        server_config = {}
        mcp_source_dir = self._get_mcp_source_dir(mcp_id, mcp_data)
        if mcp_source_dir:
            config_file = mcp_source_dir / "server_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    server_config = json.load(f)
        
        docker_config = server_config.get("docker_config", {})
        
        service_config = {
            "image": docker_config.get("image", "node:18-slim"),
            "container_name": f"{mcp_id}-mcp-server",
            "environment": [f"{var}=${{{var}}}" for var in env_vars],
            "restart": "unless-stopped",
            "networks": ["braid-agent-network"]
        }
        
        # Add ports if specified
        if "ports" in docker_config:
            service_config["ports"] = docker_config["ports"]
        
        # Add volumes if specified
        if "volumes" in docker_config:
            service_config["volumes"] = docker_config["volumes"]
        
        # Add health check if specified
        if "health_check" in docker_config:
            service_config["healthcheck"] = docker_config["health_check"]
        
        # Add command if specified
        if "command" in docker_config:
            service_config["command"] = docker_config["command"]
        
        return {
            "service_name": f"{mcp_id}-mcp",
            "config": service_config
        }
    
    def _create_mcp_client_config(self, mcp_id: str, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create MCP client configuration for agent integration."""
        auth = mcp_data.get("authentication", {})
        
        # Load server config for additional details
        server_config = {}
        mcp_source_dir = self._get_mcp_source_dir(mcp_id, mcp_data)
        if mcp_source_dir:
            config_file = mcp_source_dir / "server_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    server_config = json.load(f)
        
        braid_config = server_config.get("braid_integration", {})
        
        return {
            "mcp_id": mcp_id,
            "name": mcp_data.get("name", mcp_id),
            "category": mcp_data.get("category", "unknown"),
            "connection": {
                "type": "docker" if mcp_data.get("docker_required") else "local",
                "host": f"{mcp_id}-mcp-server" if mcp_data.get("docker_required") else "localhost",
                "port": braid_config.get("port", 3001)
            },
            "authentication": {
                "type": auth.get("type", "none"),
                "env_vars": auth.get("required_env_vars", [])
            },
            "capabilities": mcp_data.get("capabilities", []),
            "tool_prefix": braid_config.get("tool_prefix", f"{mcp_id}_"),
            "resource_namespace": braid_config.get("resource_namespace", mcp_id),
            "auto_start": braid_config.get("auto_start", True)
        }
    
    def _generate_mcp_summary(self, agent_path: Path, integration_result: Dict[str, Any]) -> None:
        """Generate MCP integration summary documentation."""
        summary_content = self._create_summary_content(integration_result)
        
        summary_path = agent_path / "MCP_INTEGRATION.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        integration_result["files_created"].append("MCP_INTEGRATION.md")
    
    def _create_summary_content(self, integration_result: Dict[str, Any]) -> str:
        """Create content for MCP integration summary."""
        content = "# MCP Integration Summary\n\n"
        content += "This agent has been configured with the following MCP servers:\n\n"
        
        for mcp_id in integration_result["integrated_mcps"]:
            mcp_data = self.registry.get_mcp_by_id(mcp_id)
            if mcp_data:
                content += f"## {mcp_data.get('name', mcp_id)}\n"
                content += f"- **Category**: {mcp_data.get('category', 'unknown')}\n"
                content += f"- **Description**: {mcp_data.get('description', 'No description')}\n"
                content += f"- **Repository**: {mcp_data.get('repository', 'N/A')}\n"
                
                # Add capabilities
                capabilities = mcp_data.get("capabilities", [])
                if capabilities:
                    content += "- **Capabilities**:\n"
                    for cap in capabilities[:5]:  # Show first 5
                        content += f"  - {cap}\n"
                    if len(capabilities) > 5:
                        content += f"  - ... and {len(capabilities) - 5} more\n"
                
                content += "\n"
        
        # Add environment variables section
        if integration_result["environment_vars"]:
            content += "## Required Environment Variables\n\n"
            content += "Add these variables to your `.env` file:\n\n"
            for var in set(integration_result["environment_vars"]):
                content += f"- `{var}`: [Add your value here]\n"
            content += "\n"
        
        # Add Docker services section
        if integration_result["docker_services"]:
            content += "## Docker Services\n\n"
            content += "The following MCP servers will run as Docker services:\n\n"
            for service in integration_result["docker_services"]:
                content += f"- `{service['service_name']}`: {service['config']['image']}\n"
            content += "\nThese are automatically configured in your `docker-compose.yml`.\n\n"
        
        content += "## Usage\n\n"
        content += "MCP tools are automatically available in your agent. "
        content += "You can use them just like core tools, with the appropriate prefixes.\n\n"
        content += "## Documentation\n\n"
        content += "See individual MCP directories in `mcp/` for specific documentation and setup instructions.\n"
        
        return content
    
    def update_docker_compose(self, agent_path: Path, docker_services: List[Dict[str, Any]]) -> bool:
        """Update docker-compose.yml with MCP services.
        
        Args:
            agent_path: Path to agent directory
            docker_services: List of Docker service configurations
            
        Returns:
            True if successfully updated
        """
        compose_path = agent_path / "docker-compose.yml"
        
        if not compose_path.exists():
            return False
        
        try:
            import yaml
            
            # Load existing compose file
            with open(compose_path, 'r', encoding='utf-8') as f:
                compose_data = yaml.safe_load(f)
            
            # Ensure services section exists
            if "services" not in compose_data:
                compose_data["services"] = {}
            
            # Add MCP services
            for service in docker_services:
                service_name = service["service_name"]
                compose_data["services"][service_name] = service["config"]
            
            # Ensure network exists
            if "networks" not in compose_data:
                compose_data["networks"] = {}
            if "braid-agent-network" not in compose_data["networks"]:
                compose_data["networks"]["braid-agent-network"] = {"driver": "bridge"}
            
            # Write updated compose file
            with open(compose_path, 'w', encoding='utf-8') as f:
                yaml.dump(compose_data, f, default_flow_style=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to update docker-compose.yml: {e}")
            return False
    
    def prepare_mcp_dockerization(self, agent_root: str, mcp_ids: List[str], 
                                production_mode: bool = True) -> Dict[str, Any]:
        """Prepare MCP servers for Docker deployment.
        
        Args:
            agent_root: Path to agent root directory
            mcp_ids: List of MCP IDs to dockerize
            production_mode: Whether to use production-optimized configurations
            
        Returns:
            Dockerization result with Docker files and compose services
        """
        agent_path = Path(agent_root)
        
        if not agent_path.exists():
            return {"success": False, "error": f"Agent directory not found: {agent_root}"}
        
        results = {
            "success": True,
            "dockerized_mcps": [],
            "failed_mcps": [],
            "docker_files": [],
            "compose_services": {},
            "volumes": [],
            "networks": ["braid-mcp-network"]
        }
        
        for mcp_id in mcp_ids:
            try:
                docker_result = self._dockerize_single_mcp(agent_path, mcp_id, production_mode)
                if docker_result["success"]:
                    results["dockerized_mcps"].append(mcp_id)
                    results["docker_files"].extend(docker_result["docker_files"])
                    results["compose_services"][f"{mcp_id}-mcp"] = docker_result["compose_service"]
                    results["volumes"].extend(docker_result["volumes"])
                else:
                    results["failed_mcps"].append({
                        "mcp_id": mcp_id,
                        "error": docker_result["error"]
                    })
            except Exception as e:
                results["failed_mcps"].append({
                    "mcp_id": mcp_id,
                    "error": str(e)
                })
        
        # Update overall success status
        results["success"] = len(results["failed_mcps"]) == 0
        
        # Generate enhanced docker-compose with MCPs
        if results["dockerized_mcps"]:
            self._generate_enhanced_docker_compose(agent_path, results)
        
        return results
    
    def _dockerize_single_mcp(self, agent_path: Path, mcp_id: str, 
                             production_mode: bool) -> Dict[str, Any]:
        """Dockerize a single MCP server.
        
        Args:
            agent_path: Path to agent directory
            mcp_id: MCP identifier
            production_mode: Whether to use production configurations
            
        Returns:
            Dockerization result for this MCP
        """
        mcp_data = self.registry.get_mcp_by_id(mcp_id)
        if not mcp_data:
            return {"success": False, "error": f"MCP '{mcp_id}' not found in registry"}
        
        # Get MCP configuration
        mcp_source_dir = self._get_mcp_source_dir(mcp_id, mcp_data)
        if not mcp_source_dir or not mcp_source_dir.exists():
            return {"success": False, "error": f"MCP source directory not found for '{mcp_id}'"}
        
        # Load server config
        server_config_path = mcp_source_dir / "server_config.json"
        if server_config_path.exists():
            with open(server_config_path, 'r') as f:
                server_config = json.load(f)
        else:
            server_config = {}
        
        result = {
            "success": True,
            "docker_files": [],
            "compose_service": {},
            "volumes": []
        }
        
        try:
            # Create MCP Docker directory in agent
            mcp_docker_dir = agent_path / "mcp" / mcp_id
            mcp_docker_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate Dockerfile
            dockerfile_content = self._generate_mcp_dockerfile(mcp_id, mcp_data, server_config, production_mode)
            dockerfile_path = mcp_docker_dir / "Dockerfile"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            result["docker_files"].append(f"mcp/{mcp_id}/Dockerfile")
            
            # Generate MCP startup script
            startup_script = self._generate_mcp_startup_script(mcp_id, server_config)
            if startup_script:
                script_path = mcp_docker_dir / "start.sh"
                with open(script_path, 'w') as f:
                    f.write(startup_script)
                script_path.chmod(0o755)  # Make executable
                result["docker_files"].append(f"mcp/{mcp_id}/start.sh")
            
            # Generate package.json for Node.js MCPs
            if self.docker_templates.detect_mcp_type(server_config) == "nodejs":
                package_json = self._generate_mcp_package_json(mcp_id, server_config)
                package_path = mcp_docker_dir / "package.json"
                with open(package_path, 'w') as f:
                    json.dump(package_json, f, indent=2)
                result["docker_files"].append(f"mcp/{mcp_id}/package.json")
            
            # Generate requirements.txt for Python MCPs
            elif self.docker_templates.detect_mcp_type(server_config) == "python":
                requirements = self._generate_mcp_requirements(mcp_id, server_config)
                if requirements:
                    req_path = mcp_docker_dir / "requirements.txt"
                    with open(req_path, 'w') as f:
                        f.write(requirements)
                    result["docker_files"].append(f"mcp/{mcp_id}/requirements.txt")
            
            # Generate docker-compose service
            compose_service = self.docker_templates.generate_docker_compose_service(
                mcp_id, mcp_data
            )
            result["compose_service"] = compose_service
            
            # Add volumes for data persistence
            template_type = self.docker_templates.detect_mcp_type(server_config)
            template = self.docker_templates.get_template(template_type)
            if template and template.volumes:
                for volume in template.volumes:
                    volume_name = f"{mcp_id}-{volume.split('/')[-1]}"
                    result["volumes"].append(volume_name)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Failed to dockerize {mcp_id}: {str(e)}"}
    
    def _generate_mcp_dockerfile(self, mcp_id: str, mcp_data: Dict[str, Any], 
                                server_config: Dict[str, Any], production_mode: bool) -> str:
        """Generate Dockerfile for MCP server."""
        # Use docker templates system
        dockerfile = self.docker_templates.generate_dockerfile(server_config)
        
        # Add MCP-specific customizations
        if production_mode:
            # Add production optimizations
            dockerfile += "\n# Production optimizations\n"
            dockerfile += "ENV NODE_ENV=production\n" if "node" in dockerfile.lower() else ""
            dockerfile += "RUN npm prune --production\n" if "npm" in dockerfile.lower() else ""
        
        return dockerfile
    
    def _generate_mcp_startup_script(self, mcp_id: str, server_config: Dict[str, Any]) -> Optional[str]:
        """Generate startup script for MCP server."""
        mcp_server_config = server_config.get("mcp_server", {})
        command = mcp_server_config.get("command", [])
        
        if not command:
            return None
        
        script_content = """#!/bin/bash
set -e

echo "🚀 Starting MCP server: {mcp_id}"

# Wait for dependencies to be ready
sleep 2

# Start MCP server
echo "📡 Executing: {command}"
exec {command_str}
""".format(
            mcp_id=mcp_id,
            command=" ".join(command),
            command_str=" ".join(command)
        )
        
        return script_content
    
    def _generate_mcp_package_json(self, mcp_id: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate package.json for Node.js MCP servers."""
        dependencies = server_config.get("braid_integration", {}).get("dependencies", [])
        
        package_json = {
            "name": f"{mcp_id}-mcp-server",
            "version": "1.0.0",
            "description": f"MCP server for {mcp_id}",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "health": "node -e 'process.exit(0)'"
            },
            "dependencies": {}
        }
        
        # Add dependencies
        for dep in dependencies:
            if "@" in dep:
                # Handle scoped packages with versions
                if dep.count("@") > 1:
                    parts = dep.rsplit("@", 1)
                    package_name = parts[0]
                    version = parts[1]
                else:
                    package_name = dep
                    version = "latest"
            else:
                package_name = dep
                version = "latest"
            
            package_json["dependencies"][package_name] = version
        
        return package_json
    
    def _generate_mcp_requirements(self, mcp_id: str, server_config: Dict[str, Any]) -> Optional[str]:
        """Generate requirements.txt for Python MCP servers."""
        dependencies = server_config.get("braid_integration", {}).get("dependencies", [])
        
        if not dependencies:
            return None
        
        requirements = []
        for dep in dependencies:
            if "==" in dep or ">=" in dep or "<=" in dep:
                requirements.append(dep)
            else:
                requirements.append(f"{dep}>=1.0.0")
        
        return "\n".join(requirements) + "\n"
    
    def _generate_enhanced_docker_compose(self, agent_path: Path, docker_results: Dict[str, Any]) -> None:
        """Generate enhanced docker-compose.yml with MCP services."""
        compose_path = agent_path / "docker-compose.yml"
        
        # Load existing compose file or create new
        if compose_path.exists():
            try:
                import yaml
                with open(compose_path, 'r') as f:
                    compose_data = yaml.safe_load(f) or {}
            except Exception:
                compose_data = {}
        else:
            compose_data = {}
        
        # Ensure required sections exist
        if "services" not in compose_data:
            compose_data["services"] = {}
        if "networks" not in compose_data:
            compose_data["networks"] = {}
        if "volumes" not in compose_data:
            compose_data["volumes"] = {}
        
        # Add MCP services
        for service_name, service_config in docker_results["compose_services"].items():
            compose_data["services"][service_name] = service_config
        
        # Add MCP network
        compose_data["networks"]["braid-mcp-network"] = {
            "driver": "bridge",
            "name": "braid-mcp-network"
        }
        
        # Ensure main agent is on MCP network
        if "agent" in compose_data["services"]:
            if "networks" not in compose_data["services"]["agent"]:
                compose_data["services"]["agent"]["networks"] = []
            if "braid-mcp-network" not in compose_data["services"]["agent"]["networks"]:
                compose_data["services"]["agent"]["networks"].append("braid-mcp-network")
        
        # Add volumes for MCP data persistence
        for volume in docker_results["volumes"]:
            compose_data["volumes"][volume] = {"driver": "local"}
        
        # Add depends_on for proper startup ordering
        if "agent" in compose_data["services"]:
            if "depends_on" not in compose_data["services"]["agent"]:
                compose_data["services"]["agent"]["depends_on"] = {}
            
            for mcp_id in docker_results["dockerized_mcps"]:
                service_name = f"{mcp_id}-mcp"
                compose_data["services"]["agent"]["depends_on"][service_name] = {
                    "condition": "service_healthy"
                }
        
        # Write updated compose file
        try:
            import yaml
            with open(compose_path, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, indent=2, sort_keys=False)
        except ImportError:
            # Fallback to JSON format if PyYAML not available
            with open(compose_path.with_suffix('.json'), 'w') as f:
                json.dump(compose_data, f, indent=2)
    
    def validate_mcp_deployment(self, agent_root: str, mcp_ids: List[str]) -> Dict[str, Any]:
        """Validate MCP deployment configuration.
        
        Args:
            agent_root: Path to agent root directory
            mcp_ids: List of MCP IDs to validate
            
        Returns:
            Validation result with any issues found
        """
        agent_path = Path(agent_root)
        validation_results = {
            "success": True,
            "issues": [],
            "warnings": [],
            "mcps_validated": [],
            "deployment_ready": True
        }
        
        for mcp_id in mcp_ids:
            mcp_issues = []
            
            # Check MCP exists in registry
            mcp_data = self.registry.get_mcp_by_id(mcp_id)
            if not mcp_data:
                mcp_issues.append(f"MCP '{mcp_id}' not found in registry")
                continue
            
            # Check Docker files exist
            mcp_docker_dir = agent_path / "mcp" / mcp_id
            if not mcp_docker_dir.exists():
                mcp_issues.append(f"Docker directory missing for '{mcp_id}'")
            else:
                # Check Dockerfile exists
                dockerfile_path = mcp_docker_dir / "Dockerfile"
                if not dockerfile_path.exists():
                    mcp_issues.append(f"Dockerfile missing for '{mcp_id}'")
                
                # Check for required environment variables
                auth_config = mcp_data.get("authentication", {})
                required_vars = auth_config.get("required_env_vars", [])
                
                env_file = agent_path / ".env"
                if required_vars and not env_file.exists():
                    mcp_issues.append(f"Missing .env file for '{mcp_id}' environment variables")
                elif required_vars and env_file.exists():
                    # Check if required vars are defined
                    with open(env_file, 'r') as f:
                        env_content = f.read()
                    
                    for var in required_vars:
                        if f"{var}=" not in env_content:
                            validation_results["warnings"].append(
                                f"Environment variable '{var}' not set for '{mcp_id}'"
                            )
            
            if mcp_issues:
                validation_results["issues"].extend(mcp_issues)
                validation_results["success"] = False
                validation_results["deployment_ready"] = False
            else:
                validation_results["mcps_validated"].append(mcp_id)
        
        return validation_results