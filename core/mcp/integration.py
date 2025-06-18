"""
MCP Integration system for adding MCPs to Braid agent builds.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from .registry import MCPRegistry


class MCPIntegrator:
    """Handle integration of MCP servers into Braid agent builds."""
    
    def __init__(self, registry: Optional[MCPRegistry] = None):
        """Initialize MCP integrator.
        
        Args:
            registry: MCPRegistry instance. If None, creates default registry.
        """
        self.registry = registry or MCPRegistry()
    
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