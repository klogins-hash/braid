"""
Sales Intelligence Agent
Automated daily sales insights and team coordination using multiple Braid tools.
"""
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment variables FIRST
load_dotenv()

# Import tools
from tools.http_tools import get_web_tools
from tools.transform_tools import get_transform_tools
from tools.slack_tools import get_slack_tools
from tools.gworkspace_tools import get_gworkspace_tools
from tools.files_tools import get_files_tools
from tools.execution_tools import get_execution_tools
from tools.csv_tools import get_csv_tools

# --- Agent State ---
class SalesAgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    daily_data: dict  # Store collected data between steps
    processing_status: dict  # Track workflow progress

# --- Tool Setup ---
all_tools = (
    get_web_tools() + 
    get_transform_tools() + 
    get_slack_tools() + 
    get_gworkspace_tools() + 
    get_files_tools() + 
    get_execution_tools() + 
    get_csv_tools()
)
tool_node = ToolNode(all_tools) if all_tools else None

# --- Specialized Prompts ---
current_date = datetime.now().strftime("%Y-%m-%d")
current_time = datetime.now().strftime("%H:%M")

sales_intelligence_prompt = f"""
You are a Sales Intelligence Agent designed to automate daily sales insights and team coordination.

**Today**: {current_date} at {current_time}
**Mission**: Gather sales data, generate insights, and coordinate team communication

**Available Tools**: {len(all_tools)} specialized tools for:
- HTTP requests (CRM/Analytics APIs, competitor scraping)
- Data transformation (cleaning, scoring, analysis)
- Slack communication (channel posts, DMs, notifications)
- Google Workspace (Sheets updates, reports)
- File operations (CSV storage, logs, reports)
- Workflow execution (scheduling, coordination, delays)
- CSV processing (historical data, analysis)

**Core Workflow**:
1. **Data Collection**: Fetch CRM data, analytics, competitor pricing
2. **Data Processing**: Clean, analyze, score leads, calculate metrics
3. **Intelligence Generation**: Create insights, identify priorities, flag alerts
4. **Distribution**: Post summaries, send personalized updates, update dashboard

**Safety Rules**:
- Never post individual customer details in public channels
- Only alert on competitor changes > 5%
- Confirm high-priority leads (score > 90) with sales manager
- Wait 2 seconds between competitor website requests
- Backup data before Google Sheets updates

**Response Style**: Professional, data-driven, action-oriented with clear metrics and next steps.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", sales_intelligence_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)  # Lower temperature for consistent business data
llm_with_tools = llm.bind_tools(all_tools) if all_tools else llm

# --- Specialized Node Functions ---

def data_collection_node(state: SalesAgentState):
    """Collect data from all sources (CRM, analytics, competitors)."""
    messages = [HumanMessage(content="""
    Execute the data collection phase:
    
    1. Fetch CRM data from our REST API for new leads and deal updates
    2. Get yesterday's website analytics 
    3. Scrape competitor pricing from key competitors
    
    Use appropriate delays between requests and handle any API failures gracefully.
    Store all collected data for the processing phase.
    """)]
    
    formatted_messages = prompt.format_messages(messages=state["messages"] + messages)
    response = llm_with_tools.invoke(formatted_messages)
    
    return {
        "messages": state["messages"] + [response],
        "daily_data": state.get("daily_data", {}),
        "processing_status": {"data_collection": "completed"}
    }

def data_processing_node(state: SalesAgentState):
    """Process and analyze the collected data."""
    messages = [HumanMessage(content="""
    Execute the data processing phase:
    
    1. Clean and normalize the collected CRM data (standardize fields, filter relevant deals)
    2. Calculate daily metrics: new leads count, deal progression, pipeline changes
    3. Analyze competitor pricing trends and identify significant changes (>5%)
    4. Generate priority lead scores based on engagement data
    5. Create structured data ready for reporting
    
    Focus on actionable insights and flag any anomalies or high-priority items.
    """)]
    
    formatted_messages = prompt.format_messages(messages=state["messages"] + messages)
    response = llm_with_tools.invoke(formatted_messages)
    
    return {
        "messages": state["messages"] + [response],
        "daily_data": state.get("daily_data", {}),
        "processing_status": {**state.get("processing_status", {}), "data_processing": "completed"}
    }

def intelligence_generation_node(state: SalesAgentState):
    """Generate sales intelligence reports and insights."""
    messages = [HumanMessage(content="""
    Execute the intelligence generation phase:
    
    1. Create daily sales intelligence report with:
       - Top 5 hottest leads requiring immediate attention
       - Competitor pricing alerts (changes > 5%)
       - Pipeline health summary with trends
       - Action items for each sales rep
    
    2. Generate different views:
       - Executive summary for leadership
       - Personalized updates for individual reps
       - Dashboard metrics for Google Sheets
    
    3. Prepare structured data for distribution channels
    
    Focus on actionable insights with clear priority levels and specific next steps.
    """)]
    
    formatted_messages = prompt.format_messages(messages=state["messages"] + messages)
    response = llm_with_tools.invoke(formatted_messages)
    
    return {
        "messages": state["messages"] + [response],
        "daily_data": state.get("daily_data", {}),
        "processing_status": {**state.get("processing_status", {}), "intelligence_generation": "completed"}
    }

def distribution_node(state: SalesAgentState):
    """Distribute insights through multiple channels."""
    messages = [HumanMessage(content="""
    Execute the distribution phase:
    
    1. Post executive summary to #sales-leadership Slack channel
    2. Send personalized updates to individual sales reps via DM
    3. Update the "Daily Sales Dashboard" Google Sheet with metrics
    4. Store detailed report as CSV for historical analysis
    5. Schedule any follow-up reminders for high-priority leads
    
    Ensure all communications are professional, data-driven, and include specific action items.
    Use appropriate formatting for each channel (emojis for Slack, structured data for Sheets).
    """)]
    
    formatted_messages = prompt.format_messages(messages=state["messages"] + messages)
    response = llm_with_tools.invoke(formatted_messages)
    
    return {
        "messages": state["messages"] + [response],
        "daily_data": state.get("daily_data", {}),
        "processing_status": {**state.get("processing_status", {}), "distribution": "completed"}
    }

def schedule_checker_node(state: SalesAgentState):
    """Check if it's appropriate to run the daily workflow."""
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    current_hour = datetime.now().hour
    
    # Only run on weekdays (Monday-Friday) between 7 AM and 10 AM
    if current_day >= 5:  # Weekend
        response = HumanMessage(content="⏭️ Weekend detected - skipping daily sales intelligence workflow")
    elif current_hour < 7 or current_hour > 10:
        response = HumanMessage(content=f"⏰ Outside business hours ({current_hour}:00) - workflow scheduled for 8 AM weekdays")
    else:
        response = HumanMessage(content="✅ Weekday morning detected - proceeding with daily sales intelligence workflow")
    
    return {
        "messages": state["messages"] + [response],
        "daily_data": state.get("daily_data", {}),
        "processing_status": {"schedule_check": "completed"}
    }

