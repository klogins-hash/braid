#!/usr/bin/env python3
"""
MCP-Enabled Agent Template
A template for creating agents with Model Context Protocol (MCP) integration.
"""

import os
import sys
import json
import subprocess
import signal
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()

class MCPClient:
    """Client for communicating with MCP servers via stdio."""
    
    def __init__(self, server_path: str, server_args: list = None, env_vars: dict = None):
        self.server_path = server_path
        self.server_args = server_args or []
        self.env_vars = env_vars or {}
        self.process = None
        self.initialized = False
        
    def start(self) -> bool:
        """Start the MCP server process."""
        env = os.environ.copy()
        env.update(self.env_vars)
        
        cmd = [self.server_path] + self.server_args
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            return True
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the MCP connection."""
        if not self.process or self.initialized:
            return self.initialized
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            self.process.stdin.write(json.dumps(init_request) + "\n")
            self.process.stdin.flush()
            
            response = self.process.stdout.readline()
            data = json.loads(response)
            
            if "result" in data:
                self.initialized = True
                return True
            else:
                print(f"MCP initialization failed: {data}")
                return False
                
        except Exception as e:
            print(f"MCP initialization error: {e}")
            return False
    
    def send_request(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process or not self.initialized:
            return {"error": "MCP server not initialized"}
        
        request = {
            "jsonrpc": "2.0",
            "id": datetime.now().microsecond,  # Unique ID
            "method": method,
            "params": params or {}
        }
        
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            response = self.process.stdout.readline()
            return json.loads(response)
        except Exception as e:
            return {"error": str(e)}
    
    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a specific tool on the MCP server."""
        response = self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "result" in response:
            return response["result"]
        else:
            return {"error": response.get("error", "Unknown error")}
    
    def list_tools(self) -> List[dict]:
        """List available tools from the MCP server."""
        response = self.send_request("tools/list")
        
        if "result" in response:
            return response["result"].get("tools", [])
        else:
            return []
    
    def stop(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.initialized = False

class MCPManager:
    """Manager for multiple MCP clients."""
    
    def __init__(self):
        self.clients = {}
        self.setup_clients()
    
    def setup_clients(self):
        """Setup MCP clients based on available environment variables."""
        
        # Setup Xero MCP
        if os.getenv('XERO_ACCESS_TOKEN'):
            self.clients['xero'] = MCPClient(
                server_path="node",
                server_args=["mcp_servers/xero/dist/index.js"],
                env_vars={
                    "XERO_CLIENT_BEARER_TOKEN": os.getenv('XERO_ACCESS_TOKEN'),
                    "XERO_CLIENT_ID": os.getenv('XERO_CLIENT_ID', ''),
                    "XERO_CLIENT_SECRET": os.getenv('XERO_CLIENT_SECRET', '')
                }
            )
        
        # Setup Notion MCP
        if os.getenv('NOTION_API_KEY'):
            self.clients['notion'] = MCPClient(
                server_path="node",
                server_args=["mcp_servers/notion/bin/cli.mjs"],
                env_vars={"NOTION_API_KEY": os.getenv('NOTION_API_KEY')}
            )
    
    def start_all(self) -> Dict[str, bool]:
        """Start all MCP clients."""
        results = {}
        for name, client in self.clients.items():
            started = client.start()
            if started:
                initialized = client.initialize()
                results[name] = initialized
                if initialized:
                    print(f"✅ {name.title()} MCP client started and initialized")
                else:
                    print(f"❌ {name.title()} MCP client started but failed to initialize")
            else:
                results[name] = False
                print(f"❌ {name.title()} MCP client failed to start")
        return results
    
    def stop_all(self):
        """Stop all MCP clients."""
        for name, client in self.clients.items():
            client.stop()
            print(f"🛑 {name.title()} MCP client stopped")
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get a specific MCP client."""
        return self.clients.get(name)

# Global MCP manager
mcp_manager = MCPManager()

# Define MCP-powered tools
@tool
def get_financial_data(report_type: str = "profit_and_loss") -> str:
    """Get financial data from Xero accounting system.
    
    Args:
        report_type: Type of financial report (profit_and_loss, balance_sheet, etc.)
        
    Returns:
        Financial data in structured format
    """
    xero_client = mcp_manager.get_client('xero')
    if not xero_client:
        return "Xero MCP not available"
    
    # Map report types to Xero MCP tool names
    tool_mapping = {
        "profit_and_loss": "list-xero-profit-and-loss",
        "balance_sheet": "list-xero-report-balance-sheet",
        "trial_balance": "list-xero-trial-balance"
    }
    
    tool_name = tool_mapping.get(report_type, "list-xero-profit-and-loss")
    
    result = xero_client.call_tool(tool_name, {})
    
    if "error" not in result:
        return json.dumps(result, indent=2)
    else:
        return f"Financial data retrieval failed: {result.get('error', 'Unknown error')}"

@tool
def create_notion_page(title: str, content: str, parent_page_id: str = None) -> str:
    """Create a new page in Notion workspace.
    
    Args:
        title: Title of the new page
        content: Content to add to the page
        parent_page_id: Optional parent page ID (uses default if not provided)
        
    Returns:
        Success message with page URL or error message
    """
    notion_client = mcp_manager.get_client('notion')
    if not notion_client:
        return "Notion MCP not available"
    
    # Use a default parent page ID if not provided
    if not parent_page_id:
        parent_page_id = os.getenv('NOTION_DEFAULT_PAGE_ID', 'your-default-page-id')
    
    result = notion_client.call_tool("API-post-page", {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [{"text": {"content": title}}]
        },
        "children": [content]
    })
    
    if "error" not in result:
        page_id = result.get("id", "unknown")
        return f"Page created successfully with ID: {page_id}"
    else:
        return f"Page creation failed: {result.get('error', 'Unknown error')}"

@tool
def search_notion_workspace(query: str) -> str:
    """Search for content in Notion workspace.
    
    Args:
        query: Search query
        
    Returns:
        Search results from Notion
    """
    notion_client = mcp_manager.get_client('notion')
    if not notion_client:
        return "Notion MCP not available"
    
    result = notion_client.call_tool("API-post-search", {
        "query": query
    })
    
    if "results" in result:
        return json.dumps(result["results"], indent=2)
    else:
        return f"Search failed: {result.get('error', 'Unknown error')}"

# Define agent state
class AgentState:
    """State for the MCP-enabled agent."""
    def __init__(self):
        self.messages = []
        self.current_task = ""
        self.mcp_data = {}
        self.final_response = ""

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Define agent nodes
def agent_node(state: AgentState) -> AgentState:
    """Main agent reasoning node."""
    # Bind tools to the LLM
    tools = [get_financial_data, create_notion_page, search_notion_workspace]
    llm_with_tools = llm.bind_tools(tools)
    
    # Get the latest message
    if state.messages:
        response = llm_with_tools.invoke(state.messages)
        state.messages.append(response)
    
    return state

def tool_node(state: AgentState) -> AgentState:
    """Execute tools called by the agent."""
    # This would be handled by LangGraph's ToolNode
    return state

def final_response_node(state: AgentState) -> AgentState:
    """Generate final response."""
    if state.messages:
        last_message = state.messages[-1]
        if hasattr(last_message, 'content'):
            state.final_response = last_message.content
    
    return state

# Create the graph
def create_agent_graph():
    """Create the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode([get_financial_data, create_notion_page, search_notion_workspace]))
    workflow.add_node("final_response", final_response_node)
    
    # Define edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        lambda state: "tools" if state.messages and hasattr(state.messages[-1], 'tool_calls') and state.messages[-1].tool_calls else "final_response"
    )
    workflow.add_edge("tools", "agent")
    workflow.add_edge("final_response", END)
    
    return workflow.compile()

