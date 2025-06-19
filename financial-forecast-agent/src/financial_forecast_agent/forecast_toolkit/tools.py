"""Tools for the Financial Forecasting Agent"""
from typing import Dict, List, Any, Optional
from langchain.tools import tool
import json
import uuid
import sys
import os

# Add the current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from database import ForecastDatabase
    from forecasting_engine import PLForecastingEngine
except ImportError:
    # Fallback for different import contexts
    from .database import ForecastDatabase
    from .forecasting_engine import PLForecastingEngine


@tool
def get_client_information(user_id: str) -> str:
    """
    Retrieve client information from the database including industry, business age, location, and strategy.
    
    Args:
        user_id: The user ID to look up client information for
        
    Returns:
        JSON string containing client information
    """
    try:
        with ForecastDatabase() as db:
            client_info = db.get_client_info(user_id)
            if client_info:
                return json.dumps(client_info, indent=2)
            else:
                return json.dumps({"error": f"No client found with user_id: {user_id}"})
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})


@tool
def get_historical_financial_data(user_id: str) -> str:
    """
    Retrieve historical financial data for a client from the database.
    
    Args:
        user_id: The user ID to retrieve historical data for
        
    Returns:
        JSON string containing historical financial data
    """
    try:
        with ForecastDatabase() as db:
            historical_data = db.get_historical_data(user_id)
            return json.dumps(historical_data, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})


@tool
def store_xero_financial_data(user_id: str, xero_data: str) -> str:
    """
    Store financial data retrieved from Xero into the database as historical records.
    
    Args:
        user_id: The user ID to store data for
        xero_data: JSON string containing Xero financial data
        
    Returns:
        JSON string indicating success or failure
    """
    try:
        xero_dict = json.loads(xero_data) if isinstance(xero_data, str) else xero_data
        with ForecastDatabase() as db:
            success = db.store_xero_data(user_id, xero_dict)
            if success:
                return json.dumps({"status": "success", "message": "Xero data stored successfully"})
            else:
                return json.dumps({"status": "error", "message": "Failed to store Xero data"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error storing Xero data: {str(e)}"})


@tool
def calculate_financial_forecast(historical_data: str, assumptions: str) -> str:
    """
    Calculate 5-year P&L forecast based on historical data and assumptions.
    
    Args:
        historical_data: JSON string containing historical financial data
        assumptions: JSON string containing forecast assumptions
        
    Returns:
        JSON string containing detailed forecast results
    """
    try:
        # Parse inputs
        hist_data = json.loads(historical_data) if isinstance(historical_data, str) else historical_data
        assump_data = json.loads(assumptions) if isinstance(assumptions, str) else assumptions
        
        # Create forecasting engine and calculate
        engine = PLForecastingEngine()
        forecast_results = engine.calculate_forecast(hist_data, assump_data)
        
        return json.dumps(forecast_results, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Forecasting error: {str(e)}"})


@tool
def validate_forecast_assumptions(assumptions: str) -> str:
    """
    Validate forecast assumptions and provide feedback and recommendations.
    
    Args:
        assumptions: JSON string containing forecast assumptions to validate
        
    Returns:
        JSON string with validation results and recommendations
    """
    try:
        assump_data = json.loads(assumptions) if isinstance(assumptions, str) else assumptions
        
        engine = PLForecastingEngine()
        validation_results = engine.validate_assumptions(assump_data)
        
        return json.dumps(validation_results, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Validation error: {str(e)}"})


@tool
def store_forecast_results(user_id: str, forecast_data: str) -> str:
    """
    Store forecast results in the database.
    
    Args:
        user_id: The user ID to store forecast for
        forecast_data: JSON string containing forecast results
        
    Returns:
        JSON string indicating success or failure with forecast ID
    """
    try:
        forecast_dict = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
        forecast_id = str(uuid.uuid4())
        
        with ForecastDatabase() as db:
            success = db.store_forecast(user_id, forecast_id, forecast_dict)
            if success:
                return json.dumps({
                    "status": "success", 
                    "message": "Forecast stored successfully",
                    "forecast_id": forecast_id
                })
            else:
                return json.dumps({"status": "error", "message": "Failed to store forecast"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error storing forecast: {str(e)}"})


@tool
def generate_scenario_analysis(historical_data: str, base_assumptions: str) -> str:
    """
    Generate optimistic, base, and pessimistic forecast scenarios.
    
    Args:
        historical_data: JSON string containing historical financial data
        base_assumptions: JSON string containing base case assumptions
        
    Returns:
        JSON string containing scenario analysis results
    """
    try:
        hist_data = json.loads(historical_data) if isinstance(historical_data, str) else historical_data
        base_assump = json.loads(base_assumptions) if isinstance(base_assumptions, str) else base_assumptions
        
        engine = PLForecastingEngine()
        scenarios = engine.generate_scenario_analysis(hist_data, base_assump)
        
        return json.dumps(scenarios, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Scenario analysis error: {str(e)}"})


@tool
def calculate_key_metrics(forecast_data: str) -> str:
    """
    Calculate key financial metrics and ratios from forecast data.
    
    Args:
        forecast_data: JSON string containing forecast results
        
    Returns:
        JSON string containing calculated metrics and ratios
    """
    try:
        forecast_dict = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
        
        # Extract yearly forecasts
        yearly_forecasts = forecast_dict.get("yearly_forecasts", [])
        if not yearly_forecasts:
            return json.dumps({"error": "No yearly forecasts found in data"})
        
        # Calculate additional metrics
        metrics = {
            "growth_metrics": {},
            "profitability_metrics": {},
            "efficiency_metrics": {}
        }
        
        # Growth metrics
        first_year = yearly_forecasts[0]
        last_year = yearly_forecasts[-1]
        years = len(yearly_forecasts)
        
        metrics["growth_metrics"] = {
            "revenue_cagr": round(((last_year["revenue"] / first_year["revenue"]) ** (1/years) - 1) * 100, 1),
            "ebitda_cagr": round(((last_year["ebitda"] / first_year["ebitda"]) ** (1/years) - 1) * 100, 1) if first_year["ebitda"] > 0 else "N/A",
            "total_revenue_growth": round(((last_year["revenue"] / first_year["revenue"]) - 1) * 100, 1)
        }
        
        # Profitability metrics (Year 5)
        metrics["profitability_metrics"] = {
            "gross_margin_y5": last_year.get("gross_margin", 0),
            "ebitda_margin_y5": last_year.get("ebitda_margin", 0),
            "net_margin_y5": last_year.get("net_margin", 0)
        }
        
        # Efficiency metrics
        avg_margin_improvement = (last_year.get("ebitda_margin", 0) - first_year.get("ebitda_margin", 0))
        metrics["efficiency_metrics"] = {
            "margin_improvement": round(avg_margin_improvement, 1),
            "revenue_per_dollar_opex_y5": round(last_year["revenue"] / last_year["operating_expenses"], 2) if last_year["operating_expenses"] > 0 else "N/A"
        }
        
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Metrics calculation error: {str(e)}"})


# Export all tools for easy import
forecast_tools = [
    get_client_information,
    get_historical_financial_data,
    store_xero_financial_data,
    calculate_financial_forecast,
    validate_forecast_assumptions,
    store_forecast_results,
    generate_scenario_analysis,
    calculate_key_metrics
]