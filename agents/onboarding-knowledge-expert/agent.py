"""
Onboarding & Internal Knowledge Expert Agent
A long-running agent that manages employee onboarding and serves as a conversational expert on company knowledge.

Features:
- Automated multi-week onboarding workflows
- RAG-powered knowledge base queries
- Slack integration for DMs and channel responses  
- Google Calendar scheduling for introductory meetings
- Notion task assignments and document management
- Persistent memory for individual user journeys
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Annotated, TypedDict, Optional
from dotenv import load_dotenv

from langchain_core.messages import (
    AnyMessage, HumanMessage, AIMessage, ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.store.base import BaseStore

# Load environment variables
load_dotenv()

# Import direct API integrations following CLAUDE.md guidance
from core.integrations.communication.slack.tools import (
    slack_send_direct_message,
    slack_post_message,
    slack_get_mentions,
    slack_find_user_by_name
)
from core.integrations.productivity.notion.tools import (
    create_notion_page,
    get_notion_page,
    update_notion_page
)
from core.integrations.productivity.gworkspace.tools import get_gworkspace_tools
from core.integrations.productivity.perplexity.tools import perplexity_ask

# Custom tools for this agent
from onboarding_tools import (
    get_onboarding_tools,
    schedule_onboarding_task,
    get_user_onboarding_status,
    mark_onboarding_complete
)
from knowledge_tools import (
    get_knowledge_tools,
    search_knowledge_base,
    get_document_with_context,
    create_service_request
)

# --- Agent State ---
class OnboardingKnowledgeState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    request_type: str  # "onboarding", "knowledge_query", "service_request"
    user_id: str  # Slack user ID
    user_name: str  # User's display name
    conversation_context: str  # "dm", "channel_mention", "scheduled_task"
    
    # Onboarding specific
    onboarding_day: Optional[int]  # Day in onboarding journey (1-30)
    onboarding_status: Optional[str]  # "active", "completed", "paused"
    scheduled_tasks: List[Dict[str, Any]]  # Pending onboarding tasks
    
    # Knowledge query specific  
    query_intent: Optional[str]  # "policy", "process", "contact", "technical"
    search_results: List[Dict[str, Any]]  # RAG search results
    source_documents: List[str]  # Document URLs for citations
    
    # General
    current_action: str
    error_messages: List[str]

# --- Tool Setup ---
# Core communication tools
slack_tools = [
    slack_send_direct_message,
    slack_post_message,
    slack_get_mentions,
    slack_find_user_by_name
]

# Productivity tools
notion_tools = [
    create_notion_page,
    get_notion_page,
    update_notion_page
]

# Get Google Workspace tools
gworkspace_tools = get_gworkspace_tools()

# Custom agent tools
onboarding_tools = get_onboarding_tools()
knowledge_tools = get_knowledge_tools()

# Research and AI tools
ai_tools = [perplexity_ask]

# Combine all tools
all_tools = slack_tools + notion_tools + gworkspace_tools + onboarding_tools + knowledge_tools + ai_tools
tool_map = {tool.name: tool for tool in all_tools}

# --- Model Setup ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)

# --- System Prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

system_prompt = f"""You are the Onboarding & Internal Knowledge Expert, a long-running agent that manages employee onboarding and serves as the company's conversational knowledge expert.

**Today's Date**: {current_date}

**Your Dual Responsibilities**:

**1. ONBOARDING AUTOMATION**
When a new hire joins (detected via Slack), you initiate and manage a personalized 30-day onboarding journey:
- Day 1: Send welcome DM, schedule intro meetings, provide essential documents
- Ongoing: Scheduled drip campaigns with tips, check-ins, and task assignments
- Progress tracking: Monitor completion and adjust timeline as needed

**2. KNOWLEDGE EXPERT (RAG-POWERED)**
You are the always-on expert for company knowledge, handling:
- Policy questions: "How do I submit an expense report?"
- Process inquiries: "What's our code review process?"
- Contact finding: "Who manages Project X?"
- Technical help: "How do I access the VPN?"

**Available Tools**: {len(all_tools)} tools for communication, scheduling, document management, and knowledge retrieval.

**Core Workflow Patterns**:

