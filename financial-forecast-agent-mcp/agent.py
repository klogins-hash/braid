#!/usr/bin/env python3
"""
Financial Forecasting Agent with MCP Integration
6-step workflow: Xero Data → Client Info → Market Research → Assumptions → Forecast → Notion Report
"""

import os
import sys
import json
import subprocess
import signal
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.error(f"Failed to start MCP server: {e}")
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
                    "name": "financial-forecast-agent",
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
                logger.error(f"MCP initialization failed: {data}")
                return False
                
        except Exception as e:
            logger.error(f"MCP initialization error: {e}")
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
        # Setup Perplexity MCP for market research
        if os.getenv('PERPLEXITY_API_KEY'):
            self.clients['perplexity'] = MCPClient(
                server_path="node",
                server_args=["mcp_servers/perplexity/perplexity-ask/dist/index.js"],
                env_vars={"PERPLEXITY_API_KEY": os.getenv('PERPLEXITY_API_KEY')}
            )
        
        # Setup Xero MCP for financial data
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
        
        # Setup Notion MCP for report generation
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
                    logger.info(f"✅ {name.title()} MCP client started and initialized")
                else:
                    logger.error(f"❌ {name.title()} MCP client started but failed to initialize")
            else:
                results[name] = False
                logger.error(f"❌ {name.title()} MCP client failed to start")
        return results
    
    def stop_all(self):
        """Stop all MCP clients."""
        for name, client in self.clients.items():
            client.stop()
            logger.info(f"🛑 {name.title()} MCP client stopped")
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get a specific MCP client."""
        return self.clients.get(name)

# Global MCP manager
mcp_manager = MCPManager()

# Agent state definition
class ForecastAgentState(BaseModel):
    """State for the financial forecasting agent."""
    messages: List[Any] = []
    current_step: str = "start"
    user_id: str = "user_123"
    xero_data: Optional[Dict] = None
    client_info: Optional[Dict] = None
    market_research: Optional[str] = None
    forecast_assumptions: Optional[Dict] = None
    forecast_results: Optional[Dict] = None
    notion_report_url: Optional[str] = None
    workflow_complete: bool = False
    
    class Config:
        arbitrary_types_allowed = True

# Define MCP-powered tools for financial forecasting
@tool
def get_xero_financial_data(report_type: str = "profit_and_loss", user_id: str = "user_123") -> str:
    """Retrieve financial data from Xero MCP server.
    
    Args:
        report_type: Type of financial report (profit_and_loss, balance_sheet, trial_balance)
        user_id: User identifier for the forecast
        
    Returns:
        Financial data in structured format
    """
    xero_client = mcp_manager.get_client('xero')
    if not xero_client:
        return "Xero MCP not available - using simulated data for testing"
    
    # Map report types to Xero MCP tool names
    tool_mapping = {
        "profit_and_loss": "list-xero-profit-and-loss",
        "balance_sheet": "list-xero-report-balance-sheet",
        "trial_balance": "list-xero-trial-balance"
    }
    
    tool_name = tool_mapping.get(report_type, "list-xero-profit-and-loss")
    
    try:
        result = xero_client.call_tool(tool_name, {})
        
        if "error" not in str(result):
            logger.info(f"✅ Retrieved {report_type} data from Xero MCP")
            return json.dumps(result, indent=2)
        else:
            logger.warning(f"⚠️ Xero MCP error, using simulated data: {result}")
            return f"Simulated {report_type} data for {user_id}: Revenue growth 15%, expenses stable"
    except Exception as e:
        logger.error(f"❌ Xero MCP call failed: {e}")
        return f"Error retrieving Xero data, using simulated data for {user_id}"

@tool
def conduct_market_research(industry: str = "Software Development", location: str = "San Francisco, CA") -> str:
    """Conduct market research using Perplexity MCP.
    
    Args:
        industry: Industry to research
        location: Geographic location for market analysis
        
    Returns:
        Market research insights and trends
    """
    perplexity_client = mcp_manager.get_client('perplexity')
    if not perplexity_client:
        return f"Perplexity MCP not available - simulated market research for {industry} in {location}"
    
    research_query = f"What are the current market trends and 5-year growth outlook for the {industry} industry in {location}? Include economic factors, opportunities, and challenges."
    
    try:
        result = perplexity_client.call_tool("perplexity_research", {
            "messages": [{
                "role": "user", 
                "content": research_query
            }]
        })
        
        if "content" in str(result):
            logger.info(f"✅ Completed market research for {industry}")
            # Extract content from result
            content = result.get("content", [])
            if content and isinstance(content, list) and len(content) > 0:
                return content[0].get("text", str(result))
            return str(result)
        else:
            logger.warning(f"⚠️ Perplexity MCP error: {result}")
            return f"Simulated market research: {industry} in {location} showing 12% annual growth with strong digital transformation trends"
    except Exception as e:
        logger.error(f"❌ Perplexity MCP call failed: {e}")
        return f"Error in market research, using simulated data for {industry} in {location}"

@tool
def create_forecast_assumptions(historical_data: str, market_research: str, client_info: str) -> str:
    """Generate forecast assumptions based on historical data and market research.
    
    Args:
        historical_data: Historical financial data from Xero
        market_research: Market insights from research
        client_info: Client business information
        
    Returns:
        Structured forecast assumptions
    """
    assumptions = {
        "revenue_growth_rate": "15%",
        "cost_of_goods_sold": "35%",
        "operating_expense_growth": "8%",
        "tax_rate": "25%",
        "depreciation_rate": "10%",
        "market_factors": "Positive growth outlook based on industry trends",
        "risk_factors": "Economic uncertainty, competition, technology changes",
        "growth_drivers": "Digital transformation, market expansion, new products"
    }
    
    logger.info("✅ Generated forecast assumptions")
    return json.dumps(assumptions, indent=2)

@tool  
def calculate_financial_forecast(historical_data: str, assumptions: str) -> str:
    """Calculate 5-year financial forecast using historical data and assumptions.
    
    Args:
        historical_data: Historical financial data
        assumptions: Forecast assumptions
        
    Returns:
        5-year financial projections
    """
    # Simplified forecast calculation for demo
    forecast = {
        "year_1": {"revenue": 1150000, "expenses": 920000, "net_income": 230000},
        "year_2": {"revenue": 1322500, "expenses": 1057600, "net_income": 264900},
        "year_3": {"revenue": 1520875, "experiences": 1214208, "net_income": 306667},
        "year_4": {"revenue": 1749006, "expenses": 1399205, "net_income": 349801},
        "year_5": {"revenue": 2011357, "expenses": 1609086, "net_income": 402271}
    }
    
    logger.info("✅ Calculated 5-year financial forecast")
    return json.dumps(forecast, indent=2)

@tool
def create_notion_report(forecast_data: str, assumptions: str, market_research: str) -> str:
    """Create comprehensive financial forecast report in Notion.
    
    Args:
        forecast_data: Financial forecast results
        assumptions: Forecast assumptions
        market_research: Market research insights
        
    Returns:
        Notion page URL or confirmation
    """
    notion_client = mcp_manager.get_client('notion')
    if not notion_client:
        return "Notion MCP not available - report content generated for local use"
    
    # Create comprehensive report content
    report_content = f"""# Financial Forecast Report

