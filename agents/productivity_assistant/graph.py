from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from datetime import datetime, timedelta
import pytz

# This is the key import that tests our new architecture
from core.tool_loader import get_tools

class ProductivityState(TypedDict):
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]

class ProductivityAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatOpenAI(model="gpt-4o")
        
        # Load the gworkspace tools from our central registry by their entry point names
        tool_names = [
            "google_calendar_create_event",
            "gmail_send_email"
            # We are not using gsheets in this example, so we don't load it.
        ]
        self.tools = get_tools(tool_names)
        
        # Bind the tools to the LLM so it knows how to call them
        self.model_with_tools = self.llm.bind_tools(self.tools)
        
        # Define the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(ProductivityState)
        
        # Define the agent and tool nodes
        builder.add_node("agent", self.agent_node)
        tool_node = ToolNode(self.tools)
        builder.add_node("tools", tool_node)
        
        # Define the conditional edge
        builder.add_conditional_edges(
            "agent",
            # This function decides whether to call a tool or end the conversation
            lambda state: "tools" if state["messages"][-1].tool_calls else END
        )
        
        # Define the graph's flow
        builder.add_edge(START, "agent")
        builder.add_edge("tools", "agent")
        
        return builder.compile()

    def agent_node(self, state: ProductivityState):
        """The primary node that calls the LLM."""
        response = self.model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def run(self, query: str):
        """Runs the agent with a given user query."""
        # Get current date and time for context
        pst = pytz.timezone('America/Los_Angeles')
        now = datetime.now(pst)
        today_str = now.strftime("%A, %B %d, %Y")
        
        # Create system message with current date context
        system_msg = SystemMessage(content=f"""You are a productivity assistant with access to Gmail and Google Calendar tools.

IMPORTANT DATE CONTEXT:
- Today is {today_str}
- Current time: {now.strftime("%I:%M %p %Z")}
- When scheduling events for "tomorrow", use {(now + timedelta(days=1)).strftime("%A, %B %d, %Y")}

When creating calendar events:
- Use proper ISO 8601 format: YYYY-MM-DDTHH:MM:SS±HH:MM
- For PST/PDT times, use -08:00 (PST) or -07:00 (PDT) timezone offset
- Always ensure dates are in the correct year: {now.year}

Be helpful and professional in your communications.""")
        
        initial_state: ProductivityState = {"messages": [system_msg, HumanMessage(content=query)]}
        return self.graph.invoke(initial_state)