**Onboarding Mode**:
1. **New Hire Detection**: Monitor Slack for new team members
2. **Journey Initiation**: Create personalized 30-day onboarding plan
3. **Scheduled Execution**: Send timed messages, create tasks, schedule meetings
4. **Progress Monitoring**: Check completion, send reminders, escalate if needed
5. **Completion**: Mark journey complete, transition to knowledge support

**Knowledge Expert Mode**:
1. **Query Understanding**: Parse user question and determine intent
2. **Knowledge Retrieval**: Search company knowledge base using RAG
3. **Contextual Response**: Provide accurate answer with source citations
4. **Service Routing**: Handle simple requests or route to appropriate teams

**Data Sources & Integration**:
- **Slack**: Communication, user detection, notifications
- **Notion**: Company wiki, policies, task assignments, IT forms
- **Google Calendar**: Meeting scheduling for introductions
- **Google Drive**: Document access and knowledge base
- **Memory Store**: Individual user progress and preferences

**Response Patterns**:
- **Onboarding**: Friendly, encouraging, structured with clear next steps
- **Knowledge Queries**: Concise, authoritative, always include source links
- **Service Requests**: Helpful, with direct links to forms or escalation paths

**Data Transparency**:
- Always use real data from knowledge base searches
- Clearly cite source documents with links
- Indicate when information might be outdated
- Escalate to humans when uncertain

**Memory Management**:
- Track individual onboarding progress persistently
- Remember user preferences and past questions
- Maintain conversation context across multiple interactions

**Error Handling**:
- Gracefully handle API failures with helpful alternatives
- Escalate complex requests to appropriate team members
- Maintain audit trail of all onboarding activities
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

# --- Workflow Nodes ---

def parse_request_node(state: OnboardingKnowledgeState) -> OnboardingKnowledgeState:
    """Parse incoming request and determine workflow path."""
    print("🔍 Parsing request type and context...")
    
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
    
    # Analyze message content to determine request type
    message_lower = last_message.lower()
    
    # Check for onboarding-related keywords
    onboarding_keywords = ["new hire", "welcome", "onboarding", "first day", "started today"]
    knowledge_keywords = ["how do i", "what is", "where can i", "who is", "policy", "process"]
    service_keywords = ["request", "need access", "can you help", "submit", "form"]
    
    if any(keyword in message_lower for keyword in onboarding_keywords):
        request_type = "onboarding"
        current_action = "initiate_onboarding"
    elif any(keyword in message_lower for keyword in service_keywords):
        request_type = "service_request" 
        current_action = "handle_service_request"
    elif any(keyword in message_lower for keyword in knowledge_keywords):
        request_type = "knowledge_query"
        current_action = "search_knowledge"
    else:
        # Default to knowledge query for ambiguous requests
        request_type = "knowledge_query"
        current_action = "search_knowledge"
    
    print(f"✅ Request type: {request_type}, Action: {current_action}")
    
    return {
        **state,
        "request_type": request_type,
        "current_action": current_action,
        "conversation_context": "dm"  # Default, can be overridden
    }

def initiate_onboarding_node(state: OnboardingKnowledgeState) -> OnboardingKnowledgeState:
    """Set up a new employee's onboarding journey."""
    print("🎉 Initiating onboarding for new hire...")
    
    try:
        # Extract user information from the request
        last_message = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_message = msg.content
                break
        
        if not last_message:
            return {
                **state,
                "error_messages": ["No onboarding request found"]
            }
        
        # Schedule the 30-day onboarding journey using our custom tool
        onboarding_result = schedule_onboarding_task.invoke({
            "user_id": state.get("user_id", "unknown"),
            "user_name": state.get("user_name", "New Hire"),
            "start_date": current_date,
            "onboarding_type": "standard_30_day"
        })
        
        # Parse the scheduling result
        import json
        schedule_info = json.loads(onboarding_result)
        
        if schedule_info.get("success"):
            scheduled_tasks = schedule_info.get("scheduled_tasks", [])
            
            print(f"✅ Onboarding journey scheduled: {len(scheduled_tasks)} tasks over 30 days")
            
            return {
                **state,
                "onboarding_day": 1,
                "onboarding_status": "active",
                "scheduled_tasks": scheduled_tasks,
                "current_action": "send_welcome_message"
            }
        else:
            error_msg = f"Failed to schedule onboarding: {schedule_info.get('message', 'Unknown error')}"
            return {
                **state,
                "error_messages": [error_msg],
                "current_action": "error_handling"
            }
            
    except Exception as e:
        error_msg = f"Error initiating onboarding: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error_messages": state.get("error_messages", []) + [error_msg],
            "current_action": "error_handling"
        }

