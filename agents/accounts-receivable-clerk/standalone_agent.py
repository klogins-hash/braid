"""
Standalone Autonomous Accounts Receivable Clerk Agent
Complete implementation without external core dependencies.
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

# Combine all tools
all_tools = xero_ar_tools + contract_tools + collections_tools
tool_map = {tool.name: tool for tool in all_tools}

# --- Model Setup ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)

# --- System Prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""You are an Autonomous Accounts Receivable Clerk that automates the complete lifecycle from contract to cash collection.

**Today's Date**: {current_date}

**Your Core Responsibilities**:
1. Extract contract data from user-provided contract information
2. Create clients and invoices in Xero accounting system
3. Track payment status and automate collections
4. Execute multi-stage collections with escalating communication

**Available Tools**:
{len(all_tools)} specialized tools for accounts receivable management.

**Workflow Process**:
1. **Contract Processing**: Extract billing information from contract descriptions
2. **Client Management**: Check if client exists in Xero, create new contact if needed
3. **Invoice Creation**: Generate invoices based on contract billing terms
4. **Payment Tracking**: Monitor invoice payment status
5. **Collections Process**: Automated escalation for overdue accounts
   - Stage 1 (7+ days overdue): Professional email reminder
   - Stage 2 (14+ days overdue): Direct SMS reminder  
   - Stage 3 (30+ days overdue): Escalate to human via notification

**Instructions**:
- Use the extract_contract_data tool to parse contract information
- Use check_xero_contact and create_xero_contact for client management
- Use create_xero_invoice for billing
- Use check_invoice_payments to monitor overdue accounts
- Use send_collection_email, send_collection_sms, and escalate_to_human for collections

**Data Transparency Rules**:
- ALWAYS use actual data from tool responses
- Be transparent about data sources (real API vs fallback)
- Clearly indicate when using simulated data due to API issues
- Provide complete audit trail of all actions

**Error Handling**:
- Handle API failures gracefully with clear messaging
- Use fallback processes when primary systems unavailable
- Escalate to human oversight when automation fails
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# --- Workflow Nodes ---

def agent_node(state: ARClerkState) -> ARClerkState:
    """Main agent node that orchestrates the AR workflow."""
    print("🤖 AR Clerk analyzing request and determining actions...")
    
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
                
                # Handle different tool types
                if "xero" in tool_name.lower():
                    print(f"✅ {tool_name}: Xero operation completed")
                elif "contract" in tool_name.lower():
                    print(f"✅ {tool_name}: Contract processing completed")
                elif "collection" in tool_name.lower():
                    print(f"✅ {tool_name}: Collections action completed")
                
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

def should_continue(state: ARClerkState) -> str:
    """Determine if we should continue or end."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, go to tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # Count total AI messages to prevent infinite loops
    ai_messages = sum(1 for msg in state["messages"] if isinstance(msg, AIMessage))
    
    # End after reasonable number of exchanges
    if ai_messages >= 4:
        return END
    
    # Check if we've done meaningful work
    tool_messages = [msg for msg in state["messages"] if isinstance(msg, ToolMessage)]
    
    # If we've executed multiple tools and have AI responses, we're likely done
    if len(tool_messages) >= 2 and ai_messages >= 3:
        return END
    
    # Continue with agent
    return "agent"

# --- Graph Construction ---
def create_ar_clerk_agent():
    """Create the Accounts Receivable Clerk workflow graph."""
    
    workflow = StateGraph(ARClerkState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# Initialize the graph
try:
    graph = create_ar_clerk_agent()
    print(f"✅ Standalone AR Clerk initialized with {len(all_tools)} tools")
except Exception as e:
    print(f"❌ Error initializing AR Clerk: {e}")
    graph = None

# --- Main Execution ---
def main():
    """Interactive execution for the Accounts Receivable Clerk."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check if graph was initialized properly
    if graph is None:
        print("❌ Agent graph not initialized. Please check dependencies.")
        return
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
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
                current_action="processing",
                error_messages=[]
            )
            
            # Run the workflow
            result = graph.invoke(initial_state, {"recursion_limit": 10})
            
            # Display results
            final_message = result["messages"][-1]
            print(f"\n🤖 AR Clerk: {final_message.content}")
            
            # Show additional info if available
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