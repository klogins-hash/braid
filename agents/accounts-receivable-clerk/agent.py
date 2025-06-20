"""
Autonomous Accounts Receivable Clerk Agent
Automates the complete accounts receivable lifecycle from contract to cash collection.

Features:
- Monitors Google Drive for new signed contracts
- Extracts contract data using AI document parsing
- Creates clients and invoices in Xero accounting system
- Tracks payment status and automates collections
- Multi-stage escalation with email, SMS, and Slack notifications
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Annotated, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import (
    AnyMessage, HumanMessage, AIMessage, ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Import specialized AR tools
from xero_tools import get_xero_ar_tools
from contract_tools import get_contract_tools
from collections_tools import get_collections_tools

# Import core integrations for supplementary functionality
try:
    import sys
    sys.path.append('/Users/chasehughes/Documents/Github-hughes7370/braid-ink/braid')
    from core.integrations.productivity.perplexity.tools import (
        perplexity_ask,
        perplexity_research
    )
    from core.integrations.communication.slack.tools import get_slack_tools
    print("✅ Core integrations imported successfully")
except ImportError as e:
    print(f"⚠️ Core integrations not available: {e}")
    # Create mock tools for testing
    def mock_tool(name):
        from langchain_core.tools import tool
        @tool(name)
        def mock_func(query: str) -> str:
            return f"Mock {name} result for: {query}"
        return mock_func
    
    perplexity_ask = mock_tool("perplexity_ask")
    perplexity_research = mock_tool("perplexity_research")
    
    def get_slack_tools():
        return [mock_tool("slack_post_message")]

# --- Agent State ---
class ARClerkState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    contract_data: Dict[str, Any]           # Extracted contract information
    client_info: Dict[str, Any]             # Xero client details
    invoice_schedule: List[Dict[str, Any]]  # Billing timeline and milestones
    collection_status: Dict[str, Any]       # Overdue tracking and escalation
    processed_files: List[str]              # Track processed contracts
    current_action: str                     # Current workflow step
    error_messages: List[str]               # Error tracking

# --- Tool Setup ---
# Get specialized AR tools
xero_ar_tools = get_xero_ar_tools()
contract_tools = get_contract_tools()
collections_tools = get_collections_tools()

# Add supplementary tools
supplementary_tools = [
    perplexity_ask,
    perplexity_research
]

# Add Slack tools
slack_tools = get_slack_tools()

# Combine all tools
all_tools = xero_ar_tools + contract_tools + collections_tools + supplementary_tools + slack_tools
tool_map = {tool.name: tool for tool in all_tools}

# --- Model Setup ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)

# --- System Prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""You are an Autonomous Accounts Receivable Clerk that automates the complete lifecycle from contract to cash collection.

**Today's Date**: {current_date}

**Your Core Responsibilities**:
1. Monitor for new customer contracts in Google Drive
2. Extract contract data (client, services, billing terms, amounts)
3. Create clients and invoices in Xero accounting system
4. Track payment status and automate collections
5. Execute multi-stage collections with escalating communication

**Available Tools**:
{len(all_tools)} tools for document processing, financial management, and communication.

**Workflow Process**:
1. **Contract Monitoring**: Check designated Google Drive folder for new signed contracts
2. **Data Extraction**: Parse contract documents to extract billing information
3. **Client Management**: Check if client exists in Xero, create new contact if needed
4. **Invoice Creation**: Generate invoices based on contract billing terms
5. **Payment Tracking**: Monitor invoice payment status
6. **Collections Process**: Automated escalation for overdue accounts
   - Stage 1 (7+ days overdue): Polite email reminder
   - Stage 2 (14+ days overdue): Direct SMS reminder  
   - Stage 3 (30+ days overdue): Escalate to human via Slack

**Data Transparency Rules**:
- ALWAYS use actual data from tool responses
- NEVER simulate financial or client information
- Be transparent about data sources and API status
- Clearly indicate when using fallback processes

**Contract Data Extraction Requirements**:
When processing contracts, extract these critical fields:
- Client Name and Contact Information
- Service/Product Description
- Total Contract Value
- Billing Terms (Net 30, 50% upfront, etc.)
- Payment Schedule/Milestones
- Contract Start/End Dates

**Collections Escalation Protocol**:
- Stage 1: Professional email reminder with invoice copy
- Stage 2: Direct SMS to billing contact
- Stage 3: Slack notification to finance team with full account history
- Always maintain professional tone and complete audit trail

**Error Handling**:
- Gracefully handle API failures with clear messaging
- Escalate to human oversight when automation fails
- Maintain complete logs of all actions and communications
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# --- Workflow Nodes ---

def monitor_contracts_node(state: ARClerkState) -> ARClerkState:
    """Monitor Google Drive folder for new signed contracts."""
    print("📁 Monitoring Google Drive for new contracts...")
    
    # For now, simulate contract monitoring
    # In production, this would use Google Drive API to check designated folder
    
    # Check if we have a request to process a specific contract
    last_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break
    
    if not last_message:
        return {
            **state,
            "current_action": "monitoring",
            "error_messages": ["No contract processing request found"]
        }
    
    # Extract contract file information from user request
    if "contract" in last_message.lower() or "new client" in last_message.lower():
        print("📄 New contract detected for processing")
        return {
            **state,
            "current_action": "extract_contract_data"
        }
    
    return {
        **state,
        "current_action": "monitoring"
    }

def extract_contract_data_node(state: ARClerkState) -> ARClerkState:
    """Extract contract data using specialized contract parsing tools."""
    print("🔍 Extracting contract data using specialized AI parsing...")
    
    # Get the user's contract information
    last_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break
    
    if not last_message:
        return {
            **state,
            "error_messages": ["No contract content to process"]
        }
    
    try:
        # Use the specialized extract_contract_data tool
        from contract_tools import extract_contract_data
        contract_result = extract_contract_data.invoke({
            "contract_text": last_message,
            "client_context": None
        })
        
        # Parse the result
        import json
        contract_data = json.loads(contract_result)
        
        print(f"✅ Contract data extracted: {contract_data.get('client_name', 'Unknown')} - ${contract_data.get('total_value', 0):,.2f}")
        
        return {
            **state,
            "contract_data": contract_data,
            "current_action": "create_client_invoice"
        }
        
    except Exception as e:
        error_msg = f"Error extracting contract data: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error_messages": state.get("error_messages", []) + [error_msg],
            "current_action": "error_handling"
        }

def agent_node(state: ARClerkState) -> ARClerkState:
    """Main agent node that orchestrates the workflow."""
    print("🤖 AR Clerk analyzing current state and next actions...")
    
    # Format the prompt with current state
    messages = prompt.format_messages(messages=state["messages"])
    
    # Get agent response
    response = llm_with_tools.invoke(messages)
    
    return {
        **state,
        "messages": state["messages"] + [response]
    }

def tools_node(state: ARClerkState) -> ARClerkState:
    """Execute tool calls from the agent."""
    print("🔧 Executing AR tools...")
    
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
                
                # Handle Xero financial data
                if tool_name in ["get_xero_profit_and_loss", "get_xero_balance_sheet"]:
                    print(f"✅ {tool_name}: Retrieved financial data for AR analysis")
                
                # Handle communication tools
                elif tool_name in ["gmail_send_email", "slack_post_message"]:
                    print(f"📧 {tool_name}: Communication sent")
                
                # Handle document research
                elif tool_name in ["perplexity_ask", "perplexity_research"]:
                    print(f"🔍 {tool_name}: Research completed")
                
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

def create_client_invoice_node(state: ARClerkState) -> ARClerkState:
    """Create Xero client and generate initial invoice using specialized tools."""
    print("💼 Creating client and invoice in Xero...")
    
    contract_data = state.get("contract_data", {})
    if not contract_data:
        return {
            **state,
            "error_messages": ["No contract data available for client creation"]
        }
    
    try:
        import json
        from xero_tools import check_xero_contact, create_xero_contact, create_xero_invoice
        
        client_name = contract_data.get("client_name", "")
        contact_email = contract_data.get("contact_email", "")
        total_value = contract_data.get("total_value", 0)
        billing_terms = contract_data.get("billing_terms", "Net 30")
        
        # Check if client exists
        contact_check_result = check_xero_contact.invoke({"name": client_name})
        contact_check = json.loads(contact_check_result)
        
        if contact_check.get("found"):
            # Use existing contact
            contact_id = contact_check["contact_id"]
            print(f"✅ Using existing Xero contact: {client_name}")
        else:
            # Create new contact
            contact_create_result = create_xero_contact.invoke({
                "name": client_name,
                "email": contact_email
            })
            contact_create = json.loads(contact_create_result)
            
            if contact_create.get("success"):
                contact_id = contact_create["contact_id"]
                print(f"✅ Created new Xero contact: {client_name}")
            else:
                return {
                    **state,
                    "error_messages": [f"Failed to create Xero contact: {contact_create.get('message', 'Unknown error')}"]
                }
        
        # Create invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        if "net 60" in billing_terms.lower():
            due_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        elif "net 90" in billing_terms.lower():
            due_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        invoice_create_result = create_xero_invoice.invoke({
            "contact_id": contact_id,
            "description": contract_data.get("service_description", "Professional services"),
            "amount": total_value,
            "due_date": due_date
        })
        invoice_create = json.loads(invoice_create_result)
        
        if invoice_create.get("success"):
            # Store successful creation
            client_info = {
                "xero_contact_id": contact_id,
                "client_name": client_name,
                "contact_email": contact_email,
                "created_date": current_date,
                "status": "active"
            }
            
            invoice_data = {
                "invoice_id": invoice_create["invoice_id"],
                "invoice_number": invoice_create["invoice_number"],
                "client_id": contact_id,
                "amount": total_value,
                "due_date": due_date,
                "status": invoice_create["status"],
                "billing_terms": billing_terms,
                "created_date": current_date
            }
            
            print(f"✅ Invoice created: {invoice_create['invoice_number']} for ${total_value:,.2f}")
            
            return {
                **state,
                "client_info": client_info,
                "invoice_schedule": [invoice_data],
                "current_action": "monitor_payments"
            }
        else:
            return {
                **state,
                "error_messages": [f"Failed to create invoice: {invoice_create.get('message', 'Unknown error')}"]
            }
            
    except Exception as e:
        error_msg = f"Error creating client/invoice: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error_messages": state.get("error_messages", []) + [error_msg],
            "current_action": "error_handling"
        }

def monitor_payments_node(state: ARClerkState) -> ARClerkState:
    """Monitor invoice payments and trigger collections if overdue using specialized tools."""
    print("💰 Monitoring payment status...")
    
    invoice_schedule = state.get("invoice_schedule", [])
    if not invoice_schedule:
        return {
            **state,
            "error_messages": ["No invoices to monitor"]
        }
    
    try:
        import json
        from xero_tools import check_invoice_payments
        
        # Check payment status using Xero API
        payment_check_result = check_invoice_payments.invoke({
            "days_overdue": 0  # Check all invoices
        })
        payment_check = json.loads(payment_check_result)
        
        if payment_check.get("success"):
            overdue_invoices = payment_check.get("overdue_invoices", [])
            collection_status = {}
            
            for overdue in overdue_invoices:
                invoice_id = overdue.get("invoice_id")
                days_overdue = overdue.get("days_overdue", 0)
                
                print(f"⚠️ Invoice {overdue.get('invoice_number')} is {days_overdue} days overdue")
                
                # Determine collection stage
                if days_overdue >= 30:
                    stage = "stage_3_escalate"
                elif days_overdue >= 14:
                    stage = "stage_2_sms"
                elif days_overdue >= 7:
                    stage = "stage_1_email"
                else:
                    stage = "monitoring"
                
                collection_status[invoice_id] = {
                    "invoice_number": overdue.get("invoice_number"),
                    "client_name": overdue.get("contact_name"),
                    "amount_due": overdue.get("amount_due"),
                    "days_overdue": days_overdue,
                    "collection_stage": stage,
                    "last_contact": None,
                    "escalation_needed": days_overdue >= 30
                }
            
            total_overdue = payment_check.get("total_overdue_amount", 0)
            if collection_status:
                print(f"📊 Total overdue: ${total_overdue:,.2f} across {len(collection_status)} invoices")
            else:
                print("✅ No overdue invoices found")
            
            return {
                **state,
                "collection_status": collection_status,
                "current_action": "collections_workflow" if collection_status else "monitoring"
            }
        else:
            # Fallback to local calculation
            collection_status = {}
            for invoice in invoice_schedule:
                invoice_id = invoice.get("invoice_id")
                due_date = datetime.strptime(invoice.get("due_date"), "%Y-%m-%d")
                days_overdue = (datetime.now() - due_date).days
                
                if days_overdue > 0:
                    stage = "stage_3_escalate" if days_overdue >= 30 else "stage_2_sms" if days_overdue >= 14 else "stage_1_email"
                    collection_status[invoice_id] = {
                        "days_overdue": days_overdue,
                        "collection_stage": stage,
                        "amount_due": invoice.get("amount", 0),
                        "escalation_needed": days_overdue >= 30
                    }
            
            return {
                **state,
                "collection_status": collection_status,
                "current_action": "collections_workflow" if collection_status else "monitoring"
            }
            
    except Exception as e:
        error_msg = f"Error monitoring payments: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error_messages": state.get("error_messages", []) + [error_msg],
            "current_action": "error_handling"
        }

def should_continue(state: ARClerkState) -> str:
    """Determine next workflow step."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, go to tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # Check current action state
    current_action = state.get("current_action", "monitoring")
    
    if current_action == "extract_contract_data":
        return "extract_contract_data"
    elif current_action == "create_client_invoice":
        return "create_client_invoice"
    elif current_action == "monitor_payments":
        return "monitor_payments"
    elif current_action == "collections_workflow":
        return "agent"  # Let agent handle collections decisions
    
    # Count AI messages to prevent infinite loops
    ai_messages = sum(1 for msg in state["messages"] if isinstance(msg, AIMessage))
    
    if ai_messages >= 5:
        return END
    
    return "agent"

