#!/usr/bin/env python3
"""
Test to show how real Demo Company data flows through forecast calculation
"""

import sys
sys.path.append('src')

import os
from dotenv import load_dotenv
load_dotenv(override=True)

from src.agent import FinancialForecastAgent
from src.tools.forecast_tools import FinancialForecastCalculator

def test_forecast_with_real_data():
    """Test to show real Demo Company data flows through forecast calculation."""
    
    print("🧮 TESTING FORECAST CALCULATION WITH REAL DEMO COMPANY DATA")
    print("=" * 80)
    
    # Initialize agent
    agent = FinancialForecastAgent()
    
    # Get real Xero data
    print("📊 Step 1: Getting Real Demo Company YTD Data...")
    print("-" * 60)
    xero_data = agent.xero.get_profit_and_loss()
    
    if xero_data and len(xero_data) > 0:
        real_data = xero_data[0]
        data_source = real_data.get('data_source', 'Unknown')
        
        print(f"✅ Data Source: {data_source}")
        
        if "Real Xero Data" in data_source:
            print("\n📈 REAL DEMO COMPANY BASE DATA (YTD 2025):")
            print("-" * 60)
            print(f"💰 Revenue:           ${real_data['revenue']:>12,.2f}")
            print(f"📦 Cost of Sales:     ${real_data['cost_of_goods_sold']:>12,.2f}")
            print(f"💰 Gross Profit:      ${real_data['gross_profit']:>12,.2f}")
            print(f"💸 Operating Exp:     ${real_data['operating_expenses']:>12,.2f}")
            print(f"📈 Net Income:        ${real_data['net_income']:>12,.2f}")
            
            # Create sample assumptions for forecast
            assumptions = {
                'revenue_growth_rate': '15%',
                'cost_of_goods_sold': '9%',  # Based on real data: 2340/26505 = ~9%
                'operating_expense_growth': '10%',
                'tax_rate': '25%',
                'depreciation_rate': '10%',
                'market_factors': 'AI and tech growth in SF',
                'risk_factors': 'Economic uncertainty',
                'growth_drivers': 'Technology adoption'
            }
            
            print(f"\n🎯 FORECAST ASSUMPTIONS:")
            print("-" * 60)
            print(f"Revenue Growth:       {assumptions['revenue_growth_rate']}")
            print(f"COGS Rate:           {assumptions['cost_of_goods_sold']}")
            print(f"OpEx Growth:         {assumptions['operating_expense_growth']}")
            print(f"Tax Rate:            {assumptions['tax_rate']}")
            
            # Calculate forecast using real data
            calculator = FinancialForecastCalculator()
            forecast_results = calculator.calculate_forecast(xero_data, assumptions)
            
            print(f"\n🚀 5-YEAR FORECAST BASED ON REAL DEMO COMPANY DATA:")
            print("=" * 80)
            print(f"{'Year':<8} {'Revenue':<12} {'COGS':<12} {'Gross Profit':<14} {'OpEx':<12} {'Net Income':<12}")
            print("-" * 80)
            
            # Show base year (real data)
            print(f"{'Base':<8} ${real_data['revenue']:<11,.0f} ${real_data['cost_of_goods_sold']:<11,.0f} ${real_data['gross_profit']:<13,.0f} ${real_data['operating_expenses']:<11,.0f} ${real_data['net_income']:<11,.0f}")
            
            # Show forecast years
            for year in range(1, 6):
                year_data = forecast_results[f'year_{year}']
                print(f"{'Year '+str(year):<8} ${year_data['revenue']:<11,.0f} ${year_data['cost_of_goods_sold']:<11,.0f} ${year_data['gross_profit']:<13,.0f} ${year_data['operating_expenses']:<11,.0f} ${year_data['net_income']:<11,.0f}")
            
            # Calculate key metrics
            metrics = calculator.calculate_key_metrics(forecast_results)
            
            print(f"\n📊 FORECAST SUMMARY:")
            print("-" * 60)
            print(f"Total 5-Year Revenue: ${metrics['total_revenue_5yr']:,.0f}")
            print(f"Avg Revenue Growth:   {metrics['average_revenue_growth']*100:.1f}%")
            print(f"Avg Gross Margin:     {metrics['average_gross_margin']*100:.1f}%")
            print(f"Avg EBITDA Margin:    {metrics['average_ebitda_margin']*100:.1f}%")
            
            print(f"\n🎉 SUCCESS: FORECAST USES REAL DEMO COMPANY DATA!")
            print("✅ The forecast calculations are based on actual YTD financial performance")
            print("✅ Real Demo Company metrics serve as the baseline for 5-year projections")
            
        else:
            print(f"⚠️ Using fallback data: {data_source}")
    else:
        print("❌ No data returned")

if __name__ == "__main__":
    test_forecast_with_real_data()