# --- Graph Definition ---
def should_continue_workflow(state: SalesAgentState):
    """Determine if the workflow should continue based on schedule and status."""
    last_message = state["messages"][-1].content
    
    if "skipping" in last_message or "Outside business hours" in last_message:
        return "end"
    
    status = state.get("processing_status", {})
    if "schedule_check" in status and "data_collection" not in status:
        return "data_collection"
    elif "data_collection" in status and "data_processing" not in status:
        return "data_processing"
    elif "data_processing" in status and "intelligence_generation" not in status:
        return "intelligence_generation"
    elif "intelligence_generation" in status and "distribution" not in status:
        return "distribution"
    else:
        return "end"

# Build the specialized sales intelligence graph
builder = StateGraph(SalesAgentState)

# Add specialized nodes
builder.add_node("schedule_checker", schedule_checker_node)
builder.add_node("data_collection", data_collection_node)
builder.add_node("data_processing", data_processing_node)
builder.add_node("intelligence_generation", intelligence_generation_node)
builder.add_node("distribution", distribution_node)
builder.add_node("tools", tool_node)

# Define the workflow
builder.add_edge(START, "schedule_checker")
builder.add_conditional_edges("schedule_checker", should_continue_workflow)
builder.add_conditional_edges("data_collection", tools_condition)
builder.add_conditional_edges("data_processing", tools_condition)
builder.add_conditional_edges("intelligence_generation", tools_condition)
builder.add_conditional_edges("distribution", tools_condition)
builder.add_edge("tools", "schedule_checker")  # Return to flow control

graph = builder.compile()

# --- Main Execution ---
def run_daily_intelligence():
    """Execute the daily sales intelligence workflow."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY", 
        "SLACK_BOT_TOKEN", 
        "SLACK_USER_TOKEN"
    ]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"❌ Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        return
    
    print("🎯 Sales Intelligence Agent Starting...")
    print(f"📅 Date: {current_date}")
    print(f"🔧 Tools loaded: {len(all_tools)}")
    print("=" * 50)
    
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content="Starting daily sales intelligence workflow")],
        "daily_data": {},
        "processing_status": {}
    }
    
    try:
        # Execute the workflow
        result = graph.invoke(initial_state)
        
        # Print final status
        print("\n" + "=" * 50)
        print("🏁 Sales Intelligence Workflow Complete")
        print(f"📊 Processing Status: {result.get('processing_status', {})}")
        
        # Show final message
        final_message = result["messages"][-1]
        print(f"📝 Final Status: {final_message.content}")
        
    except Exception as e:
        print(f"❌ Workflow Error: {e}")
        logging.error(f"Sales intelligence workflow failed: {e}")

def interactive_mode():
    """Run the agent in interactive mode for testing."""
    print("🎯 Sales Intelligence Agent - Interactive Mode")
    print("Type 'daily' to run daily workflow, or ask questions about sales data")
    print("Type 'quit' to exit\n")
    
    conversation: List[BaseMessage] = []
    
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == "daily":
            run_daily_intelligence()
            continue
        
        if not user_input:
            continue
            
        conversation.append(HumanMessage(content=user_input))
        print("🤖 Processing...")
        
        try:
            # Use the simple agent node for interactive queries
            state = {"messages": conversation}
            result = graph.invoke(state)
            final_response = result["messages"][-1]
            conversation = result["messages"]
            
            print(f"🤖 Sales Agent: {final_response.content}")
            print("---")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("---")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--daily":
        run_daily_intelligence()
    else:
        interactive_mode()