class MCPAgent:
    """Main MCP-enabled agent class."""
    
    def __init__(self):
        self.graph = create_agent_graph()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def startup(self) -> bool:
        """Start the agent and all MCP servers."""
        print("🚀 Starting MCP-enabled agent...")
        
        # Start MCP clients
        results = mcp_manager.start_all()
        
        if not any(results.values()):
            print("❌ No MCP servers started. Check your environment variables.")
            return False
        
        working_servers = [name for name, status in results.items() if status]
        print(f"✅ Agent started with {len(working_servers)} MCP servers: {', '.join(working_servers)}")
        
        return True
    
    def shutdown(self):
        """Shutdown the agent and all MCP servers."""
        print("🛑 Shutting down MCP agent...")
        mcp_manager.stop_all()
        print("✅ Agent shutdown complete")
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input."""
        # Create initial state
        state = AgentState()
        state.messages = [{"role": "user", "content": user_input}]
        state.current_task = user_input
        
        # Run the graph
        try:
            final_state = self.graph.invoke(state)
            return final_state.final_response
        except Exception as e:
            return f"Agent execution failed: {e}"
    
    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print("\n🤖 MCP Agent Interactive Mode")
        print("Type 'quit' to exit, 'help' for available commands")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif not user_input:
                    continue
                
                print("\n🤖 Agent: ", end="")
                response = self.run(user_input)
                print(response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        print("\n👋 Goodbye!")
    
    def show_help(self):
        """Show help information."""
        print("\n📚 Available Commands:")
        print("  help     - Show this help message")
        print("  status   - Show MCP server status")
        print("  quit     - Exit the agent")
        print("\n🔧 Available Capabilities:")
        print("  💰 Financial data via Xero MCP")
        print("  📝 Notion workspace management")
        print("\n💡 Example queries:")
        print("  'Research the latest AI trends'")
        print("  'Get my company's profit and loss report'")
        print("  'Create a summary report in Notion'")
    
    def show_status(self):
        """Show status of MCP servers."""
        print("\n📊 MCP Server Status:")
        for name, client in mcp_manager.clients.items():
            if client.process and client.initialized:
                status = "🟢 Running"
            elif client.process:
                status = "🟡 Started but not initialized"
            else:
                status = "🔴 Stopped"
            
            tools_count = len(client.list_tools()) if client.initialized else 0
            print(f"  {name.title()}: {status} ({tools_count} tools)")

def main():
    """Main entry point."""
    print("🤖 MCP-Enabled Agent Template")
    print("=" * 40)
    
    # Create and start the agent
    agent = MCPAgent()
    
    if not agent.startup():
        print("❌ Failed to start agent")
        sys.exit(1)
    
    try:
        # Run in interactive mode
        agent.interactive_mode()
    finally:
        # Ensure cleanup
        agent.shutdown()

if __name__ == "__main__":
    main()