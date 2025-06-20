#!/usr/bin/env python3
"""
Example Financial Agent using Xero Integration

This demonstrates how to use the Xero integration in a simple agent
that analyzes financial performance and provides insights.
"""

import json
from typing import Dict, Any
from core.integrations.xero import get_xero_profit_and_loss, get_xero_balance_sheet

class SimpleFinancialAgent:
    """Simple agent that analyzes Xero financial data."""
    
    def __init__(self):
        """Initialize the agent."""
        print("🤖 Financial Agent initialized")
        print("📊 Ready to analyze Xero financial data")
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get a summary of current financial performance."""
        
        print("\n📈 Retrieving Year-to-Date financial data...")
        
        try:
            # Get YTD P&L data
            pl_response = get_xero_profit_and_loss.invoke({})
            pl_data = json.loads(pl_response)
            
            if "error" in pl_data:
                return {"error": f"Failed to get P&L data: {pl_data['error']}"}
            
            # Extract key financial metrics
            financial_data = pl_data.get("financial_data", {})
            
            if not financial_data:
                return {"error": "No financial data found in P&L report"}
            
            # Calculate key ratios
            revenue = financial_data.get("total_revenue", 0)
            gross_profit = financial_data.get("gross_profit", 0)
            net_income = financial_data.get("net_income", 0)
            expenses = financial_data.get("total_expenses", 0)
            
            # Calculate margins
            gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
            net_margin = (net_income / revenue * 100) if revenue > 0 else 0
            expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0
            
            # Determine financial health
            health_score = self._calculate_health_score(gross_margin, net_margin, expense_ratio)
            
            summary = {
                "report_name": pl_data.get("reportName", ""),
                "report_period": pl_data.get("reportDate", ""),
                "financial_metrics": {
                    "revenue": revenue,
                    "gross_profit": gross_profit,
                    "net_income": net_income,
                    "total_expenses": expenses
                },
                "performance_ratios": {
                    "gross_margin_percent": round(gross_margin, 1),
                    "net_margin_percent": round(net_margin, 1),
                    "expense_ratio_percent": round(expense_ratio, 1)
                },
                "health_assessment": {
                    "score": health_score,
                    "status": self._get_health_status(health_score),
                    "insights": self._generate_insights(financial_data, gross_margin, net_margin)
                }
            }
            
            return summary
            
        except Exception as e:
            return {"error": f"Financial analysis failed: {str(e)}"}
    
    def _calculate_health_score(self, gross_margin: float, net_margin: float, expense_ratio: float) -> int:
        """Calculate a simple financial health score (0-100)."""
        score = 50  # Base score
        
        # Gross margin scoring
        if gross_margin > 70:
            score += 20
        elif gross_margin > 50:
            score += 10
        elif gross_margin < 20:
            score -= 10
        
        # Net margin scoring
        if net_margin > 10:
            score += 20
        elif net_margin > 0:
            score += 10
        elif net_margin < -10:
            score -= 20
        elif net_margin < 0:
            score -= 10
        
        # Expense ratio scoring
        if expense_ratio < 60:
            score += 10
        elif expense_ratio > 90:
            score -= 10
        
        return max(0, min(100, score))
    
    def _get_health_status(self, score: int) -> str:
        """Get health status based on score."""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_insights(self, financial_data: Dict, gross_margin: float, net_margin: float) -> List[str]:
        """Generate actionable insights."""
        insights = []
        
        revenue = financial_data.get("total_revenue", 0)
        net_income = financial_data.get("net_income", 0)
        
        # Revenue insights
        if revenue > 0:
            insights.append(f"YTD Revenue: ${revenue:,.2f}")
        else:
            insights.append("⚠️ No revenue recorded for this period")
        
        # Profitability insights
        if net_income > 0:
            insights.append(f"✅ Profitable: ${net_income:,.2f} net income")
        else:
            insights.append(f"❌ Operating at loss: ${net_income:,.2f}")
        
        # Margin insights
        if gross_margin > 70:
            insights.append("✅ Excellent gross margins")
        elif gross_margin < 30:
            insights.append("⚠️ Low gross margins - review pricing or costs")
        
        if net_margin < 0:
            insights.append("🔍 Review operating expenses to improve profitability")
        
        return insights
    
    def analyze_trends(self, months: int = 3) -> Dict[str, Any]:
        """Analyze financial trends over multiple periods."""
        
        print(f"\n📊 Analyzing {months}-month financial trends...")
        
        try:
            # This would require multiple API calls for different periods
            # For now, we'll show the structure
            
            # Get current period
            current_data = self.get_financial_summary()
            
            if "error" in current_data:
                return current_data
            
            # In a real implementation, you'd make multiple calls for different periods
            # and compare the results
            
            trend_analysis = {
                "current_period": current_data,
                "trend_indicators": {
                    "revenue_trend": "Need historical data for comparison",
                    "margin_trend": "Need historical data for comparison",
                    "expense_trend": "Need historical data for comparison"
                },
                "recommendations": [
                    "Set up regular monthly financial reviews",
                    "Track key metrics over time",
                    "Compare performance to industry benchmarks"
                ]
            }
            
            return trend_analysis
            
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}

def main():
    """Demonstrate the financial agent."""
    
    print("🎯 FINANCIAL AGENT DEMO")
    print("=" * 50)
    print("This agent analyzes your Xero financial data")
    print()
    
    # Check if Xero is set up
    try:
        from core.integrations.xero.setup import test_xero_connection
        if not test_xero_connection():
            print("❌ Xero connection failed. Run setup first:")
            print("   python -m core.integrations.xero.setup")
            return
    except Exception as e:
        print(f"❌ Setup check failed: {e}")
        print("Run: python -m core.integrations.xero.setup")
        return
    
    # Initialize agent
    agent = SimpleFinancialAgent()
    
    # Get financial summary
    print("\n" + "="*50)
    summary = agent.get_financial_summary()
    
    if "error" in summary:
        print(f"❌ {summary['error']}")
        return
    
    # Display results
    print("📊 FINANCIAL SUMMARY")
    print("=" * 50)
    print(f"Report: {summary['report_name']}")
    print(f"Period: {summary['report_period']}")
    print()
    
    metrics = summary['financial_metrics']
    print("💰 KEY METRICS:")
    print(f"  Revenue:      ${metrics['revenue']:>12,.2f}")
    print(f"  Gross Profit: ${metrics['gross_profit']:>12,.2f}")
    print(f"  Net Income:   ${metrics['net_income']:>12,.2f}")
    print(f"  Expenses:     ${metrics['total_expenses']:>12,.2f}")
    print()
    
    ratios = summary['performance_ratios']
    print("📈 PERFORMANCE RATIOS:")
    print(f"  Gross Margin:  {ratios['gross_margin_percent']:>8.1f}%")
    print(f"  Net Margin:    {ratios['net_margin_percent']:>8.1f}%")
    print(f"  Expense Ratio: {ratios['expense_ratio_percent']:>8.1f}%")
    print()
    
    health = summary['health_assessment']
    print("🏥 FINANCIAL HEALTH:")
    print(f"  Score: {health['score']}/100 ({health['status']})")
    print("  Insights:")
    for insight in health['insights']:
        print(f"    • {insight}")
    
    print("\n" + "="*50)
    print("✅ Financial analysis complete!")
    print("💡 Pro tip: Run this regularly to track your financial progress")

if __name__ == "__main__":
    main()