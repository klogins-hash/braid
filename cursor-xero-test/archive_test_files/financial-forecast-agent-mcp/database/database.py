"""
Database connection and operations for financial forecasting agent.
SQLite database with SQLAlchemy ORM.
"""

import os
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
import json

from .models import Base, Client, HistoricalFinancial, ForecastAssumption, ForecastResult, NotionReport

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for financial forecasting."""
    
    def __init__(self, db_path: str = "forecast_data.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            # Create SQLite database
            self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Load schema if tables are empty
            self._load_initial_schema()
            
            logger.info(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _load_initial_schema(self):
        """Load initial schema and sample data."""
        try:
            # Check if we need to load sample data
            with self.get_session() as session:
                client_count = session.query(Client).count()
                
                if client_count == 0:
                    # Load sample clients
                    sample_clients = [
                        Client(
                            user_id="user_123",
                            company_name="Northeast Logistics Co",
                            industry="Software Development",
                            business_age=5,
                            location="San Francisco, CA",
                            business_strategy="Aggressive growth through digital transformation",
                            employees=25,
                            current_revenue=1000000.0
                        ),
                        Client(
                            user_id="demo_company",
                            company_name="Demo Tech Solutions",
                            industry="Technology Services",
                            business_age=3,
                            location="Boston, MA",
                            business_strategy="Market expansion and product development",
                            employees=15,
                            current_revenue=750000.0
                        )
                    ]
                    
                    for client in sample_clients:
                        session.add(client)
                    
                    session.commit()
                    logger.info("✅ Sample client data loaded")
                    
        except Exception as e:
            logger.error(f"❌ Failed to load initial schema: {e}")
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # Client operations
    def get_client(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client information by user ID."""
        try:
            with self.get_session() as session:
                client = session.query(Client).filter(Client.user_id == user_id).first()
                return client.to_dict() if client else None
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting client {user_id}: {e}")
            return None
    
    def create_or_update_client(self, client_data: Dict[str, Any]) -> bool:
        """Create or update client information."""
        try:
            with self.get_session() as session:
                client = session.query(Client).filter(Client.user_id == client_data['user_id']).first()
                
                if client:
                    # Update existing client
                    for key, value in client_data.items():
                        setattr(client, key, value)
                    client.updated_at = datetime.utcnow()
                else:
                    # Create new client
                    client = Client(**client_data)
                    session.add(client)
                
                session.commit()
                logger.info(f"✅ Client {client_data['user_id']} saved")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error saving client: {e}")
            return False
    
    # Historical financial data operations
    def store_historical_data(self, user_id: str, xero_data: Dict[str, Any], report_type: str = "profit_and_loss") -> bool:
        """Store historical financial data from Xero."""
        try:
            with self.get_session() as session:
                # Parse Xero data (simplified for now)
                historical_data = HistoricalFinancial(
                    user_id=user_id,
                    data_source="xero_mcp",
                    report_type=report_type,
                    period_start=date.today().replace(month=1, day=1),  # Current year start
                    period_end=date.today(),
                    revenue=1000000.0,  # Will be parsed from actual Xero data
                    cogs=350000.0,
                    gross_profit=650000.0,
                    operating_expenses=420000.0,
                    ebitda=230000.0,
                    depreciation=50000.0,
                    ebit=180000.0,
                    interest_expense=20000.0,
                    tax_expense=40000.0,
                    net_income=120000.0,
                    raw_data=xero_data
                )
                
                session.add(historical_data)
                session.commit()
                logger.info(f"✅ Historical data stored for {user_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error storing historical data: {e}")
            return False
    
    def get_historical_data(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get historical financial data for a user."""
        try:
            with self.get_session() as session:
                historical_records = (
                    session.query(HistoricalFinancial)
                    .filter(HistoricalFinancial.user_id == user_id)
                    .order_by(HistoricalFinancial.period_end.desc())
                    .limit(limit)
                    .all()
                )
                
                return [record.to_dict() for record in historical_records]
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting historical data: {e}")
            return []
    
    # Forecast assumptions operations
    def store_forecast_assumptions(self, user_id: str, assumptions: Dict[str, Any]) -> Optional[int]:
        """Store forecast assumptions."""
        try:
            with self.get_session() as session:
                assumption_record = ForecastAssumption(
                    user_id=user_id,
                    revenue_growth_rate=assumptions.get('revenue_growth_rate', 0.15),
                    cogs_percentage=assumptions.get('cogs_percentage', 0.35),
                    opex_growth_rate=assumptions.get('opex_growth_rate', 0.08),
                    tax_rate=assumptions.get('tax_rate', 0.25),
                    depreciation_rate=assumptions.get('depreciation_rate', 0.10),
                    market_research=assumptions.get('market_research', ''),
                    industry_outlook=assumptions.get('industry_outlook', ''),
                    qualitative_assumptions=assumptions.get('qualitative_assumptions', {}),
                    risk_factors=assumptions.get('risk_factors', []),
                    growth_drivers=assumptions.get('growth_drivers', [])
                )
                
                session.add(assumption_record)
                session.commit()
                session.refresh(assumption_record)
                
                logger.info(f"✅ Forecast assumptions stored for {user_id}")
                return assumption_record.id
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error storing forecast assumptions: {e}")
            return None
    
    def get_forecast_assumptions(self, user_id: str, assumptions_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get forecast assumptions."""
        try:
            with self.get_session() as session:
                if assumptions_id:
                    assumption = session.query(ForecastAssumption).filter(
                        ForecastAssumption.id == assumptions_id,
                        ForecastAssumption.user_id == user_id
                    ).first()
                else:
                    # Get latest assumptions
                    assumption = (
                        session.query(ForecastAssumption)
                        .filter(ForecastAssumption.user_id == user_id)
                        .order_by(ForecastAssumption.created_at.desc())
                        .first()
                    )
                
                return assumption.to_dict() if assumption else None
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting forecast assumptions: {e}")
            return None
    
    # Forecast results operations
    def store_forecast_results(self, user_id: str, assumptions_id: int, forecast_data: List[Dict[str, Any]]) -> bool:
        """Store forecast results for multiple years."""
        try:
            with self.get_session() as session:
                for year_data in forecast_data:
                    forecast_result = ForecastResult(
                        user_id=user_id,
                        assumptions_id=assumptions_id,
                        forecast_year=year_data['year'],
                        revenue=year_data['revenue'],
                        cogs=year_data['cogs'],
                        gross_profit=year_data['gross_profit'],
                        operating_expenses=year_data['operating_expenses'],
                        ebitda=year_data['ebitda'],
                        depreciation=year_data.get('depreciation', 0),
                        ebit=year_data.get('ebit', 0),
                        interest_expense=year_data.get('interest_expense', 0),
                        tax_expense=year_data.get('tax_expense', 0),
                        net_income=year_data['net_income'],
                        gross_margin=year_data.get('gross_margin', 0),
                        ebitda_margin=year_data.get('ebitda_margin', 0),
                        net_margin=year_data.get('net_margin', 0)
                    )
                    session.add(forecast_result)
                
                session.commit()
                logger.info(f"✅ Forecast results stored for {user_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error storing forecast results: {e}")
            return False
    
    def get_forecast_results(self, user_id: str, assumptions_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get forecast results."""
        try:
            with self.get_session() as session:
                query = session.query(ForecastResult).filter(ForecastResult.user_id == user_id)
                
                if assumptions_id:
                    query = query.filter(ForecastResult.assumptions_id == assumptions_id)
                
                results = query.order_by(ForecastResult.forecast_year).all()
                return [result.to_dict() for result in results]
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting forecast results: {e}")
            return []
    
    def approve_forecast(self, user_id: str, assumptions_id: int) -> bool:
        """Mark forecast assumptions and results as approved."""
        try:
            with self.get_session() as session:
                # Approve assumptions
                assumption = session.query(ForecastAssumption).filter(
                    ForecastAssumption.id == assumptions_id,
                    ForecastAssumption.user_id == user_id
                ).first()
                
                if assumption:
                    assumption.approved = True
                    assumption.validated = True
                
                # Approve results
                results = session.query(ForecastResult).filter(
                    ForecastResult.assumptions_id == assumptions_id,
                    ForecastResult.user_id == user_id
                ).all()
                
                for result in results:
                    result.approved = True
                    result.validated = True
                
                session.commit()
                logger.info(f"✅ Forecast approved for {user_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error approving forecast: {e}")
            return False
    
    def store_notion_report(self, user_id: str, assumptions_id: int, notion_data: Dict[str, Any]) -> bool:
        """Store Notion report information."""
        try:
            with self.get_session() as session:
                report = NotionReport(
                    user_id=user_id,
                    forecast_assumptions_id=assumptions_id,
                    notion_page_id=notion_data.get('page_id'),
                    notion_page_url=notion_data.get('page_url'),
                    report_title=notion_data.get('title'),
                    report_content=notion_data.get('content')
                )
                
                session.add(report)
                session.commit()
                logger.info(f"✅ Notion report stored for {user_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error storing Notion report: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("🛑 Database connection closed")

# Global database manager instance
db_manager = DatabaseManager()