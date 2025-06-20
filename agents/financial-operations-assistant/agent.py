"""
Financial Operations Assistant Agent
Automates routine financial reporting for small businesses and teams.

Features:
- Fetches real financial data from Xero API
- Adds market context via Perplexity research
- Generates structured reports in Notion
- Sends notifications via Slack
- Supports flexible natural language requests
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Annotated, TypedDict, Optional
from dotenv import load_dotenv

from langchain_core.messages import (
    AnyMessage, BaseMessage, HumanMessage, AIMessage, ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Import direct API integrations (now fixed in core)
from core.integrations.xero.tools import (
    get_xero_profit_and_loss,
    get_xero_balance_sheet,
    get_xero_trial_balance
)
from core.integrations.notion.tools import (
    create_notion_page,
    get_notion_page,
    update_notion_page
)
from core.integrations.perplexity.tools import (
    perplexity_market_research,
    perplexity_research,
    perplexity_ask
)
from core.integrations.slack.tools import get_slack_tools

# --- Agent State ---
class FinancialAgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    request_type: str  # "scheduled", "slack_command", "manual"
    reporting_period: str  # "weekly", "monthly", "quarterly", "custom"
    date_range: Dict[str, str]  # {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}
    financial_data: Dict[str, Any]
    market_context: str
    report_url: Optional[str]
    slack_channel: Optional[str]
    error_messages: List[str]

# --- Tool Setup ---
financial_tools = [
    get_xero_profit_and_loss,   # Now fixed in core integration
    get_xero_balance_sheet,
    get_xero_trial_balance,
    create_notion_page,
    perplexity_market_research,
    perplexity_research,
    perplexity_ask
]

# Add Slack tools
slack_tools = get_slack_tools()
all_tools = financial_tools + slack_tools
tool_map = {tool.name: tool for tool in all_tools}

# --- Model Setup ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)

# --- System Prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""You are a Financial Operations Assistant that automates routine financial reporting for small businesses.

**Today's Date**: {current_date}

**Your Capabilities**:
- Fetch real financial data from Xero (P&L, balance sheets, invoices)
- Research market trends and context via Perplexity
- Generate structured reports in Notion with analysis
- Send notifications and summaries via Slack
- Process natural language requests for flexible reporting

**Available Tools**:
{len(all_tools)} tools for financial data, research, reporting, and communication.

**Core Workflow**:
1. Parse user request to understand reporting needs
2. Fetch relevant financial data from Xero
3. Add market context and insights via Perplexity
4. Generate comprehensive report in Notion
5. Notify stakeholders via Slack with summary

**Data Transparency Rules**:
- ALWAYS use the actual financial data from tool responses
- NEVER make up or simulate financial numbers 
- If tool returns real data, use those exact numbers in your response
- Be honest about data availability and limitations
- Clearly indicate when using fallback or simulated data

**Instructions**:
- Process requests in natural language (e.g., "show Q2 performance", "weekly report")
- CRITICAL: Always extract and use the exact financial numbers from tool responses
- If a tool returns financial_data with revenue, expenses, etc., use those EXACT numbers
- Provide comprehensive analysis with market context
- Generate professional reports with clear insights
- Handle errors gracefully with transparent messaging

**Safety & Accuracy**:
- Verify financial data accuracy before reporting
- Include appropriate disclaimers for market analysis
- Respect data privacy and security requirements
- Provide actionable insights and recommendations
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# --- Workflow Nodes ---

def parse_request_node(state: FinancialAgentState) -> FinancialAgentState:
    """Parse the user request to extract reporting requirements."""
    print("📋 Parsing financial reporting request...")
    
    # Get the last human message
    last_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break
    
    if not last_message:
        return {
            **state,
            "error_messages": ["No user request found to parse"]
        }
    
    # Simple natural language parsing
    request_lower = last_message.lower()
    
    # Determine reporting period
    if any(term in request_lower for term in ["q1", "q2", "q3", "q4", "quarter"]):
        reporting_period = "quarterly"
    elif any(term in request_lower for term in ["month", "monthly"]):
        reporting_period = "monthly"
    elif any(term in request_lower for term in ["week", "weekly"]):
        reporting_period = "weekly"
    else:
        reporting_period = "monthly"  # default
    
    # Calculate date range based on period
    today = datetime.now()
    if reporting_period == "quarterly":
        # Current quarter YTD
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        from_date = datetime(today.year, quarter_start_month, 1)
        to_date = today
    elif reporting_period == "weekly":
        # Last 7 days
        from_date = today - timedelta(days=7)
        to_date = today
    else:  # monthly
        # Current month YTD
        from_date = datetime(today.year, today.month, 1)
        to_date = today
    
    date_range = {
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d")
    }
    
    # Determine request type
    request_type = "manual"  # Default for now
    if "@financebot" in request_lower or "slack" in request_lower:
        request_type = "slack_command"
    
    print(f"✅ Parsed request: {reporting_period} report from {date_range['from']} to {date_range['to']}")
    
    return {
        **state,
        "request_type": request_type,
        "reporting_period": reporting_period,
        "date_range": date_range
    }

def agent_node(state: FinancialAgentState) -> FinancialAgentState:
    """Main agent node that decides which tools to call."""
    print("🤖 Agent analyzing financial reporting needs...")
    
    # Format the prompt with current state
    messages = prompt.format_messages(messages=state["messages"])
    
    # Get agent response
    response = llm_with_tools.invoke(messages)
    
    return {
        **state,
        "messages": state["messages"] + [response]
    }

def tools_node(state: FinancialAgentState) -> FinancialAgentState:
    """Execute tool calls from the agent."""
    print("🔧 Executing financial tools...")
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return state
    
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        print(f"📊 Executing {tool_name} with args: {tool_args}")
        
        try:
            if tool_name in tool_map:
                result = tool_map[tool_name].invoke(tool_args)
                
                # Store financial data in state
                if tool_name in ["get_xero_profit_and_loss", "get_xero_balance_sheet", "get_xero_trial_balance"]:
                    if "financial_data" not in state:
                        state["financial_data"] = {}
                    state["financial_data"][tool_name] = result
                    
                    # Check if result indicates real data or error  
                    if isinstance(result, str):
                        try:
                            import json
                            data = json.loads(result)
                            
                            # Check for mock data indicators
                            data_source = data.get("data_source", "")
                            if "Mock Data" in data_source or "Error:" in result or "failed:" in result:
                                print(f"⚠️ {tool_name}: Using fallback data due to API issues")
                            else:
                                print(f"✅ {tool_name}: Real Xero data retrieved")
                                # Show key financial metric if available
                                if data.get("financial_data"):
                                    revenue = data["financial_data"].get("total_revenue")
                                    net_income = data["financial_data"].get("net_income")
                                    if revenue:
                                        print(f"📊 Real Data - Revenue: ${revenue:,.2f}, Net Income: ${net_income:,.2f}")
                        except:
                            # Fallback for non-JSON responses
                            if "Mock Data" in result or "Error:" in result or "failed:" in result:
                                print(f"⚠️ {tool_name}: Using fallback data due to API issues")
                            else:
                                print(f"✅ {tool_name}: Real Xero data retrieved")
                
                # Store market context
                elif tool_name in ["perplexity_market_research", "perplexity_research", "perplexity_ask"]:
                    state["market_context"] = result
                
                # Store report URL
                elif tool_name == "create_notion_page":
                    try:
                        result_json = json.loads(result)
                        if "url" in result_json:
                            state["report_url"] = result_json["url"]
                    except:
                        pass
                
                tool_messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id
                ))
                
            else:
                error_msg = f"Tool {tool_name} not found"
                print(f"❌ {error_msg}")
                tool_messages.append(ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_call_id
                ))
                
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            print(f"❌ {error_msg}")
            if "error_messages" not in state:
                state["error_messages"] = []
            state["error_messages"].append(error_msg)
            
            tool_messages.append(ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id
            ))
    
    return {
        **state,
        "messages": state["messages"] + tool_messages
    }

def should_continue(state: FinancialAgentState) -> str:
    """Determine if we should continue or end."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, go to tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # Count total AI messages to prevent infinite loops
    ai_messages = sum(1 for msg in state["messages"] if isinstance(msg, AIMessage))
    
    # End after reasonable number of exchanges
    if ai_messages >= 4:  # Reduced from 6 to 4 
        return END
    
    # Check if we've done meaningful work (created report, sent notifications)
    tool_messages = [msg for msg in state["messages"] if isinstance(msg, ToolMessage)]
    
    # If we've executed multiple tools and have AI responses, we're likely done
    if len(tool_messages) >= 2 and ai_messages >= 3:
        return END
    
    # Continue with agent for initial exchanges
    return "agent"

