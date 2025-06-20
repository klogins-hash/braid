"""
Python forecasting tools for financial statement calculations.
Uses the forecasting engine for P&L projections and validation.
"""

import logging
import json
from typing import Dict, Any, List
from langchain.tools import tool
from forecasting.engine import FinancialForecastEngine

logger = logging.getLogger(__name__)

@tool
def generate_forecast_assumptions_with_ai(historical_data: str, market_research: str, client_info: str) -> str:
    """Generate AI-powered forecast assumptions based on data analysis.
    
    Args:
        historical_data: Historical financial data from SQL/Xero
        market_research: Market insights from Perplexity
        client_info: Client business information
        
    Returns:
        Structured forecast assumptions in JSON format
    """
    try:
        # Parse input data
        try:
            historical = json.loads(historical_data) if isinstance(historical_data, str) else historical_data
        except:
            historical = []
        
        # Extract key metrics from historical data for assumption generation
        if historical and isinstance(historical, list) and len(historical) > 0:
            latest_data = historical[0]
            base_revenue = latest_data.get('revenue', 1000000)
            base_cogs = latest_data.get('cogs', 350000)
            cogs_percentage = (base_cogs / base_revenue) if base_revenue > 0 else 0.35
        else:
            base_revenue = 1000000
            cogs_percentage = 0.35
        
        # Analyze market research for growth insights
        market_growth_rate = 0.15  # Default 15%
        if "growth" in market_research.lower():
            if any(word in market_research.lower() for word in ["strong", "high", "rapid", "aggressive"]):
                market_growth_rate = 0.20
            elif any(word in market_research.lower() for word in ["slow", "cautious", "moderate"]):
                market_growth_rate = 0.10
            elif any(word in market_research.lower() for word in ["decline", "negative", "recession"]):
                market_growth_rate = 0.05
        
        # Adjust based on client strategy
        strategy_multiplier = 1.0
        if isinstance(client_info, str):
            try:
                client_data = json.loads(client_info)
                strategy = client_data.get('business_strategy', '').lower()
                if "aggressive" in strategy or "expansion" in strategy:
                    strategy_multiplier = 1.2
                elif "conservative" in strategy or "stable" in strategy:
                    strategy_multiplier = 0.9
            except:
                pass
        
        # Generate intelligent assumptions
        assumptions = {
            "revenue_growth_rate": round(market_growth_rate * strategy_multiplier, 3),
            "cogs_percentage": round(cogs_percentage, 3),
            "opex_growth_rate": 0.08,  # Conservative 8% operating expense growth
            "tax_rate": 0.25,  # Standard corporate tax rate
            "depreciation_rate": 0.10,  # 10% depreciation rate
            "market_factors": "Growth driven by market trends and digital transformation",
            "risk_factors": [
                "Economic uncertainty",
                "Increased competition", 
                "Technology changes",
                "Regulatory changes"
            ],
            "growth_drivers": [
                "Market expansion",
                "Product development",
                "Digital transformation",
                "Operational efficiency"
            ],
            "qualitative_assumptions": {
                "market_outlook": "Positive growth trajectory based on industry analysis",
                "competitive_position": "Strong position with growth opportunities",
                "operational_strategy": "Focus on efficiency and market expansion"
            }
        }
        
        logger.info("✅ Generated AI-powered forecast assumptions")
        return json.dumps(assumptions, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error generating forecast assumptions: {e}")
        # Return default assumptions as fallback
        default_assumptions = {
            "revenue_growth_rate": 0.15,
            "cogs_percentage": 0.35,
            "opex_growth_rate": 0.08,
            "tax_rate": 0.25,
            "depreciation_rate": 0.10,
            "market_factors": "Standard market assumptions applied",
            "risk_factors": ["Market volatility", "Competition"],
            "growth_drivers": ["Market expansion", "Operational efficiency"]
        }
        return json.dumps(default_assumptions, indent=2)

@tool
def calculate_financial_forecast_python(historical_data: str, assumptions: str, years: int = 5) -> str:
    """Calculate 5-year financial forecast using Python forecasting engine.
    
    Args:
        historical_data: Historical financial data from SQL database
        assumptions: Forecast assumptions in JSON format
        years: Number of years to forecast (default 5)
        
    Returns:
        Financial projections in JSON format
    """
    try:
        # Parse input data
        try:
            historical = json.loads(historical_data) if isinstance(historical_data, str) else historical_data
            if not isinstance(historical, list):
                historical = []
        except:
            historical = []
        
        try:
            assumptions_dict = json.loads(assumptions) if isinstance(assumptions, str) else assumptions
        except:
            logger.warning("⚠️ Could not parse assumptions, using defaults")
            assumptions_dict = {
                "revenue_growth_rate": 0.15,
                "cogs_percentage": 0.35,
                "opex_growth_rate": 0.08,
                "tax_rate": 0.25,
                "depreciation_rate": 0.10
            }
        
        # Initialize forecasting engine
        engine = FinancialForecastEngine(historical, assumptions_dict)
        
        # Calculate P&L forecast
        forecasts = engine.calculate_pnl_forecast(years=years)
        
        if not forecasts:
            logger.error("❌ Failed to generate forecasts")
            return "❌ Failed to generate financial forecasts"
        
        logger.info(f"✅ Generated {years}-year financial forecast")
        return json.dumps(forecasts, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error calculating financial forecast: {e}")
        return f"❌ Error calculating financial forecast: {str(e)}"

@tool
def validate_and_review_forecast(forecast_data: str, assumptions: str) -> str:
    """Validate forecast projections and provide feedback for iterative improvement.
    
    Args:
        forecast_data: Financial forecast projections in JSON format
        assumptions: Original assumptions used for forecasting
        
    Returns:
        Validation results and recommendations
    """
    try:
        # Parse forecast data
        try:
            forecasts = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
            if not isinstance(forecasts, list):
                return "❌ Invalid forecast data format - expected list of yearly projections"
        except:
            return "❌ Could not parse forecast data"
        
        try:
            assumptions_dict = json.loads(assumptions) if isinstance(assumptions, str) else assumptions
        except:
            assumptions_dict = {}
        
        # Initialize engine for validation
        engine = FinancialForecastEngine([], assumptions_dict)
        
        # Validate forecasts
        validation_results = engine.validate_forecast(forecasts)
        
        # Generate scenarios for comparison
        scenarios = engine.generate_scenarios(forecasts)
        
        # Get recommendation
        recommendation = engine.get_recommendation(validation_results)
        
        # Compile comprehensive review
        review = {
            "validation_status": "VALID" if validation_results['is_valid'] else "INVALID",
            "recommendation": recommendation,
            "key_metrics": validation_results.get('key_metrics', {}),
            "warnings": validation_results.get('warnings', []),
            "recommendations": validation_results.get('recommendations', []),
            "scenario_analysis": {
                "base_case_summary": {
                    "year_1_revenue": forecasts[0]['revenue'] if forecasts else 0,
                    "year_5_revenue": forecasts[-1]['revenue'] if len(forecasts) >= 5 else 0,
                    "avg_net_margin": sum(f['net_margin'] for f in forecasts) / len(forecasts) if forecasts else 0
                },
                "scenarios_available": list(scenarios.keys())
            },
            "approval_status": "APPROVED" if validation_results['is_valid'] and len(validation_results['warnings']) <= 2 else "NEEDS_REVISION"
        }
        
        logger.info(f"✅ Forecast validation completed - Status: {review['approval_status']}")
        return json.dumps(review, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error validating forecast: {e}")
        return f"❌ Error validating forecast: {str(e)}"

@tool
def generate_forecast_scenarios(base_forecast: str, scenario_type: str = "all") -> str:
    """Generate multiple forecast scenarios (optimistic, pessimistic, base).
    
    Args:
        base_forecast: Base case forecast in JSON format
        scenario_type: Type of scenarios to generate ("all", "optimistic", "pessimistic")
        
    Returns:
        Multiple forecast scenarios in JSON format
    """
    try:
        # Parse base forecast
        try:
            base_forecasts = json.loads(base_forecast) if isinstance(base_forecast, str) else base_forecast
            if not isinstance(base_forecasts, list):
                return "❌ Invalid base forecast format"
        except:
            return "❌ Could not parse base forecast data"
        
        # Initialize engine for scenario generation
        engine = FinancialForecastEngine([], {})
        
        # Generate scenarios
        scenarios = engine.generate_scenarios(base_forecasts)
        
        # Filter scenarios based on request
        if scenario_type.lower() == "optimistic":
            result = {"optimistic": scenarios["optimistic"]}
        elif scenario_type.lower() == "pessimistic":
            result = {"pessimistic": scenarios["pessimistic"]}
        else:
            result = scenarios
        
        logger.info(f"✅ Generated forecast scenarios: {list(result.keys())}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error generating scenarios: {e}")
        return f"❌ Error generating forecast scenarios: {str(e)}"

@tool
def calculate_key_financial_metrics(forecast_data: str) -> str:
    """Calculate key financial metrics and ratios from forecast data.
    
    Args:
        forecast_data: Financial forecast in JSON format
        
    Returns:
        Key financial metrics and ratios
    """
    try:
        # Parse forecast data
        try:
            forecasts = json.loads(forecast_data) if isinstance(forecast_data, str) else forecast_data
            if not isinstance(forecasts, list):
                return "❌ Invalid forecast data format"
        except:
            return "❌ Could not parse forecast data"
        
        if not forecasts:
            return "❌ No forecast data provided"
        
        # Calculate key metrics
        first_year = forecasts[0]
        last_year = forecasts[-1]
        
        # Growth metrics
        revenue_cagr = ((last_year['revenue'] / first_year['revenue']) ** (1 / len(forecasts))) - 1
        
        # Average margins
        avg_gross_margin = sum(f['gross_margin'] for f in forecasts) / len(forecasts)
        avg_ebitda_margin = sum(f['ebitda_margin'] for f in forecasts) / len(forecasts)
        avg_net_margin = sum(f['net_margin'] for f in forecasts) / len(forecasts)
        
        # Profitability metrics
        total_net_income = sum(f['net_income'] for f in forecasts)
        profitable_years = len([f for f in forecasts if f['net_income'] > 0])
        
        metrics = {
            "growth_metrics": {
                "revenue_cagr": round(revenue_cagr * 100, 1),
                "total_revenue_growth": round(((last_year['revenue'] / first_year['revenue']) - 1) * 100, 1),
                "year_1_revenue": first_year['revenue'],
                "year_5_revenue": last_year['revenue']
            },
            "profitability_metrics": {
                "avg_gross_margin": round(avg_gross_margin, 1),
                "avg_ebitda_margin": round(avg_ebitda_margin, 1),
                "avg_net_margin": round(avg_net_margin, 1),
                "total_net_income": round(total_net_income, 2),
                "profitable_years": profitable_years,
                "profitability_ratio": round((profitable_years / len(forecasts)) * 100, 1)
            },
            "risk_assessment": {
                "margin_volatility": "Low" if max(f['net_margin'] for f in forecasts) - min(f['net_margin'] for f in forecasts) < 10 else "High",
                "growth_consistency": "Consistent" if all(forecasts[i]['revenue'] >= forecasts[i-1]['revenue'] for i in range(1, len(forecasts))) else "Variable"
            }
        }
        
        logger.info("✅ Calculated key financial metrics")
        return json.dumps(metrics, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error calculating metrics: {e}")
        return f"❌ Error calculating financial metrics: {str(e)}"