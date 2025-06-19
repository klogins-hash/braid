#!/usr/bin/env python3
"""
Script to integrate Notion MCP into the test agent.
"""

import sys
import os
from pathlib import Path

# Add the braid directory to Python path
braid_root = Path(__file__).parent.parent
sys.path.insert(0, str(braid_root))

from core.mcp.integration import MCPIntegrator
from core.mcp.discovery import MCPDiscovery


def main():
    """Integrate Notion MCP into this agent."""
    print("🔧 Integrating Notion MCP into test agent...")
    
    # Get current agent directory
    agent_root = Path(__file__).parent
    print(f"   Agent directory: {agent_root}")
    
    # Initialize integrator
    integrator = MCPIntegrator()
    
    # Test task analysis first
    discovery = MCPDiscovery()
    task = "I want to create an agent that can search my Notion workspace and create pages"
    analysis = discovery.analyze_task_description(task)
    
    print(f"\n📝 Task analysis:")
    print(f"   Task: {task}")
    print(f"   Should suggest MCP: {analysis['requires_mcp']}")
    print(f"   Confidence: {analysis['confidence']:.0%}")
    
    if analysis['suggested_mcps']:
        mcp_id = analysis['suggested_mcps'][0]['mcp_id']
        print(f"   Suggested MCP: {mcp_id}")
        
        # Integrate the MCP
        print(f"\n🚀 Integrating {mcp_id} MCP...")
        result = integrator.prepare_mcp_integration(str(agent_root), [mcp_id])
        
        if result['success']:
            print("   ✅ MCP integration successful!")
            print(f"   📄 Files created: {len(result['files_created'])}")
            for file in result['files_created']:
                print(f"      - {file}")
            
            print(f"   🔑 Environment variables required: {result['environment_vars']}")
            print(f"   🐳 Docker services: {len(result['docker_services'])}")
            
        else:
            print("   ❌ MCP integration failed!")
            for failure in result['failed_mcps']:
                print(f"      {failure['mcp_id']}: {failure['error']}")
        
        # Update .env.example with MCP requirements
        update_env_example(agent_root, result['environment_vars'])
        
        print(f"\n📖 Next steps:")
        print(f"   1. Add your Notion API key to .env:")
        print(f"      NOTION_API_KEY=your_notion_integration_token")
        print(f"   2. Review the MCP_INTEGRATION.md file")
        print(f"   3. Test with: python src/notion_test_agent/graph.py")
        
    else:
        print("   No MCP suggestions found")


def update_env_example(agent_root: Path, env_vars: list):
    """Update .env.example with required MCP environment variables."""
    env_example_path = agent_root / ".env.example"
    
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add MCP section
        mcp_section = "\n# MCP Integration Environment Variables\n"
        for var in env_vars:
            mcp_section += f"{var}=your_{var.lower()}_here\n"
        
        with open(env_example_path, 'w', encoding='utf-8') as f:
            f.write(content + mcp_section)
        
        print(f"   📝 Updated .env.example with MCP variables")


if __name__ == "__main__":
    main()