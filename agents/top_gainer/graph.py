from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from .tools import get_top_gainer, search_gainer_news
from core.rag_resource import create_rag_tool_from_directory


class TopGainerState(TypedDict):
    top_gainer_data: dict
    news_summary: str
    document_analysis: str  # New field for RAG results
    final_rating: str  # Changed from final_report
    error: str


class TopGainerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        # The RAG tool is created once during initialization
        self.rag_tool = create_rag_tool_from_directory(
            "data/stock_analysis_reports/",
            name="InternalReportSearchTool",
            description="Searches internal financial analysis documents for insights on a stock."
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(TopGainerState)

        builder.add_node("get_top_gainer", self.get_top_gainer_node)
        builder.add_node("research_gainer", self.research_gainer_node)
        builder.add_node("analyze_local_report", self.analyze_local_report_node) # New RAG node
        builder.add_node("generate_final_rating", self.generate_final_rating_node) # Modified final node

        builder.add_edge(START, "get_top_gainer")
        builder.add_edge("get_top_gainer", "research_gainer")
        builder.add_edge("research_gainer", "analyze_local_report") # New edge
        builder.add_edge("analyze_local_report", "generate_final_rating") # New edge
        builder.add_edge("generate_final_rating", END)

        return builder.compile()

    def get_top_gainer_node(self, state: TopGainerState):
        print("--- Fetching Top Gainer ---")
        gainer_data = get_top_gainer.invoke({})
        if gainer_data.get("error"):
            print(f"Error: {gainer_data['error']}")
            return {**state, "error": gainer_data["error"]}
        print(f"Found Top Gainer: {gainer_data['ticker']}")
        return {**state, "top_gainer_data": gainer_data}

    def research_gainer_node(self, state: TopGainerState):
        print("\n--- Researching Public News ---")
        if state.get("error"):
            return state
        gainer = state["top_gainer_data"]
        news_summary = search_gainer_news.invoke({
            "ticker": gainer["ticker"],
            "company_name": gainer["company_name"]
        })
        print("Finished researching public news.")
        return {**state, "news_summary": news_summary}

    def analyze_local_report_node(self, state: TopGainerState):
        print("\n--- Analyzing Internal Documents (RAG) ---")
        if state.get("error"):
            return state
        gainer = state["top_gainer_data"]
        query = f"What is the internal analysis or rating for {gainer['ticker']}?"
        doc_analysis = self.rag_tool.invoke(query)
        print(f"Internal Document Analysis Result: {doc_analysis}")
        return {**state, "document_analysis": doc_analysis}

    def generate_final_rating_node(self, state: TopGainerState):
        print("\n--- Generating Final Analyst Rating ---")
        if state.get("error"):
            return {**state, "final_rating": state["error"]}

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior financial analyst. Your task is to provide a final stock rating (e.g., Strong Buy, Buy, Hold, Sell, Strong Sell) and a concise justification based on all available data. Integrate the public news with the internal analysis from our documents."),
            ("human", """
                Here is the data for {ticker}:

                **Performance Data:**
                - Price: {price}
                - Change: {change_amount} ({change_percentage})
                - Volume: {volume}

                **Public News Summary (from Tavily):**
                {news_summary}

                **Internal Document Analysis (from RAG):**
                {document_analysis}

                Please provide your final rating and a 2-3 sentence justification.
            """)
        ])
        
        chain = prompt | self.llm
        gainer_data = state["top_gainer_data"]
        report = chain.invoke({
            "ticker": gainer_data["ticker"],
            "price": gainer_data["price"],
            "change_amount": gainer_data["change_amount"],
            "change_percentage": gainer_data["change_percentage"],
            "volume": gainer_data["volume"],
            "news_summary": state["news_summary"],
            "document_analysis": state["document_analysis"]
        })
        
        return {**state, "final_rating": report.content}

    def run(self):
        return self.graph.invoke({})