def search_knowledge_node(state: OnboardingKnowledgeState) -> OnboardingKnowledgeState:
    """Search the company knowledge base using RAG."""
    print("🔍 Searching company knowledge base...")
    
    # Get the user's query
    last_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break
    
    if not last_message:
        return {
            **state,
            "error_messages": ["No query found for knowledge search"]
        }
    
    try:
        # Use our custom knowledge search tool
        search_result = search_knowledge_base.invoke({
            "query": last_message,
            "max_results": 5,
            "include_sources": True
        })
        
        # Parse search results
        import json
        search_data = json.loads(search_result)
        
        if search_data.get("success"):
            search_results = search_data.get("results", [])
            source_documents = [result.get("source_url", "") for result in search_results if result.get("source_url")]
            
            print(f"✅ Found {len(search_results)} relevant knowledge base entries")
            
            # Determine query intent for better routing
            query_lower = last_message.lower()
            if any(word in query_lower for word in ["policy", "rule", "guideline"]):
                query_intent = "policy"
            elif any(word in query_lower for word in ["process", "procedure", "workflow"]):
                query_intent = "process"
            elif any(word in query_lower for word in ["who", "contact", "manager"]):
                query_intent = "contact"
            else:
                query_intent = "technical"
            
            return {
                **state,
                "search_results": search_results,
                "source_documents": source_documents,
                "query_intent": query_intent,
                "current_action": "provide_answer"
            }
        else:
            # No results found, try broader search or escalate
            print("⚠️ No knowledge base results found, trying perplexity fallback")
            return {
                **state,
                "current_action": "fallback_search"
            }
            
    except Exception as e:
        error_msg = f"Error searching knowledge base: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            **state,
            "error_messages": state.get("error_messages", []) + [error_msg],
            "current_action": "error_handling"
        }

def agent_node(state: OnboardingKnowledgeState) -> OnboardingKnowledgeState:
    """Main agent node that orchestrates responses."""
    print("🤖 Agent analyzing request and generating response...")
    
    # Format the prompt with current state context
    messages = prompt.format_messages(messages=state["messages"])
    
    # Add context about current state for better responses
    context_info = f"""
Current Context:
- Request Type: {state.get('request_type', 'unknown')}
- User: {state.get('user_name', 'Unknown')}
- Action: {state.get('current_action', 'unknown')}
"""
    
    if state.get('onboarding_status'):
        context_info += f"- Onboarding Day: {state.get('onboarding_day', 'N/A')}\n"
        context_info += f"- Onboarding Status: {state.get('onboarding_status', 'N/A')}\n"
    
    if state.get('search_results'):
        context_info += f"- Knowledge Results: {len(state.get('search_results', []))} found\n"
        context_info += f"- Query Intent: {state.get('query_intent', 'N/A')}\n"
    
    # Add context as a system message
    enhanced_messages = messages + [HumanMessage(content=context_info)]
    
    # Get agent response
    response = llm_with_tools.invoke(enhanced_messages)
    
    return {
        **state,
        "messages": state["messages"] + [response]
    }

def tools_node(state: OnboardingKnowledgeState) -> OnboardingKnowledgeState:
    """Execute tool calls from the agent."""
    print("🔧 Executing onboarding and knowledge tools...")
    
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
                if tool_name in ["slack_send_direct_message", "slack_post_message"]:
                    print(f"📧 {tool_name}: Message sent successfully")
                
                elif tool_name in ["search_knowledge_base", "get_document_with_context"]:
                    print(f"🔍 {tool_name}: Knowledge search completed")
                
                elif tool_name in ["create_notion_page", "update_notion_page"]:
                    print(f"📝 {tool_name}: Notion operation completed")
                
                elif tool_name in ["schedule_onboarding_task", "get_user_onboarding_status"]:
                    print(f"🎯 {tool_name}: Onboarding operation completed")
                
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

