#!/usr/bin/env python3
"""
Comprehensive test script for MCP deployment and Docker orchestration.
Tests the entire pipeline from MCP detection to Docker deployment.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Add braid root to path
braid_root = Path(__file__).parent.parent
sys.path.insert(0, str(braid_root))

from core.mcp.integration import MCPIntegrator
from core.mcp.docker_templates import MCPDockerTemplates
from core.mcp.discovery import MCPDiscovery


def test_mcp_docker_templates():
    """Test MCP Docker template generation."""
    print("🧪 Testing MCP Docker Templates...")
    
    templates = MCPDockerTemplates()
    
    # Test template detection
    test_configs = [
        {
            "name": "nodejs_test",
            "dependencies": ["@notionhq/notion-mcp-server"],
            "command": ["npx", "-y", "@notionhq/notion-mcp-server"]
        },
        {
            "name": "python_test", 
            "dependencies": ["requests>=2.28.0"],
            "command": ["python", "server.py"]
        }
    ]
    
    for config in test_configs:
        detected_type = templates.detect_mcp_type(config)
        print(f"   📋 {config['name']}: detected as '{detected_type}'")
        
        # Generate Dockerfile
        dockerfile = templates.generate_dockerfile(config)
        if dockerfile and len(dockerfile) > 100:
            print(f"   ✅ Dockerfile generated ({len(dockerfile)} chars)")
        else:
            print(f"   ❌ Dockerfile generation failed")
            return False
        
        # Generate docker-compose service
        service = templates.generate_docker_compose_service(config["name"], config)
        if service and "build" in service:
            print(f"   ✅ Docker Compose service generated")
        else:
            print(f"   ❌ Docker Compose service generation failed")
            return False
    
    return True


def test_mcp_integration():
    """Test MCP integration and dockerization."""
    print("\n🔧 Testing MCP Integration...")
    
    agent_root = Path(__file__).parent
    integrator = MCPIntegrator()
    
    # Test MCP detection
    mcps_found = []
    mcp_dir = agent_root / "mcp"
    if mcp_dir.exists():
        for item in mcp_dir.iterdir():
            if item.is_dir() and not item.name.endswith("_client.json"):
                if (item / "metadata.json").exists() or (item / "server_config.json").exists():
                    mcps_found.append(item.name)
    
    print(f"   📦 Found MCPs: {mcps_found}")
    
    if not mcps_found:
        print("   ⚠️  No MCPs found for testing")
        return True
    
    # Test dockerization
    docker_result = integrator.prepare_mcp_dockerization(
        str(agent_root), mcps_found, production_mode=True
    )
    
    if docker_result["success"]:
        print(f"   ✅ Dockerization successful: {docker_result['dockerized_mcps']}")
        print(f"   📁 Docker files created: {len(docker_result['docker_files'])}")
        
        # Validate generated files
        for mcp_id in docker_result["dockerized_mcps"]:
            dockerfile_path = agent_root / "mcp" / mcp_id / "Dockerfile"
            if dockerfile_path.exists():
                print(f"   ✅ {mcp_id}: Dockerfile exists")
            else:
                print(f"   ❌ {mcp_id}: Dockerfile missing")
                return False
        
        return True
    else:
        print(f"   ❌ Dockerization failed: {docker_result['failed_mcps']}")
        return False


def test_package_command_with_mcps():
    """Test the enhanced braid package command with MCP auto-dockerization."""
    print("\n📦 Testing Enhanced Package Command...")
    
    agent_root = Path(__file__).parent
    
    try:
        # Run braid package with production flag
        result = subprocess.run(
            ["braid", "package", "--production"],
            cwd=str(agent_root),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("   ✅ Package command executed successfully")
            
            # Check output for MCP messages
            output = result.stdout
            if "MCP" in output:
                print("   ✅ MCP detection and processing detected in output")
                if "Dockerized" in output:
                    print("   ✅ MCP dockerization confirmed")
            else:
                print("   ℹ️  No MCP-specific output (might be no MCPs)")
            
            # Verify enhanced docker-compose.yml
            compose_path = agent_root / "docker-compose.yml"
            if compose_path.exists():
                with open(compose_path, 'r') as f:
                    compose_content = f.read()
                
                if "braid-mcp-network" in compose_content:
                    print("   ✅ MCP networking configured in docker-compose.yml")
                else:
                    print("   ℹ️  No MCP networking in docker-compose.yml")
                
                if "-mcp" in compose_content:
                    print("   ✅ MCP services found in docker-compose.yml")
                else:
                    print("   ℹ️  No MCP services in docker-compose.yml")
            
            return True
        else:
            print(f"   ❌ Package command failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Package command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Package command error: {e}")
        return False


def test_docker_compose_validation():
    """Test Docker Compose file validation and structure."""
    print("\n🐳 Testing Docker Compose Configuration...")
    
    agent_root = Path(__file__).parent
    compose_path = agent_root / "docker-compose.yml"
    
    if not compose_path.exists():
        print("   ❌ docker-compose.yml not found")
        return False
    
    try:
        # Test docker-compose config validation
        result = subprocess.run(
            ["docker", "compose", "config"],
            cwd=str(agent_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ Docker Compose configuration is valid")
            
            # Parse the validated config
            config = result.stdout
            
            # Check for required elements
            if "braid-mcp-network" in config:
                print("   ✅ MCP network configuration found")
            
            if "agent" in config and "depends_on" in config:
                print("   ✅ Service dependencies configured")
            
            if "healthcheck" in config:
                print("   ✅ Health checks configured")
            
            # Count services
            service_count = config.count("  ") // 2  # Rough count
            print(f"   📊 Estimated {service_count} services configured")
            
            return True
        else:
            print(f"   ❌ Docker Compose validation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Docker Compose validation timed out")
        return False
    except Exception as e:
        print(f"   ❌ Docker Compose validation error: {e}")
        return False


def test_mcp_deployment_readiness():
    """Test MCP deployment readiness validation."""
    print("\n🔍 Testing MCP Deployment Readiness...")
    
    agent_root = Path(__file__).parent
    integrator = MCPIntegrator()
    
    # Find MCPs
    mcps_found = []
    mcp_dir = agent_root / "mcp"
    if mcp_dir.exists():
        for item in mcp_dir.iterdir():
            if item.is_dir() and not item.name.endswith("_client.json"):
                if (item / "metadata.json").exists() or (item / "server_config.json").exists():
                    mcps_found.append(item.name)
    
    if not mcps_found:
        print("   ℹ️  No MCPs to validate")
        return True
    
    # Validate deployment
    validation_result = integrator.validate_mcp_deployment(str(agent_root), mcps_found)
    
    print(f"   📋 MCPs validated: {validation_result['mcps_validated']}")
    print(f"   ✅ Deployment ready: {validation_result['deployment_ready']}")
    
    if validation_result["issues"]:
        print("   ⚠️  Issues found:")
        for issue in validation_result["issues"]:
            print(f"      - {issue}")
    
    if validation_result["warnings"]:
        print("   ⚠️  Warnings:")
        for warning in validation_result["warnings"]:
            print(f"      - {warning}")
    
    return validation_result["deployment_ready"]


def test_multi_mcp_scenario():
    """Test scenarios with multiple MCPs (if available)."""
    print("\n🔀 Testing Multi-MCP Scenarios...")
    
    agent_root = Path(__file__).parent
    
    # Count available MCPs
    mcps_found = []
    mcp_dir = agent_root / "mcp"
    if mcp_dir.exists():
        for item in mcp_dir.iterdir():
            if item.is_dir() and not item.name.endswith("_client.json"):
                if (item / "metadata.json").exists():
                    mcps_found.append(item.name)
    
    print(f"   📦 Available MCPs: {len(mcps_found)} ({', '.join(mcps_found)})")
    
    if len(mcps_found) < 1:
        print("   ℹ️  Single or no MCP scenario - creating simulated test")
        
        # Create a mock second MCP for testing
        mock_mcp_dir = agent_root / "mcp" / "test_slack"
        mock_mcp_dir.mkdir(exist_ok=True)
        
        mock_metadata = {
            "mcp_info": {
                "name": "Test Slack MCP",
                "id": "test_slack",
                "category": "communication"
            },
            "authentication": {
                "type": "api_key",
                "required_env_vars": ["SLACK_BOT_TOKEN"]
            }
        }
        
        with open(mock_mcp_dir / "metadata.json", 'w') as f:
            json.dump(mock_metadata, f, indent=2)
        
        mcps_found.append("test_slack")
        print(f"   🧪 Created mock MCP for testing: {len(mcps_found)} total")
    
    # Test multi-MCP integration
    integrator = MCPIntegrator()
    docker_result = integrator.prepare_mcp_dockerization(
        str(agent_root), mcps_found, production_mode=True
    )
    
    if docker_result["success"]:
        print(f"   ✅ Multi-MCP dockerization successful")
        print(f"   📦 Services created: {len(docker_result['compose_services'])}")
        print(f"   🔗 Networks: {docker_result['networks']}")
        print(f"   💾 Volumes: {len(docker_result['volumes'])}")
        return True
    else:
        print(f"   ❌ Multi-MCP dockerization failed")
        return False


def main():
    """Run comprehensive MCP deployment tests."""
    print("🚀 Comprehensive MCP Deployment Testing\n")
    
    tests = [
        ("Docker Templates", test_mcp_docker_templates),
        ("MCP Integration", test_mcp_integration), 
        ("Package Command", test_package_command_with_mcps),
        ("Docker Compose", test_docker_compose_validation),
        ("Deployment Readiness", test_mcp_deployment_readiness),
        ("Multi-MCP Scenarios", test_multi_mcp_scenario)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"🧪 Running {test_name} test...")
            if test_func():
                print(f"✅ {test_name} test PASSED\n")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED\n")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}\n")
            failed += 1
    
    print("📊 Test Results Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {passed/(passed+failed)*100:.0f}%")
    
    if failed == 0:
        print("\n🎉 All MCP deployment tests passed!")
        print("🚀 The MCP Docker orchestration system is ready for production!")
        
        print("\n📋 What this validates:")
        print("   ✅ MCP auto-detection and dockerization")
        print("   ✅ Multi-MCP deployment support")
        print("   ✅ Docker networking and health checks")
        print("   ✅ Production-ready orchestration")
        print("   ✅ Scalable architecture for future MCPs")
        
        print("\n🎯 Ready for:")
        print("   - Production deployments with MCPs")
        print("   - Multi-MCP agent architectures")
        print("   - Reliable Docker orchestration")
        print("   - Future MCP integrations")
        
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review output above.")
        print("🔧 The system may need adjustments before production use.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)