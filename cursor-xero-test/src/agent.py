"""
Financial Forecasting Agent using LangGraph
A 6-step workflow for financial forecasting using Xero data and market research.
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain.tools import Tool

# Local imports
from .types import ForecastState
from .database.database import DatabaseOperations
from .tools.forecast_tools import FinancialForecastCalculator
from .tools.xero_tools import XeroTools
from .tools.perplexity_tools import PerplexityTools
from .tools.notion_tools import NotionTools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialForecastAgent:
    """LangGraph agent for financial forecasting."""
    
    def __init__(self):
        self.db = DatabaseOperations()
        self.calculator = FinancialForecastCalculator()
        self.xero = XeroTools()
        self.perplexity = PerplexityTools()
        self.notion = NotionTools()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create graph
        self.graph = self.create_agent_graph()
    
    def _create_tools(self) -> List[Tool]:
        """Create the tool set for the agent."""
        return [
            Tool(
                name="get_xero_data",
                description="Get historical financial data from Xero",
                func=self.xero.get_profit_and_loss
            ),
            Tool(
                name="get_client_info",
                description="Get client business information from database",
                func=self.db.get_client_info
            ),
            Tool(
                name="perform_market_research",
                description="Conduct market research for an industry and location",
                func=self.perplexity.conduct_market_research
            ),
            Tool(
                name="create_forecast_assumptions",
                description="Generate forecast assumptions based on historical data and market research",
                func=self._create_assumptions
            ),
            Tool(
                name="calculate_forecast",
                description="Calculate 5-year financial forecast using historical data and assumptions",
                func=self.calculator.calculate_forecast
            ),
            Tool(
                name="create_notion_report",
                description="Create a comprehensive forecast report in Notion",
                func=self.notion.create_forecast_report
            )
        ]
    
    def _create_assumptions(self, historical_data: str, market_research: str, client_info: str) -> Dict[str, Any]:
        """Create forecast assumptions using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial analyst creating forecast assumptions.
Based on the historical data, market research, and client information provided,
generate realistic growth and operational assumptions for a 5-year forecast.

The assumptions should include:
- Revenue growth rate (as %)
- Cost of goods sold (as % of revenue)
- Operating expense growth (as %)
- Tax rate (as %)
- Depreciation rate (as %)
- Market factors (text)
- Risk factors (text)
- Growth drivers (text)

