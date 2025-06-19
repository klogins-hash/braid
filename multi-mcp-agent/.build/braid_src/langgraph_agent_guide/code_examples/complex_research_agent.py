"""
An example of a complex research agent using LangGraph.

This agent is designed to answer a user's question by:
1.  Planning a research strategy.
2.  Executing parallel web searches based on the plan.
3.  Processing the search results.
4.  Synthesizing the results into a final report.

This demonstrates several advanced LangGraph concepts:
- A complex state schema ("scratchpad").
- The map-reduce pattern for parallel execution.
- Conditional routing and loops for planning and reflection (though reflection
  is kept simple here for clarity).
"""

import os
from typing import List, Annotated, TypedDict

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# Set any necessary API keys here
# You will need an OpenAI API key and a Tavily API key.
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..."
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = "ls_..."


# 1. Define the tools
# The agent will have access to a single tool: Tavily Search.
search_tool = TavilySearchResults(max_results=3)


# 2. Define the State ("Scratchpad") for the agent
class ResearchAgentState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    # The list of search queries to perform
    search_queries: List[str]
    # The results of the search queries
    search_results: List[dict]
    # The final report
    final_report: str


# 3. Define the Nodes for the graph
llm = ChatOpenAI(model="gpt-4o")

def planning_node(state: ResearchAgentState):
    """
    The first step is to plan the research. This node will take the user's
    question and generate a list of search queries.
    """
    planner_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "You are an expert research assistant. Your goal is to generate a list of "
             "3-5 search queries that will help answer the user's question. "
             "Return your answer as a list of strings, separated by newlines.\n"
             "For example:\n"
             "What is the capital of France?\n"
             "Who is the current prime minister of Canada?\n"
             "History of the internet"),
            ("human", "{question}"),
        ]
    )
    planner = planner_prompt | llm
    response = planner.invoke({"question": state["question"]})
    search_queries = response.content.strip().split("\n")
    return {"search_queries": search_queries}


def search_node(state: ResearchAgentState):
    """
    This node executes the search queries in parallel.
    We use the .map() method of the tool to do this.
    """
    print("---Executing Searches---")
    search_queries = state["search_queries"]
    # The .map() method executes the tool for each query in the list
    search_results = search_tool.map(search_queries)
    return {"search_results": search_results}


def reporting_node(state: ResearchAgentState):
    """
    This node takes the search results and synthesizes them into a final report.
    """
    print("---Generating Report---")
    reporter_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert research analyst. Your task is to write a detailed report
        based on the provided research results.
        
        Original Question:
        {question}
        
        Research Results:
        {search_results}
        
        Please provide a comprehensive report that answers the original question.
        """
    )
    reporter = reporter_prompt | llm
    response = reporter.invoke(
        {
            "question": state["question"],
            "search_results": state["search_results"],
        }
    )
    return {"final_report": response.content}


# 4. Build the Graph
def build_graph():
    """Builds the research agent graph."""
    builder = StateGraph(ResearchAgentState)

    # Add the nodes
    builder.add_node("planner", planning_node)
    builder.add_node("searcher", search_node)
    builder.add_node("reporter", reporting_node)

    # Define the edges
    builder.add_edge("planner", "searcher")
    builder.add_edge("searcher", "reporter")
    builder.add_edge("reporter", END)

    # Set the entry point
    builder.set_entry_point("planner")

    return builder.compile()


def main():
    """
    Runs the complex research agent.
    """
    graph = build_graph()

    # Get user input
    question = input("What would you like to research? ")

    # Invoke the graph
    # The initial state is the user's question
    initial_state = {"question": question}
    final_state = graph.invoke(initial_state)

    # Print the final report
    print("\n---Final Report---")
    print(final_state["final_report"])


if __name__ == "__main__":
    main() 