def should_continue(state: OnboardingKnowledgeState) -> str:
    """Determine next workflow step."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, go to tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # Check current action state for routing
    current_action = state.get("current_action", "")
    
    if current_action == "initiate_onboarding":
        return "initiate_onboarding"
    elif current_action == "search_knowledge":
        return "search_knowledge"
    elif current_action in ["provide_answer", "send_welcome_message", "handle_service_request"]:
        return "agent"  # Let agent handle the response
    
    # Count AI messages to prevent infinite loops
    ai_messages = sum(1 for msg in state["messages"] if isinstance(msg, AIMessage))
    
    if ai_messages >= 4:
        return END
    
    return "agent"

# --- Graph Construction ---
def create_onboarding_knowledge_agent():
    """Create the Onboarding & Internal Knowledge Expert workflow graph."""
    
    workflow = StateGraph(OnboardingKnowledgeState)
    
    # Add nodes
    workflow.add_node("parse_request", parse_request_node)
    workflow.add_node("initiate_onboarding", initiate_onboarding_node)
    workflow.add_node("search_knowledge", search_knowledge_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    
    # Set entry point
    workflow.set_entry_point("parse_request")
    
    # Add edges
    workflow.add_edge("parse_request", "agent")
    workflow.add_edge("initiate_onboarding", "agent")
    workflow.add_edge("search_knowledge", "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# Initialize the graph (with error handling for imports)
try:
    graph = create_onboarding_knowledge_agent()
    print(f"✅ Onboarding & Knowledge Expert graph initialized with {len(all_tools)} tools")
except Exception as e:
    print(f"❌ Error initializing agent graph: {e}")
    graph = None

# --- Main Execution ---
def main():
    """Interactive execution for the Onboarding & Internal Knowledge Expert."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check if graph was initialized properly
    if graph is None:
        print("❌ Agent graph not initialized. Please check dependencies and imports.")
        return
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "SLACK_BOT_TOKEN",
        "NOTION_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please configure your .env file with the required API keys.")
        return
    
    print("✅ Onboarding & Internal Knowledge Expert is ready!")
    print(f"📅 Today's date: {current_date}")
    print(f"🔧 Tools available: {len(all_tools)}")
    print("\n💡 Try requests like:")
    print("  - 'New hire Sarah Johnson started today in Engineering'")
    print("  - 'How do I submit an expense report?'")
    print("  - 'What are our remote work policies?'")
    print("  - 'Who is the product manager for Project Alpha?'")
    print("\n💬 Type 'quit' to exit\n")
    
    while True:
        user_input = input("👤 Request: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Onboarding & Knowledge Expert shutting down!")
            break
        
        if not user_input:
            continue
        
        print("🏢 Processing your request...")
        
        try:
            # Create initial state
            initial_state = OnboardingKnowledgeState(
                messages=[HumanMessage(content=user_input)],
                request_type="unknown",
                user_id="user_demo",
                user_name="Demo User",
                conversation_context="dm",
                onboarding_day=None,
                onboarding_status=None,
                scheduled_tasks=[],
                query_intent=None,
                search_results=[],
                source_documents=[],
                current_action="parse_request",
                error_messages=[]
            )
            
            # Run the workflow
            result = graph.invoke(initial_state, {"recursion_limit": 15})
            
            # Display results
            final_message = result["messages"][-1]
            print(f"\n🤖 Knowledge Expert: {final_message.content}")
            
            # Show additional context
            if result.get("request_type"):
                print(f"📋 Request type: {result['request_type']}")
            
            if result.get("onboarding_status"):
                print(f"🎯 Onboarding status: {result['onboarding_status']} (Day {result.get('onboarding_day', 'N/A')})")
            
            if result.get("search_results"):
                print(f"🔍 Knowledge results: {len(result['search_results'])} documents found")
            
            if result.get("source_documents"):
                print("📚 Sources:")
                for i, source in enumerate(result["source_documents"][:3], 1):
                    print(f"  {i}. {source}")
            
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