# --- Graph Construction ---
def create_financial_agent():
    """Create the financial operations assistant graph."""
    
    # Create the graph
    workflow = StateGraph(FinancialAgentState)
    
    # Add nodes
    workflow.add_node("parse_request", parse_request_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    # Set entry point
    workflow.set_entry_point("parse_request")
    
    # Add edges
    workflow.add_edge("parse_request", "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# Initialize the graph
graph = create_financial_agent()

# --- Main Execution ---
def main():
    """Interactive execution for testing the Financial Operations Assistant."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "XERO_ACCESS_TOKEN", 
        "XERO_TENANT_ID",
        "PERPLEXITY_API_KEY",
        "NOTION_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please configure your .env file with the required API keys.")
        return
    
    print("✅ Financial Operations Assistant is ready!")
    print(f"📅 Today's date: {current_date}")
    print(f"🔧 Tools available: {len(all_tools)}")
    print("\n💡 Try requests like:")
    print("  - 'Generate monthly financial report'")
    print("  - 'Show me Q2 performance with market context'")
    print("  - 'Create weekly summary for the team'")
    print("\n💬 Type 'quit' to exit\n")
    
    while True:
        user_input = input("👤 Request: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Financial Operations Assistant shutting down!")
            break
        
        if not user_input:
            continue
        
        print("🏦 Processing financial reporting request...")
        
        try:
            # Create initial state
            initial_state = FinancialAgentState(
                messages=[HumanMessage(content=user_input)],
                request_type="manual",
                reporting_period="monthly",
                date_range={"from": "", "to": ""},
                financial_data={},
                market_context="",
                report_url=None,
                slack_channel=None,
                error_messages=[]
            )
            
            # Run the workflow with recursion limit
            result = graph.invoke(initial_state, {"recursion_limit": 10})
            
            # Display results
            final_message = result["messages"][-1]
            print(f"\n🤖 Financial Assistant: {final_message.content}")
            
            # Show additional info if available
            if result.get("report_url"):
                print(f"📄 Report created: {result['report_url']}")
            
            if result.get("error_messages"):
                print("⚠️ Errors encountered:")
                for error in result["error_messages"]:
                    print(f"  - {error}")
            
            print("---\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---\n")

if __name__ == "__main__":
    main()