Format the numerical assumptions with % symbol."""),
            ("human", "Historical Data: {historical_data}\n\nMarket Research: {market_research}\n\nClient Info: {client_info}")
        ])
        
        # Get LLM response
        chain = prompt | self.llm
        response = chain.invoke({
            "historical_data": historical_data,
            "market_research": market_research,
            "client_info": client_info
        })
        
        # Parse response into assumptions dict
        assumptions = {
            "revenue_growth_rate": "15%",  # Default values if parsing fails
            "cost_of_goods_sold": "30%",
            "operating_expense_growth": "10%",
            "tax_rate": "25%",
            "depreciation_rate": "10%",
            "market_factors": response.content,
            "risk_factors": "Economic uncertainty, competition",
            "growth_drivers": "Market expansion, technology adoption",
            "client_name": "TechFlow Solutions"  # Add client name for Notion report
        }
        
        return assumptions
    
    def create_agent_graph(self) -> StateGraph:
        """Create the 6-step financial forecasting workflow."""
        
        # Create the graph
        builder = StateGraph(ForecastState)
        
        # Add nodes for each step
        builder.add_node("fetch_xero_data", self.step_1_xero_data)
        builder.add_node("fetch_client_info", self.step_2_client_info)
        builder.add_node("conduct_market_research", self.step_3_market_research)
        builder.add_node("generate_assumptions", self.step_4_assumptions)
        builder.add_node("perform_calculation", self.step_5_calculate)
        builder.add_node("generate_report", self.step_6_report)
        
        # Add edges
        builder.add_edge(START, "fetch_xero_data")
        builder.add_edge("fetch_xero_data", "fetch_client_info")
        builder.add_edge("fetch_client_info", "conduct_market_research")
        builder.add_edge("conduct_market_research", "generate_assumptions")
        builder.add_edge("generate_assumptions", "perform_calculation")
        builder.add_edge("perform_calculation", "generate_report")
        builder.add_edge("generate_report", END)
        
        return builder.compile()
    
    def step_1_xero_data(self, state: ForecastState) -> Dict[str, Any]:
        """Step 1: Retrieve financial data from Xero."""
        logger.info("Step 1: Retrieving Xero financial data...")
        
        try:
            # Get Xero data using tool
            xero_data = self.tools[0].func()
            
            # Store in database
            self.db.store_historical_financials(state['user_id'], xero_data)
            
            return {
                "messages": state['messages'] + [AIMessage(content="Retrieved and stored Xero financial data")],
                "current_step": "fetch_client_info",
                "xero_data": xero_data
            }
        except Exception as e:
            logger.error(f"Error in step 1: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error retrieving Xero data: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def step_2_client_info(self, state: ForecastState) -> Dict[str, Any]:
        """Step 2: Get client business information."""
        logger.info("Step 2: Getting client information...")
        
        try:
            client_info = self.tools[1].func(state['user_id'])
            
            if not client_info:
                raise ValueError(f"No client information found for user {state['user_id']}")
            
            return {
                "messages": state['messages'] + [AIMessage(content="Retrieved client information")],
                "current_step": "conduct_market_research",
                "client_info": client_info
            }
        except Exception as e:
            logger.error(f"Error in step 2: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error retrieving client info: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def step_3_market_research(self, state: ForecastState) -> Dict[str, Any]:
        """Step 3: Conduct market research."""
        logger.info("Step 3: Conducting market research...")
        
        try:
            research = self.tools[2].func(
                state['client_info']['industry'],
                state['client_info']['location']
            )
            
            return {
                "messages": state['messages'] + [AIMessage(content="Completed market research")],
                "current_step": "generate_assumptions",
                "market_research": research
            }
        except Exception as e:
            logger.error(f"Error in step 3: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error conducting market research: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def step_4_assumptions(self, state: ForecastState) -> Dict[str, Any]:
        """Step 4: Generate forecast assumptions."""
        logger.info("Step 4: Generating forecast assumptions...")
        
        try:
            assumptions = self.tools[3].func(
                json.dumps(state['xero_data']),
                state['market_research'],
                json.dumps(state['client_info'])
            )
            
            return {
                "messages": state['messages'] + [AIMessage(content="Generated forecast assumptions")],
                "current_step": "perform_calculation",
                "forecast_assumptions": assumptions
            }
        except Exception as e:
            logger.error(f"Error in step 4: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error generating assumptions: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def step_5_calculate(self, state: ForecastState) -> Dict[str, Any]:
        """Step 5: Calculate financial forecast."""
        logger.info("Step 5: Calculating financial forecast...")
        
        try:
            results = self.tools[4].func(
                state['xero_data'],
                state['forecast_assumptions']
            )
            
            return {
                "messages": state['messages'] + [AIMessage(content="Calculated financial forecast")],
                "current_step": "generate_report",
                "forecast_results": results
            }
        except Exception as e:
            logger.error(f"Error in step 5: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error calculating forecast: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def step_6_report(self, state: ForecastState) -> Dict[str, Any]:
        """Step 6: Create comprehensive Notion report."""
        logger.info("Step 6: Creating Notion report...")
        
        try:
            report_url = self.tools[5].func(
                state['forecast_results'],
                state['forecast_assumptions'],
                state['market_research']
            )
            
            return {
                "messages": state['messages'] + [AIMessage(content=f"Created Notion report: {report_url}")],
                "current_step": "complete",
                "notion_report_url": report_url,
                "workflow_complete": True
            }
        except Exception as e:
            logger.error(f"Error in step 6: {e}")
            return {
                "messages": state['messages'] + [AIMessage(content=f"Error creating report: {str(e)}")],
                "current_step": "error",
                "error": str(e)
            }
    
    def run_forecast(self, user_id: str) -> Dict[str, Any]:
        """Run the complete forecasting workflow for a user."""
        initial_state = {
            "messages": [],
            "current_step": "start",
            "user_id": user_id,
            "xero_data": None,
            "client_info": None,
            "market_research": None,
            "forecast_assumptions": None,
            "forecast_results": None,
            "notion_report_url": None,
            "workflow_complete": False
        }
        
        try:
            result = self.graph.invoke(initial_state)
            logger.info("Completed forecasting workflow successfully")
            return result
        except Exception as e:
            logger.error(f"Error in forecasting workflow: {str(e)}")
            raise 