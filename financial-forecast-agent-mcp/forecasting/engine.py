"""
Core financial forecasting engine with three-statement model.
Handles P&L projections, validation, and iterative feedback.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FinancialForecastEngine:
    """
    Three-statement financial model with iterative feedback capability.
    Focuses on P&L forecasting with validation and scenario analysis.
    """
    
    def __init__(self, historical_data: List[Dict[str, Any]], assumptions: Dict[str, Any]):
        self.historical_data = historical_data
        self.assumptions = assumptions
        self.validation_results = {}
        
    def calculate_pnl_forecast(self, years: int = 5, base_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculate P&L forecast for specified number of years.
        
        Args:
            years: Number of years to forecast
            base_year: Base year for calculations (defaults to current year)
            
        Returns:
            List of annual P&L projections
        """
        try:
            base_year = base_year or datetime.now().year
            
            # Get baseline financials from historical data
            baseline = self._get_baseline_financials()
            
            forecasts = []
            for year in range(1, years + 1):
                forecast_year = base_year + year
                
                # Calculate revenue
                revenue = self._calculate_revenue(baseline['revenue'], year)
                
                # Calculate COGS
                cogs = self._calculate_cogs(revenue)
                
                # Calculate gross profit
                gross_profit = revenue - cogs
                
                # Calculate operating expenses
                operating_expenses = self._calculate_opex(baseline['operating_expenses'], year)
                
                # Calculate EBITDA
                ebitda = gross_profit - operating_expenses
                
                # Calculate depreciation
                depreciation = self._calculate_depreciation(baseline.get('depreciation', 0), year)
                
                # Calculate EBIT
                ebit = ebitda - depreciation
                
                # Calculate interest expense
                interest_expense = self._calculate_interest(baseline.get('interest_expense', 0), year)
                
                # Calculate taxes
                tax_expense = self._calculate_taxes(ebit - interest_expense)
                
                # Calculate net income
                net_income = ebit - interest_expense - tax_expense
                
                # Calculate key metrics
                gross_margin = (gross_profit / revenue) * 100 if revenue > 0 else 0
                ebitda_margin = (ebitda / revenue) * 100 if revenue > 0 else 0
                net_margin = (net_income / revenue) * 100 if revenue > 0 else 0
                
                forecast = {
                    'year': forecast_year,
                    'revenue': round(revenue, 2),
                    'cogs': round(cogs, 2),
                    'gross_profit': round(gross_profit, 2),
                    'operating_expenses': round(operating_expenses, 2),
                    'ebitda': round(ebitda, 2),
                    'depreciation': round(depreciation, 2),
                    'ebit': round(ebit, 2),
                    'interest_expense': round(interest_expense, 2),
                    'tax_expense': round(tax_expense, 2),
                    'net_income': round(net_income, 2),
                    'gross_margin': round(gross_margin, 1),
                    'ebitda_margin': round(ebitda_margin, 1),
                    'net_margin': round(net_margin, 1)
                }
                
                forecasts.append(forecast)
                
            logger.info(f"✅ Generated {years}-year P&L forecast")
            return forecasts
            
        except Exception as e:
            logger.error(f"❌ P&L forecast calculation failed: {e}")
            return []
    
    def _get_baseline_financials(self) -> Dict[str, float]:
        """Extract baseline financial metrics from historical data."""
        if not self.historical_data:
            # Return default baseline for demo
            return {
                'revenue': 1000000.0,
                'cogs': 350000.0,
                'operating_expenses': 420000.0,
                'ebitda': 230000.0,
                'depreciation': 50000.0,
                'interest_expense': 20000.0,
                'net_income': 120000.0
            }
        
        # Use most recent historical data as baseline
        latest_data = self.historical_data[0] if self.historical_data else {}
        
        return {
            'revenue': latest_data.get('revenue', 1000000.0),
            'cogs': latest_data.get('cogs', 350000.0),
            'operating_expenses': latest_data.get('operating_expenses', 420000.0),
            'ebitda': latest_data.get('ebitda', 230000.0),
            'depreciation': latest_data.get('depreciation', 50000.0),
            'interest_expense': latest_data.get('interest_expense', 20000.0),
            'net_income': latest_data.get('net_income', 120000.0)
        }
    
    def _calculate_revenue(self, base_revenue: float, year: int) -> float:
        """Calculate revenue for a given year."""
        growth_rate = self.assumptions.get('revenue_growth_rate', 0.15)
        
        # Apply compound growth
        return base_revenue * ((1 + growth_rate) ** year)
    
    def _calculate_cogs(self, revenue: float) -> float:
        """Calculate Cost of Goods Sold as percentage of revenue."""
        cogs_percentage = self.assumptions.get('cogs_percentage', 0.35)
        return revenue * cogs_percentage
    
    def _calculate_opex(self, base_opex: float, year: int) -> float:
        """Calculate operating expenses with growth rate."""
        opex_growth_rate = self.assumptions.get('opex_growth_rate', 0.08)
        
        # Apply compound growth to operating expenses
        return base_opex * ((1 + opex_growth_rate) ** year)
    
    def _calculate_depreciation(self, base_depreciation: float, year: int) -> float:
        """Calculate depreciation based on depreciation rate."""
        depreciation_rate = self.assumptions.get('depreciation_rate', 0.10)
        
        # Simple model: depreciation grows with revenue base
        baseline = self._get_baseline_financials()
        revenue_multiple = self._calculate_revenue(baseline['revenue'], year) / baseline['revenue']
        
        return base_depreciation * revenue_multiple * (1 + depreciation_rate * (year - 1))
    
    def _calculate_interest(self, base_interest: float, year: int) -> float:
        """Calculate interest expense (simplified model)."""
        # Assume interest expense remains relatively stable or grows slowly
        interest_growth = 0.05  # 5% annual growth
        return base_interest * ((1 + interest_growth) ** year)
    
    def _calculate_taxes(self, pre_tax_income: float) -> float:
        """Calculate tax expense based on pre-tax income."""
        tax_rate = self.assumptions.get('tax_rate', 0.25)
        
        # Only apply taxes if there's positive pre-tax income
        return max(0, pre_tax_income * tax_rate)
    
    def validate_forecast(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate forecast projections for reasonableness.
        
        Args:
            forecasts: List of annual forecast projections
            
        Returns:
            Validation results with warnings and recommendations
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'recommendations': [],
            'key_metrics': {}
        }
        
        try:
            if not forecasts:
                validation_results['is_valid'] = False
                validation_results['warnings'].append("No forecast data to validate")
                return validation_results
            
            # Calculate key validation metrics
            first_year = forecasts[0]
            last_year = forecasts[-1]
            
            # Revenue growth validation
            total_revenue_growth = ((last_year['revenue'] / first_year['revenue']) - 1) * 100
            avg_annual_growth = (total_revenue_growth / len(forecasts))
            
            validation_results['key_metrics']['total_revenue_growth'] = round(total_revenue_growth, 1)
            validation_results['key_metrics']['avg_annual_growth'] = round(avg_annual_growth, 1)
            
            # Validate revenue growth reasonableness
            if avg_annual_growth > 50:
                validation_results['warnings'].append(f"Very high revenue growth ({avg_annual_growth:.1f}% annually)")
                validation_results['recommendations'].append("Consider more conservative growth assumptions")
            elif avg_annual_growth < 0:
                validation_results['warnings'].append("Negative revenue growth projected")
                validation_results['recommendations'].append("Review market assumptions and growth drivers")
            
            # Margin validation
            for year_data in forecasts:
                # Check for negative margins
                if year_data['gross_margin'] < 0:
                    validation_results['warnings'].append(f"Negative gross margin in {year_data['year']}")
                    validation_results['is_valid'] = False
                
                if year_data['ebitda_margin'] < -20:
                    validation_results['warnings'].append(f"Very poor EBITDA margin ({year_data['ebitda_margin']:.1f}%) in {year_data['year']}")
                
                # Check for unrealistic margins
                if year_data['gross_margin'] > 90:
                    validation_results['warnings'].append(f"Unusually high gross margin ({year_data['gross_margin']:.1f}%) in {year_data['year']}")
            
            # Cash flow validation (simplified)
            negative_years = [year['year'] for year in forecasts if year['net_income'] < 0]
            if len(negative_years) > 2:
                validation_results['warnings'].append(f"Multiple years of losses: {negative_years}")
                validation_results['recommendations'].append("Review cost structure and timeline to profitability")
            
            # COGS consistency
            cogs_percentages = [(year['cogs'] / year['revenue']) * 100 for year in forecasts if year['revenue'] > 0]
            if cogs_percentages:
                cogs_variance = max(cogs_percentages) - min(cogs_percentages)
                if cogs_variance > 10:  # More than 10% variance in COGS %
                    validation_results['warnings'].append(f"High variance in COGS percentage ({cogs_variance:.1f}%)")
                    validation_results['recommendations'].append("Review COGS assumptions for consistency")
            
            logger.info("✅ Forecast validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Forecast validation failed: {e}")
            validation_results['is_valid'] = False
            validation_results['warnings'].append(f"Validation error: {str(e)}")
            return validation_results
    
    def generate_scenarios(self, base_forecasts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate optimistic and pessimistic scenarios.
        
        Args:
            base_forecasts: Base case forecast projections
            
        Returns:
            Dictionary with base, optimistic, and pessimistic scenarios
        """
        try:
            scenarios = {
                'base': base_forecasts,
                'optimistic': self._adjust_scenario(base_forecasts, 1.2),  # 20% better
                'pessimistic': self._adjust_scenario(base_forecasts, 0.8)  # 20% worse
            }
            
            logger.info("✅ Generated forecast scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"❌ Scenario generation failed: {e}")
            return {'base': base_forecasts}
    
    def _adjust_scenario(self, base_forecasts: List[Dict[str, Any]], multiplier: float) -> List[Dict[str, Any]]:
        """Adjust forecast scenario by multiplier."""
        adjusted_forecasts = []
        
        for forecast in base_forecasts:
            adjusted = forecast.copy()
            
            # Adjust key revenue drivers
            adjusted['revenue'] = round(forecast['revenue'] * multiplier, 2)
            adjusted['cogs'] = round(forecast['cogs'] * multiplier, 2)
            adjusted['gross_profit'] = adjusted['revenue'] - adjusted['cogs']
            
            # Keep operating expenses more stable (only 50% of the adjustment)
            opex_multiplier = 1 + ((multiplier - 1) * 0.5)
            adjusted['operating_expenses'] = round(forecast['operating_expenses'] * opex_multiplier, 2)
            
            # Recalculate derived metrics
            adjusted['ebitda'] = adjusted['gross_profit'] - adjusted['operating_expenses']
            adjusted['ebit'] = adjusted['ebitda'] - forecast['depreciation']  # Keep depreciation stable
            adjusted['net_income'] = round(adjusted['ebit'] - forecast['interest_expense'] - forecast['tax_expense'], 2)
            
            # Recalculate margins
            if adjusted['revenue'] > 0:
                adjusted['gross_margin'] = round((adjusted['gross_profit'] / adjusted['revenue']) * 100, 1)
                adjusted['ebitda_margin'] = round((adjusted['ebitda'] / adjusted['revenue']) * 100, 1)
                adjusted['net_margin'] = round((adjusted['net_income'] / adjusted['revenue']) * 100, 1)
            
            adjusted_forecasts.append(adjusted)
        
        return adjusted_forecasts
    
    def get_recommendation(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate recommendation based on validation results.
        
        Args:
            validation_results: Results from validate_forecast()
            
        Returns:
            Recommendation string for the agent
        """
        if validation_results['is_valid'] and not validation_results['warnings']:
            return "APPROVED: Forecast projections appear reasonable and well-balanced."
        
        elif validation_results['is_valid'] and validation_results['warnings']:
            warnings_text = "; ".join(validation_results['warnings'][:3])  # Limit to top 3
            recommendations_text = "; ".join(validation_results['recommendations'][:2])  # Limit to top 2
            return f"CONDITIONAL APPROVAL: {warnings_text}. Recommendations: {recommendations_text}"
        
        else:
            critical_issues = "; ".join(validation_results['warnings'][:2])
            return f"REVISION REQUIRED: {critical_issues}. Please revise assumptions and recalculate."