# --- Graph Construction ---
def create_ar_clerk_agent():
    """Create the Accounts Receivable Clerk workflow graph."""
    
    workflow = StateGraph(ARClerkState)
    
    # Add nodes
    workflow.add_node("monitor_contracts", monitor_contracts_node)
    workflow.add_node("extract_contract_data", extract_contract_data_node)
    workflow.add_node("create_client_invoice", create_client_invoice_node)
    workflow.add_node("monitor_payments", monitor_payments_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    # Set entry point
    workflow.set_entry_point("monitor_contracts")
    
    # Add edges
    workflow.add_edge("monitor_contracts", "agent")
    workflow.add_edge("extract_contract_data", "create_client_invoice")
    workflow.add_edge("create_client_invoice", "monitor_payments")
    workflow.add_edge("monitor_payments", "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# Initialize the graph (with error handling for imports)
try:
    graph = create_ar_clerk_agent()
    print(f"✅ AR Clerk graph initialized with {len(all_tools)} tools")
except Exception as e:
    print(f"❌ Error initializing AR Clerk graph: {e}")
    graph = None

# --- Main Execution ---
def main():
    """Interactive execution for the Accounts Receivable Clerk."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check if graph was initialized properly
    if graph is None:
        print("❌ Agent graph not initialized. Please check dependencies and imports.")
        return
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "XERO_ACCESS_TOKEN",
        "XERO_TENANT_ID",
        "PERPLEXITY_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please configure your .env file with the required API keys.")
        return
    
    print("✅ Autonomous Accounts Receivable Clerk is ready!")
    print(f"📅 Today's date: {current_date}")
    print(f"🔧 Tools available: {len(all_tools)}")
    print("\n💡 Try requests like:")
    print("  - 'Process new contract for ABC Corp, $15,000 web development, Net 30 terms'")
    print("  - 'Check payment status for all outstanding invoices'")
    print("  - 'Run collections process for overdue accounts'")
    print("\n💬 Type 'quit' to exit\n")
    
    while True:
        user_input = input("👤 AR Request: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Accounts Receivable Clerk shutting down!")
            break
        
        if not user_input:
            continue
        
        print("🏦 Processing AR workflow...")
        
        try:
            # Create initial state
            initial_state = ARClerkState(
                messages=[HumanMessage(content=user_input)],
                contract_data={},
                client_info={},
                invoice_schedule=[],
                collection_status={},
                processed_files=[],
                current_action="monitoring",
                error_messages=[]
            )
            
            # Run the workflow
            result = graph.invoke(initial_state, {"recursion_limit": 15})
            
            # Display results
            final_message = result["messages"][-1]
            print(f"\n🤖 AR Clerk: {final_message.content}")
            
            # Show workflow status
            if result.get("contract_data"):
                contract = result["contract_data"]
                print(f"📄 Contract processed: {contract.get('client_name')} - ${contract.get('total_value', 0):,.2f}")
            
            if result.get("invoice_schedule"):
                invoices = result["invoice_schedule"]
                print(f"📋 Invoices managed: {len(invoices)} invoice(s)")
            
            if result.get("collection_status"):
                collections = result["collection_status"]
                overdue_count = len([c for c in collections.values() if c.get("days_overdue", 0) > 0])
                if overdue_count > 0:
                    print(f"⚠️ Collections needed: {overdue_count} overdue invoice(s)")
            
            if result.get("error_messages"):
                print("⚠️ Issues encountered:")
                for error in result["error_messages"]:
                    print(f"  - {error}")
            
            print("---\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---\n")

if __name__ == "__main__":
    main()