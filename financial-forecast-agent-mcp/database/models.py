"""
SQLAlchemy ORM models for financial forecasting database.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class Client(Base):
    """Client information and business context."""
    __tablename__ = 'clients'
    
    user_id = Column(String(50), primary_key=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    business_age = Column(Integer)
    location = Column(String(100))
    business_strategy = Column(Text)
    employees = Column(Integer)
    current_revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    historical_financials = relationship("HistoricalFinancial", back_populates="client")
    forecast_assumptions = relationship("ForecastAssumption", back_populates="client")
    forecast_results = relationship("ForecastResult", back_populates="client")
    notion_reports = relationship("NotionReport", back_populates="client")
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'business_age': self.business_age,
            'location': self.location,
            'business_strategy': self.business_strategy,
            'employees': self.employees,
            'current_revenue': self.current_revenue
        }

class HistoricalFinancial(Base):
    """Historical financial data from Xero MCP."""
    __tablename__ = 'historical_financials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('clients.user_id'), nullable=False)
    data_source = Column(String(50), default='xero_mcp')
    report_type = Column(String(50), nullable=False)
    period_start = Column(Date)
    period_end = Column(Date)
    
    # P&L line items
    revenue = Column(Float)
    cogs = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    ebitda = Column(Float)
    depreciation = Column(Float)
    ebit = Column(Float)
    interest_expense = Column(Float)
    tax_expense = Column(Float)
    net_income = Column(Float)
    
    # Balance sheet items (basic)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    equity = Column(Float)
    
    # Raw data storage
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="historical_financials")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'data_source': self.data_source,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'revenue': self.revenue,
            'cogs': self.cogs,
            'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'ebitda': self.ebitda,
            'net_income': self.net_income
        }

class ForecastAssumption(Base):
    """Market research and forecast assumptions."""
    __tablename__ = 'forecast_assumptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('clients.user_id'), nullable=False)
    forecast_date = Column(Date, default=datetime.utcnow().date())
    
    # Quantitative assumptions
    revenue_growth_rate = Column(Float)
    cogs_percentage = Column(Float)
    opex_growth_rate = Column(Float)
    tax_rate = Column(Float)
    depreciation_rate = Column(Float)
    
    # Market context
    market_research = Column(Text)
    industry_outlook = Column(Text)
    
    # Qualitative assumptions
    qualitative_assumptions = Column(JSON)
    risk_factors = Column(JSON)
    growth_drivers = Column(JSON)
    
    # Validation status
    validated = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="forecast_assumptions")
    forecast_results = relationship("ForecastResult", back_populates="assumptions")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'revenue_growth_rate': self.revenue_growth_rate,
            'cogs_percentage': self.cogs_percentage,
            'opex_growth_rate': self.opex_growth_rate,
            'tax_rate': self.tax_rate,
            'market_research': self.market_research,
            'qualitative_assumptions': self.qualitative_assumptions,
            'validated': self.validated,
            'approved': self.approved
        }

class ForecastResult(Base):
    """Forecast results with annual projections."""
    __tablename__ = 'forecast_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('clients.user_id'), nullable=False)
    assumptions_id = Column(Integer, ForeignKey('forecast_assumptions.id'), nullable=False)
    forecast_year = Column(Integer, nullable=False)
    
    # P&L projections
    revenue = Column(Float)
    cogs = Column(Float)
    gross_profit = Column(Float)
    operating_expenses = Column(Float)
    ebitda = Column(Float)
    depreciation = Column(Float)
    ebit = Column(Float)
    interest_expense = Column(Float)
    tax_expense = Column(Float)
    net_income = Column(Float)
    
    # Key metrics
    gross_margin = Column(Float)
    ebitda_margin = Column(Float)
    net_margin = Column(Float)
    
    # Validation and approval
    validated = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    validation_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="forecast_results")
    assumptions = relationship("ForecastAssumption", back_populates="forecast_results")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assumptions_id': self.assumptions_id,
            'forecast_year': self.forecast_year,
            'revenue': self.revenue,
            'cogs': self.cogs,
            'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'ebitda': self.ebitda,
            'net_income': self.net_income,
            'gross_margin': self.gross_margin,
            'ebitda_margin': self.ebitda_margin,
            'net_margin': self.net_margin,
            'validated': self.validated,
            'approved': self.approved
        }

class NotionReport(Base):
    """Notion reports generated for forecasts."""
    __tablename__ = 'notion_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('clients.user_id'), nullable=False)
    forecast_assumptions_id = Column(Integer, ForeignKey('forecast_assumptions.id'))
    notion_page_id = Column(String(100))
    notion_page_url = Column(String(500))
    report_title = Column(String(200))
    report_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="notion_reports")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notion_page_id': self.notion_page_id,
            'notion_page_url': self.notion_page_url,
            'report_title': self.report_title,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }