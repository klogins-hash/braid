"""P&L Forecasting Engine for Financial Forecast Agent"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json


class PLForecastingEngine:
    """Simple P&L forecasting engine that calculates forecasted statements based on assumptions"""
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def calculate_forecast(self, 
                         historical_data: List[Dict[str, Any]], 
                         assumptions: Dict[str, Any],
                         forecast_years: int = 5) -> Dict[str, Any]:
        """
        Calculate P&L forecast based on historical data and assumptions
        
        Args:
            historical_data: List of historical financial data
            assumptions: Dictionary of forecast assumptions
            forecast_years: Number of years to forecast (default 5)
            
        Returns:
            Dictionary containing forecast results and calculations
        """
        if not historical_data:
            raise ValueError("Historical data is required for forecasting")
        
        # Get the most recent year as base
        base_year_data = max(historical_data, key=lambda x: x['period_end'])
        
        # Calculate growth rates from historical data
        historical_growth = self._calculate_historical_growth(historical_data)
        
        # Generate forecast
        forecast_results = {
            "base_year": base_year_data,
            "historical_growth_rates": historical_growth,
            "assumptions": assumptions,
            "yearly_forecasts": [],
            "summary_metrics": {}
        }
        
        # Generate yearly forecasts
        for year_offset in range(1, forecast_years + 1):
            forecast_year = self.current_year + year_offset
            year_forecast = self._calculate_year_forecast(
                base_year_data, assumptions, year_offset, historical_growth
            )
            year_forecast["year"] = forecast_year
            forecast_results["yearly_forecasts"].append(year_forecast)
        
        # Calculate summary metrics
        forecast_results["summary_metrics"] = self._calculate_summary_metrics(
            forecast_results["yearly_forecasts"]
        )
        
        return forecast_results
    
    def _calculate_historical_growth(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate historical growth rates for key metrics"""
        if len(historical_data) < 2:
            return {
                "revenue_cagr": 0.15,  # Default 15% if insufficient data
                "expense_growth": 0.12,  # Default 12%
                "margin_trend": 0.0
            }
        
        # Sort by period
        sorted_data = sorted(historical_data, key=lambda x: x['period_end'])
        
        # Calculate CAGR for revenue
        first_year = sorted_data[0]
        last_year = sorted_data[-1] 
        years = len(sorted_data) - 1
        
        revenue_cagr = (last_year['revenue'] / first_year['revenue']) ** (1/years) - 1
        
        # Calculate average expense growth
        expense_growth_rates = []
        for i in range(1, len(sorted_data)):
            prev_expenses = sorted_data[i-1]['operating_expenses']
            curr_expenses = sorted_data[i]['operating_expenses']
            if prev_expenses > 0:
                growth = (curr_expenses / prev_expenses) - 1
                expense_growth_rates.append(growth)
        
        avg_expense_growth = sum(expense_growth_rates) / len(expense_growth_rates) if expense_growth_rates else 0.12
        
        # Calculate margin trend
        margins = [(d['gross_profit'] / d['revenue']) for d in sorted_data if d['revenue'] > 0]
        margin_trend = (margins[-1] - margins[0]) / len(margins) if len(margins) > 1 else 0.0
        
        return {
            "revenue_cagr": revenue_cagr,
            "expense_growth": avg_expense_growth,
            "margin_trend": margin_trend
        }
    
    def _calculate_year_forecast(self, 
                               base_data: Dict[str, Any], 
                               assumptions: Dict[str, Any],
                               year_offset: int,
                               historical_growth: Dict[str, float]) -> Dict[str, Any]:
        """Calculate forecast for a specific year"""
        
        # Get growth assumptions with fallbacks to historical data
        revenue_growth = assumptions.get("revenue_growth_rate", historical_growth["revenue_cagr"])
        expense_growth = assumptions.get("expense_growth_rate", historical_growth["expense_growth"])
        
        # Apply year-over-year compounding
        revenue = base_data['revenue'] * ((1 + revenue_growth) ** year_offset)
        
        # Calculate COGS based on assumptions or historical ratio
        if "cogs_percentage" in assumptions:
            cogs = revenue * assumptions["cogs_percentage"]
        else:
            cogs_ratio = base_data['cost_of_goods_sold'] / base_data['revenue'] if base_data['revenue'] > 0 else 0.3
            cogs = revenue * cogs_ratio
        
        gross_profit = revenue - cogs
        
        # Calculate operating expenses
        base_opex = base_data['operating_expenses']
        operating_expenses = base_opex * ((1 + expense_growth) ** year_offset)
        
        # Apply any specific expense assumptions
        if "opex_as_percent_revenue" in assumptions:
            operating_expenses = revenue * assumptions["opex_as_percent_revenue"]
        
        # Calculate EBITDA
        ebitda = gross_profit - operating_expenses
        
        # Depreciation
        if "depreciation_rate" in assumptions:
            depreciation = revenue * assumptions["depreciation_rate"]
        else:
            depreciation_ratio = base_data['depreciation'] / base_data['revenue'] if base_data['revenue'] > 0 else 0.02
            depreciation = revenue * depreciation_ratio
        
        # EBIT
        ebit = ebitda - depreciation
        
        # Interest expense
        if "interest_rate" in assumptions:
            interest_expense = assumptions["debt_level"] * assumptions["interest_rate"]
        else:
            interest_ratio = base_data['interest_expense'] / base_data['revenue'] if base_data['revenue'] > 0 else 0.005
            interest_expense = revenue * interest_ratio
        
        # Tax
        tax_rate = assumptions.get("tax_rate", 0.25)  # Default 25%
        pretax_income = ebit - interest_expense
        tax_expense = max(0, pretax_income * tax_rate)  # No tax benefit for losses
        
        # Net income
        net_income = pretax_income - tax_expense
        
        return {
            "revenue": round(revenue, 2),
            "cost_of_goods_sold": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_expenses": round(operating_expenses, 2),
            "ebitda": round(ebitda, 2),
            "depreciation": round(depreciation, 2),
            "ebit": round(ebit, 2),
            "interest_expense": round(interest_expense, 2),
            "tax_expense": round(tax_expense, 2),
            "net_income": round(net_income, 2),
            "gross_margin": round((gross_profit / revenue) * 100, 1) if revenue > 0 else 0,
            "ebitda_margin": round((ebitda / revenue) * 100, 1) if revenue > 0 else 0,
            "net_margin": round((net_income / revenue) * 100, 1) if revenue > 0 else 0
        }
    
    def _calculate_summary_metrics(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics across all forecast years"""
        if not forecasts:
            return {}
        
        total_revenue = sum(f["revenue"] for f in forecasts)
        total_ebitda = sum(f["ebitda"] for f in forecasts)
        avg_growth = ((forecasts[-1]["revenue"] / forecasts[0]["revenue"]) ** (1/len(forecasts))) - 1
        
        return {
            "total_5_year_revenue": round(total_revenue, 2),
            "total_5_year_ebitda": round(total_ebitda, 2),
            "average_annual_growth": round(avg_growth * 100, 1),
            "year_5_revenue": round(forecasts[-1]["revenue"], 2),
            "year_5_ebitda": round(forecasts[-1]["ebitda"], 2),
            "year_5_net_income": round(forecasts[-1]["net_income"], 2)
        }
    
    def validate_assumptions(self, assumptions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate forecast assumptions and provide feedback
        
        Returns:
            Dictionary with validation results and recommendations
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "recommendations": [],
            "adjusted_assumptions": assumptions.copy()
        }
        
        # Revenue growth validation
        revenue_growth = assumptions.get("revenue_growth_rate", 0)
        if revenue_growth > 1.0:  # > 100%
            validation_results["warnings"].append(
                f"Revenue growth rate of {revenue_growth*100:.1f}% seems very aggressive"
            )
        elif revenue_growth < -0.5:  # < -50%
            validation_results["warnings"].append(
                f"Revenue decline of {abs(revenue_growth)*100:.1f}% seems severe"
            )
        
        # Margin validation
        if "cogs_percentage" in assumptions:
            cogs_pct = assumptions["cogs_percentage"]
            if cogs_pct > 0.8:  # > 80%
                validation_results["warnings"].append(
                    f"COGS at {cogs_pct*100:.1f}% of revenue leaves very thin gross margins"
                )
        
        # Expense ratio validation
        if "opex_as_percent_revenue" in assumptions:
            opex_pct = assumptions["opex_as_percent_revenue"] 
            if opex_pct > 0.8:  # > 80%
                validation_results["warnings"].append(
                    f"Operating expenses at {opex_pct*100:.1f}% of revenue may be unsustainable"
                )
        
        # Provide recommendations
        if not validation_results["warnings"]:
            validation_results["recommendations"].append(
                "Assumptions appear reasonable for the forecast model"
            )
        
        return validation_results
    
    def generate_scenario_analysis(self, 
                                 historical_data: List[Dict[str, Any]], 
                                 base_assumptions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimistic, base, and pessimistic scenarios"""
        
        scenarios = {}
        
        # Base case
        scenarios["base"] = self.calculate_forecast(historical_data, base_assumptions)
        
        # Optimistic case (higher growth, better margins)
        optimistic_assumptions = base_assumptions.copy()
        optimistic_assumptions["revenue_growth_rate"] = base_assumptions.get("revenue_growth_rate", 0.15) * 1.5
        optimistic_assumptions["opex_as_percent_revenue"] = base_assumptions.get("opex_as_percent_revenue", 0.6) * 0.9
        scenarios["optimistic"] = self.calculate_forecast(historical_data, optimistic_assumptions)
        
        # Pessimistic case (lower growth, margin pressure)
        pessimistic_assumptions = base_assumptions.copy()
        pessimistic_assumptions["revenue_growth_rate"] = base_assumptions.get("revenue_growth_rate", 0.15) * 0.5
        pessimistic_assumptions["opex_as_percent_revenue"] = base_assumptions.get("opex_as_percent_revenue", 0.6) * 1.1
        scenarios["pessimistic"] = self.calculate_forecast(historical_data, pessimistic_assumptions)
        
        # Summary comparison
        scenarios["scenario_comparison"] = {
            "year_5_revenue": {
                "optimistic": scenarios["optimistic"]["summary_metrics"]["year_5_revenue"],
                "base": scenarios["base"]["summary_metrics"]["year_5_revenue"],
                "pessimistic": scenarios["pessimistic"]["summary_metrics"]["year_5_revenue"]
            },
            "year_5_ebitda": {
                "optimistic": scenarios["optimistic"]["summary_metrics"]["year_5_ebitda"],
                "base": scenarios["base"]["summary_metrics"]["year_5_ebitda"],
                "pessimistic": scenarios["pessimistic"]["summary_metrics"]["year_5_ebitda"]
            }
        }
        
        return scenarios