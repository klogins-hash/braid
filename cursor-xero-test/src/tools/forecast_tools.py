"""Financial forecasting calculation tools."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime

class FinancialForecastCalculator:
    """Calculator for financial forecasts based on historical data and assumptions."""
    
    def __init__(self):
        self.forecast_years = 5
    
    def calculate_forecast(self, 
                         historical_data: List[Dict[str, Any]], 
                         assumptions: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Calculate 5-year financial forecast using historical data and assumptions.
        
        Args:
            historical_data: List of historical financial data points
            assumptions: Dictionary of forecast assumptions
            
        Returns:
            Dictionary containing forecast results by year
        """
        # Convert historical data to DataFrame
        df_historical = pd.DataFrame(historical_data)
        
        # Get the most recent year's data as base
        base_data = df_historical.iloc[-1]
        
        # Extract growth rates from assumptions
        revenue_growth = float(assumptions['revenue_growth_rate'].strip('%')) / 100
        cogs_rate = float(assumptions['cost_of_goods_sold'].strip('%')) / 100
        opex_growth = float(assumptions['operating_expense_growth'].strip('%')) / 100
        tax_rate = float(assumptions['tax_rate'].strip('%')) / 100
        
        forecast_results = {}
        
        # Calculate forecast for each year
        for year in range(1, self.forecast_years + 1):
            # Revenue growth
            revenue = base_data['revenue'] * (1 + revenue_growth) ** year
            
            # Cost of goods sold
            cogs = revenue * cogs_rate
            
            # Gross profit
            gross_profit = revenue - cogs
            
            # Operating expenses with growth
            opex = base_data['operating_expenses'] * (1 + opex_growth) ** year
            
            # EBITDA
            ebitda = gross_profit - opex
            
            # Net income (simplified with just tax)
            net_income = ebitda * (1 - tax_rate)
            
            # Store results
            forecast_results[f'year_{year}'] = {
                'revenue': round(revenue, 2),
                'cost_of_goods_sold': round(cogs, 2),
                'gross_profit': round(gross_profit, 2),
                'operating_expenses': round(opex, 2),
                'ebitda': round(ebitda, 2),
                'net_income': round(net_income, 2)
            }
        
        return forecast_results
    
    def validate_assumptions(self, assumptions: Dict[str, Any]) -> bool:
        """
        Validate forecast assumptions.
        
        Args:
            assumptions: Dictionary of forecast assumptions
            
        Returns:
            True if assumptions are valid, False otherwise
        """
        required_rates = [
            'revenue_growth_rate',
            'cost_of_goods_sold',
            'operating_expense_growth',
            'tax_rate',
            'depreciation_rate'
        ]
        
        # Check all required rates exist
        for rate in required_rates:
            if rate not in assumptions:
                return False
            
            # Validate rate format (should be string with %)
            try:
                value = float(assumptions[rate].strip('%')) / 100
                if not (0 <= value <= 10):  # Assuming no growth rate should exceed 1000%
                    return False
            except (ValueError, AttributeError):
                return False
        
        # Validate qualitative assumptions exist
        required_qualitative = ['market_factors', 'risk_factors', 'growth_drivers']
        for field in required_qualitative:
            if field not in assumptions or not assumptions[field]:
                return False
        
        return True
    
    def calculate_key_metrics(self, forecast_results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate key financial metrics from forecast results.
        
        Args:
            forecast_results: Dictionary of forecast results by year
            
        Returns:
            Dictionary of key metrics
        """
        metrics = {
            'average_revenue_growth': 0.0,
            'average_gross_margin': 0.0,
            'average_ebitda_margin': 0.0,
            'total_revenue_5yr': 0.0
        }
        
        prev_revenue = None
        for year in range(1, self.forecast_years + 1):
            year_data = forecast_results[f'year_{year}']
            
            # Calculate growth rate if we have previous revenue
            if prev_revenue:
                growth_rate = (year_data['revenue'] - prev_revenue) / prev_revenue
                metrics['average_revenue_growth'] += growth_rate
            
            # Calculate margins
            gross_margin = year_data['gross_profit'] / year_data['revenue']
            ebitda_margin = year_data['ebitda'] / year_data['revenue']
            
            metrics['average_gross_margin'] += gross_margin
            metrics['average_ebitda_margin'] += ebitda_margin
            metrics['total_revenue_5yr'] += year_data['revenue']
            
            prev_revenue = year_data['revenue']
        
        # Calculate averages
        metrics['average_revenue_growth'] /= (self.forecast_years - 1)
        metrics['average_gross_margin'] /= self.forecast_years
        metrics['average_ebitda_margin'] /= self.forecast_years
        
        # Round all metrics
        return {k: round(v, 4) for k, v in metrics.items()} 