## Executive Summary
5-year financial forecast showing strong growth trajectory with 15% annual revenue growth.

## Historical Analysis
{forecast_data}

## Market Research Insights
{market_research}

## Key Assumptions
{assumptions}

## Forecast Results
Detailed 5-year projections with scenario analysis.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        # Use default parent page ID or get from environment
        parent_page_id = os.getenv('NOTION_DEFAULT_PAGE_ID', 'default-page-id')
        
        result = notion_client.call_tool("API-post-page", {
            "parent": {"page_id": parent_page_id},
            "properties": {
                "title": [{"text": {"content": f"Financial Forecast - {datetime.now().strftime('%Y-%m-%d')}"}}]
            },
            "children": [report_content]
        })
        
        if "error" not in str(result):
            page_id = result.get("id", "unknown")
            logger.info(f"✅ Created Notion report with ID: {page_id}")
            return f"Notion report created successfully with ID: {page_id}"
        else:
            logger.warning(f"⚠️ Notion MCP error: {result}")
            return f"Report content generated (Notion creation failed): {report_content[:200]}..."
    except Exception as e:
        logger.error(f"❌ Notion MCP call failed: {e}")
        return f"Report content generated locally: {report_content[:200]}..."

@tool
def get_client_information(user_id: str = "user_123") -> str:
    """Get client business information for forecasting.
    
    Args:
        user_id: User identifier
        
    Returns:
        Client business information
    """
    # Simulated client data - in production this would come from a database
    client_info = {
        "user_id": user_id,
        "company_name": "Northeast Logistics Co",
        "industry": "Software Development",
        "business_age": "5 years",
        "location": "San Francisco, CA",
        "business_strategy": "Aggressive growth through digital transformation",
        "employees": 25,
        "current_revenue": "1M annually"
    }
    
    logger.info(f"✅ Retrieved client information for {user_id}")
    return json.dumps(client_info, indent=2)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Financial Forecasting Agent
class FinancialForecastAgent:
    """6-step financial forecasting agent with MCP integration."""
    
    def __init__(self):
        self.graph = self.create_agent_graph()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def startup(self) -> bool:
        """Start the agent and all MCP servers."""
        logger.info("🚀 Starting Financial Forecasting Agent with MCP integration...")
        
        # Start MCP clients
        results = mcp_manager.start_all()
        
        working_servers = [name for name, status in results.items() if status]
        logger.info(f"✅ Agent started with {len(working_servers)} MCP servers: {', '.join(working_servers)}")
        
        return True
    
    def shutdown(self):
        """Shutdown the agent and all MCP servers."""
        logger.info("🛑 Shutting down Financial Forecasting Agent...")
        mcp_manager.stop_all()
        logger.info("✅ Agent shutdown complete")
    
    def create_agent_graph(self):
        """Create the 6-step financial forecasting workflow."""
        # Define all tools
        tools = [
            get_xero_financial_data,
            get_client_information, 
            conduct_market_research,
            create_forecast_assumptions,
            calculate_financial_forecast,
            create_notion_report
        ]
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Define workflow nodes
        def step_1_xero_data(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 1: Retrieve financial data from Xero."""
            logger.info("📊 Step 1: Retrieving Xero financial data...")
            
            prompt = f"""You are a financial forecasting agent. Execute Step 1 of the forecasting workflow.

STEP 1: Retrieve Financial Data from Xero
- Use get_xero_financial_data tool to get profit_and_loss data for user {state.user_id}
- This provides the historical baseline for our forecast

Call the tool now to retrieve the Xero financial data."""
            
            messages = [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "step_2"
            }
        
        def step_2_client_info(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 2: Get client business information."""
            logger.info("🏢 Step 2: Getting client information...")
            
            prompt = f"""STEP 2: Get Client Business Information
- Use get_client_information tool to retrieve business details for user {state.user_id}
- This provides context about the business for accurate forecasting

Call the tool now to get client information."""
            
            messages = state.messages + [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "step_3"
            }
        
        def step_3_market_research(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 3: Conduct market research."""
            logger.info("🔍 Step 3: Conducting market research...")
            
            prompt = """STEP 3: Conduct Market Research
- Use conduct_market_research tool to analyze industry trends
- Focus on Software Development industry in San Francisco, CA
- This provides market context for forecast assumptions

Call the tool now to conduct market research."""
            
            messages = state.messages + [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "step_4"
            }
        
        def step_4_assumptions(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 4: Generate forecast assumptions."""
            logger.info("📋 Step 4: Generating forecast assumptions...")
            
            prompt = """STEP 4: Generate Forecast Assumptions
- Use create_forecast_assumptions tool to generate assumptions
- Base assumptions on the historical data, client info, and market research from previous steps
- Provide the data from previous steps as arguments

Call the tool now to create forecast assumptions."""
            
            messages = state.messages + [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "step_5"
            }
        
        def step_5_calculate_forecast(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 5: Calculate financial forecast."""
            logger.info("📈 Step 5: Calculating financial forecast...")
            
            prompt = """STEP 5: Calculate Financial Forecast
- Use calculate_financial_forecast tool to generate 5-year projections
- Use the historical data and assumptions from previous steps
- This creates the core forecast results

Call the tool now to calculate the financial forecast."""
            
            messages = state.messages + [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "step_6"
            }
        
        def step_6_create_report(state: ForecastAgentState) -> Dict[str, Any]:
            """Step 6: Create comprehensive Notion report."""
            logger.info("📄 Step 6: Creating Notion report...")
            
            prompt = """STEP 6: Create Notion Report
- Use create_notion_report tool to generate comprehensive forecast report
- Include forecast data, assumptions, and market research from previous steps
- This creates the final deliverable

Call the tool now to create the Notion report."""
            
            messages = state.messages + [HumanMessage(content=prompt)]
            response = llm_with_tools.invoke(messages)
            
            return {
                "messages": state.messages + [response],
                "current_step": "complete",
                "workflow_complete": True
            }
        
        # Tool execution node
        def execute_tools(state: ForecastAgentState) -> Dict[str, Any]:
            """Execute tools called by the agent."""
            tool_node = ToolNode(tools)
            result = tool_node.invoke(state)
            return result
        
        # Routing function
        def should_continue(state: ForecastAgentState) -> str:
            """Determine next step in workflow."""
            messages = state.messages
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "execute_tools"
            
            current_step = state.current_step
            if current_step == "start":
                return "step_1"
            elif current_step == "step_2":
                return "step_2_client_info"
            elif current_step == "step_3":
                return "step_3_market_research"
            elif current_step == "step_4":
                return "step_4_assumptions"
            elif current_step == "step_5":
                return "step_5_calculate_forecast"
            elif current_step == "step_6":
                return "step_6_create_report"
            elif current_step == "complete":
                return END
            else:
                return "step_1"
        
        # Build the graph
        workflow = StateGraph(ForecastAgentState)
        
        # Add nodes
        workflow.add_node("step_1", step_1_xero_data)
        workflow.add_node("step_2_client_info", step_2_client_info)
        workflow.add_node("step_3_market_research", step_3_market_research)
        workflow.add_node("step_4_assumptions", step_4_assumptions)
        workflow.add_node("step_5_calculate_forecast", step_5_calculate_forecast)
        workflow.add_node("step_6_create_report", step_6_create_report)
        workflow.add_node("execute_tools", execute_tools)
        
        # Add edges
        workflow.set_entry_point("step_1")
        
        # Add conditional edges
        for step in ["step_1", "step_2_client_info", "step_3_market_research", 
                    "step_4_assumptions", "step_5_calculate_forecast", "step_6_create_report"]:
            workflow.add_conditional_edges(step, should_continue)
        
        workflow.add_edge("execute_tools", "step_1")  # Return to routing after tool execution
        
        return workflow.compile()
    
    def run_forecast(self, user_id: str = "user_123") -> str:
        """Run the complete 6-step forecasting workflow."""
        logger.info(f"🚀 Starting financial forecast for user: {user_id}")
        
        # Create initial state
        initial_state = ForecastAgentState(
            messages=[HumanMessage(content=f"Create a financial forecast for user {user_id}")],
            current_step="start",
            user_id=user_id
        )
        
        try:
            # Run the workflow
            final_state = self.graph.invoke(initial_state)
            
            # Extract final response
            if final_state.messages:
                final_message = final_state.messages[-1]
                result = f"✅ Financial forecast completed for {user_id}\n\n"
                if hasattr(final_message, 'content'):
                    result += final_message.content
                else:
                    result += str(final_message)
                return result
            else:
                return f"✅ Financial forecast workflow completed for {user_id}"
                
        except Exception as e:
            logger.error(f"❌ Forecast workflow failed: {e}")
            return f"❌ Forecast failed for {user_id}: {e}"
    
    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print("\n💰 Financial Forecasting Agent with MCP Integration")
        print("=" * 60)
        print("📊 6-Step Workflow: Xero → Client Info → Market Research → Assumptions → Forecast → Notion Report")
        print("🔌 MCP Servers: Perplexity (research), Xero (financial data), Notion (reporting)")
        print("Type 'forecast' to run complete workflow, 'quit' to exit")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() in ['forecast', 'run', 'start']:
                    print("\n🚀 Starting 6-step financial forecasting workflow...")
                    result = self.run_forecast()
                    print(f"\n🤖 Result:\n{result}")
                elif user_input.lower() == 'status':
                    self.show_mcp_status()
                elif user_input.lower() == 'help':
                    self.show_help()
                elif not user_input:
                    continue
                else:
                    print("Commands: 'forecast' (run workflow), 'status' (MCP status), 'help', 'quit'")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
        
        print("\n👋 Goodbye!")
    
    def show_mcp_status(self):
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
    
    def show_help(self):
        """Show help information."""
        print("\n📚 Financial Forecasting Agent Help:")
        print("Commands:")
        print("  forecast - Run complete 6-step forecasting workflow")
        print("  status   - Show MCP server status")
        print("  help     - Show this help message")
        print("  quit     - Exit the agent")
        print("\n🔄 Workflow Steps:")
        print("  1. 📊 Retrieve Xero financial data")
        print("  2. 🏢 Get client business information")
        print("  3. 🔍 Conduct market research (Perplexity)")
        print("  4. 📋 Generate forecast assumptions")
        print("  5. 📈 Calculate 5-year financial forecast")
        print("  6. 📄 Create comprehensive Notion report")

def main():
    """Main entry point."""
    print("💰 Financial Forecasting Agent with MCP Integration")
    print("=" * 60)
    
    # Create and start the agent
    agent = FinancialForecastAgent()
    
    if not agent.startup():
        logger.error("❌ Failed to start agent")
        sys.exit(1)
    
    try:
        # Run in interactive mode
        agent.interactive_mode()
    finally:
        # Ensure cleanup
        agent.shutdown()

if __name__ == "__main__":
    main()