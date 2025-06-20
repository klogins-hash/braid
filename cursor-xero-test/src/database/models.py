from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    business_age = Column(String)
    location = Column(String)
    business_strategy = Column(String)
    employees = Column(Integer)
    current_revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HistoricalFinancials(Base):
    __tablename__ = 'historical_financials'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    revenue = Column(Float)
    cost_of_goods_sold = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    data_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastAssumptions(Base):
    __tablename__ = 'forecast_assumptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    revenue_growth_rate = Column(Float)
    cost_of_goods_sold_rate = Column(Float)
    operating_expense_growth = Column(Float)
    tax_rate = Column(Float)
    depreciation_rate = Column(Float)
    market_factors = Column(String)
    risk_factors = Column(String)
    growth_drivers = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ForecastResults(Base):
    __tablename__ = 'forecast_results'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    forecast_year = Column(Integer, nullable=False)
    revenue = Column(Float)
    cost_of_goods_sold = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    assumptions_id = Column(Integer, nullable=False) 