from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

# This is the key import that tests our new architecture
from core.tool_loader import get_tools

class CommsState(TypedDict):
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]

class InternalCommsAgent:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatOpenAI(model="gpt-4o")
        
        # Load the ms365 tools from our central registry by their entry point names
        tool_names = [
            "teams_post_message",
            "outlook_send_email"
        ]
        self.tools = get_tools(tool_names)
        
        # Bind the tools to the LLM
        self.model_with_tools = self.llm.bind_tools(self.tools)
        
        # Define the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CommsState)
        
        builder.add_node("agent", self.agent_node)
        tool_node = ToolNode(self.tools)
        builder.add_node("tools", tool_node)
        
        builder.add_conditional_edges(
            "agent",
            lambda state: "tools" if state["messages"][-1].tool_calls else END
        )
        
        builder.add_edge(START, "agent")
        builder.add_edge("tools", "agent")
        
        return builder.compile()

    def agent_node(self, state: CommsState):
        """The primary node that calls the LLM."""
        response = self.model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def run(self, query: str):
        """Runs the agent with a given user query."""
        initial_state: CommsState = {"messages": [HumanMessage(content=query)]}
        return self.graph.invoke(initial_state)
