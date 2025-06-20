from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Optional, List, Dict, Any
import os
import json
from datetime import datetime

from .models import Base, Client, HistoricalFinancials, ForecastAssumptions, ForecastResults

# Create database engine
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./financial_forecast.db')
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseOperations:
    """Database operations for the financial forecasting system."""
    
    def __init__(self):
        self.session = SessionLocal()
        
    def __del__(self):
        """Close database session on cleanup."""
        if hasattr(self, 'session'):
            self.session.close()
    
    @property 
    def db(self):
        """Get database session for backward compatibility."""
        return self.session
    
    def get_client_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client information from database."""
        client = self.db.query(Client).filter(Client.user_id == user_id).first()
        if not client:
            return None
        return {
            'user_id': client.user_id,
            'company_name': client.company_name,
            'industry': client.industry,
            'business_age': client.business_age,
            'location': client.location,
            'business_strategy': client.business_strategy,
            'employees': client.employees,
            'current_revenue': client.current_revenue
        }
    
    def store_historical_financials(self, user_id: str, financials_data: List[Dict[str, Any]]):
        """Store historical financial data from Xero."""
        try:
            for data in financials_data:
                financial = HistoricalFinancials(
                    user_id=user_id,
                    period_start=datetime.strptime(data['period_start'], '%Y-%m-%d'),
                    period_end=datetime.strptime(data['period_end'], '%Y-%m-%d'),
                    revenue=data.get('revenue'),
                    cost_of_goods_sold=data.get('cost_of_goods_sold'),
                    gross_profit=data.get('gross_profit'),
                    operating_expenses=data.get('operating_expenses'),
                    ebitda=data.get('ebitda'),
                    net_income=data.get('net_income'),
                    data_source=data.get('data_source')
                )
                self.db.add(financial)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def store_forecast_assumptions(self, user_id: str, assumptions: Dict[str, Any]) -> int:
        """Store forecast assumptions and return the ID."""
        forecast_assumptions = ForecastAssumptions(
            user_id=user_id,
            revenue_growth_rate=float(assumptions['revenue_growth_rate'].strip('%')) / 100,
            cost_of_goods_sold_rate=float(assumptions['cost_of_goods_sold'].strip('%')) / 100,
            operating_expense_growth=float(assumptions['operating_expense_growth'].strip('%')) / 100,
            tax_rate=float(assumptions['tax_rate'].strip('%')) / 100,
            depreciation_rate=float(assumptions['depreciation_rate'].strip('%')) / 100,
            market_factors=assumptions['market_factors'],
            risk_factors=assumptions['risk_factors'],
            growth_drivers=assumptions['growth_drivers']
        )
        self.db.add(forecast_assumptions)
        self.db.commit()
        return forecast_assumptions.id
    
    def store_forecast_results(self, user_id: str, assumptions_id: int, results: Dict[str, Dict[str, float]]):
        """Store forecast results."""
        for year, data in results.items():
            year_num = int(year.split('_')[1])
            forecast = ForecastResults(
                user_id=user_id,
                forecast_year=year_num,
                revenue=data['revenue'],
                cost_of_goods_sold=data.get('expenses'),  # Map to appropriate field
                gross_profit=data['revenue'] - data.get('expenses', 0),
                operating_expenses=data.get('expenses'),
                ebitda=data['revenue'] - data.get('expenses', 0),  # Simplified
                net_income=data['net_income'],
                assumptions_id=assumptions_id
            )
            self.db.add(forecast)
        self.db.commit()
    
    def get_historical_financials(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical financial data for a user."""
        financials = self.db.query(HistoricalFinancials)\
            .filter(HistoricalFinancials.user_id == user_id)\
            .all()
        return [
            {
                'period_start': financial.period_start.strftime('%Y-%m-%d'),
                'period_end': financial.period_end.strftime('%Y-%m-%d'),
                'revenue': financial.revenue,
                'cost_of_goods_sold': financial.cost_of_goods_sold,
                'gross_profit': financial.gross_profit,
                'operating_expenses': financial.operating_expenses,
                'ebitda': financial.ebitda,
                'net_income': financial.net_income,
                'data_source': financial.data_source
            }
            for financial in financials
        ] 