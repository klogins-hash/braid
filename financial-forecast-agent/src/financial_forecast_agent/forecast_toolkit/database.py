"""Mock SQL Database for Financial Forecasting Agent"""
import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path


class ForecastDatabase:
    """Mock SQL database for storing client information and historical financial data"""
    
    def __init__(self, db_path: str = "forecast_data.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        self._create_tables()
        self._populate_mock_data()
    
    def _create_tables(self):
        """Create the required database tables"""
        cursor = self.connection.cursor()
        
        # Clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                user_id TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                business_age INTEGER NOT NULL,
                location TEXT NOT NULL,
                strategy TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Historical financial data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                revenue REAL NOT NULL,
                cost_of_goods_sold REAL DEFAULT 0,
                gross_profit REAL NOT NULL,
                operating_expenses REAL NOT NULL,
                ebitda REAL NOT NULL,
                depreciation REAL DEFAULT 0,
                ebit REAL NOT NULL,
                interest_expense REAL DEFAULT 0,
                tax_expense REAL DEFAULT 0,
                net_income REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES clients (user_id)
            )
        """)
        
        # Forecasts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                forecast_id TEXT NOT NULL,
                forecast_year INTEGER NOT NULL,
                assumptions TEXT NOT NULL,
                revenue REAL NOT NULL,
                cost_of_goods_sold REAL DEFAULT 0,
                gross_profit REAL NOT NULL,
                operating_expenses REAL NOT NULL,
                ebitda REAL NOT NULL,
                depreciation REAL DEFAULT 0,
                ebit REAL NOT NULL,
                interest_expense REAL DEFAULT 0,
                tax_expense REAL DEFAULT 0,
                net_income REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES clients (user_id)
            )
        """)
        
        self.connection.commit()
    
    def _populate_mock_data(self):
        """Populate database with mock data for testing"""
        cursor = self.connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone()[0] > 0:
            return
        
        # Mock client data
        mock_clients = [
            {
                "user_id": "user_123",
                "business_name": "TechStart Solutions",
                "industry": "Software Development",
                "business_age": 3,
                "location": "San Francisco, CA",
                "strategy": "Aggressive growth through B2B SaaS expansion, focusing on mid-market clients"
            },
            {
                "user_id": "user_456", 
                "business_name": "Northeast Logistics Co",
                "industry": "Last Mile Logistics",
                "business_age": 7,
                "location": "Boston, MA",
                "strategy": "Market consolidation through strategic acquisitions and technology modernization"
            }
        ]
        
        for client in mock_clients:
            cursor.execute("""
                INSERT INTO clients (user_id, business_name, industry, business_age, location, strategy)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (client["user_id"], client["business_name"], client["industry"], 
                  client["business_age"], client["location"], client["strategy"]))
        
        # Mock historical data for TechStart Solutions (3 years)
        historical_data = [
            {
                "user_id": "user_123",
                "period_start": "2022-01-01",
                "period_end": "2022-12-31", 
                "revenue": 750000,
                "cost_of_goods_sold": 225000,
                "gross_profit": 525000,
                "operating_expenses": 450000,
                "ebitda": 75000,
                "depreciation": 15000,
                "ebit": 60000,
                "interest_expense": 5000,
                "tax_expense": 13750,
                "net_income": 41250
            },
            {
                "user_id": "user_123",
                "period_start": "2023-01-01",
                "period_end": "2023-12-31",
                "revenue": 1200000,
                "cost_of_goods_sold": 360000,
                "gross_profit": 840000,
                "operating_expenses": 720000,
                "ebitda": 120000,
                "depreciation": 25000,
                "ebit": 95000,
                "interest_expense": 8000,
                "tax_expense": 21750,
                "net_income": 65250
            },
            {
                "user_id": "user_123",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "revenue": 1800000,
                "cost_of_goods_sold": 540000,
                "gross_profit": 1260000,
                "operating_expenses": 1080000,
                "ebitda": 180000,
                "depreciation": 35000,
                "ebit": 145000,
                "interest_expense": 12000,
                "tax_expense": 33250,
                "net_income": 99750
            }
        ]
        
        # Historical data for Northeast Logistics (3 years)
        logistics_data = [
            {
                "user_id": "user_456",
                "period_start": "2022-01-01",
                "period_end": "2022-12-31",
                "revenue": 3200000,
                "cost_of_goods_sold": 2240000,
                "gross_profit": 960000,
                "operating_expenses": 800000,
                "ebitda": 160000,
                "depreciation": 80000,
                "ebit": 80000,
                "interest_expense": 15000,
                "tax_expense": 16250,
                "net_income": 48750
            },
            {
                "user_id": "user_456",
                "period_start": "2023-01-01",
                "period_end": "2023-12-31",
                "revenue": 3520000,
                "cost_of_goods_sold": 2464000,
                "gross_profit": 1056000,
                "operating_expenses": 880000,
                "ebitda": 176000,
                "depreciation": 85000,
                "ebit": 91000,
                "interest_expense": 18000,
                "tax_expense": 18250,
                "net_income": 54750
            },
            {
                "user_id": "user_456",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "revenue": 3840000,
                "cost_of_goods_sold": 2688000,
                "gross_profit": 1152000,
                "operating_expenses": 960000,
                "ebitda": 192000,
                "depreciation": 90000,
                "ebit": 102000,
                "interest_expense": 20000,
                "tax_expense": 20500,
                "net_income": 61500
            }
        ]
        
        all_historical = historical_data + logistics_data
        
        for data in all_historical:
            cursor.execute("""
                INSERT INTO historical_data 
                (user_id, period_start, period_end, revenue, cost_of_goods_sold, 
                 gross_profit, operating_expenses, ebitda, depreciation, ebit, 
                 interest_expense, tax_expense, net_income)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["user_id"], data["period_start"], data["period_end"],
                data["revenue"], data["cost_of_goods_sold"], data["gross_profit"],
                data["operating_expenses"], data["ebitda"], data["depreciation"],
                data["ebit"], data["interest_expense"], data["tax_expense"], 
                data["net_income"]
            ))
        
        self.connection.commit()
    
    def get_client_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client information by user ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM clients WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_historical_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical financial data for a user"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM historical_data 
            WHERE user_id = ? 
            ORDER BY period_start
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def store_xero_data(self, user_id: str, xero_data: Dict[str, Any]) -> bool:
        """Store Xero data as historical records"""
        try:
            cursor = self.connection.cursor()
            
            # This would process actual Xero data structure
            # For now, we'll simulate storing P&L data
            for period_data in xero_data.get("profit_loss_data", []):
                cursor.execute("""
                    INSERT OR REPLACE INTO historical_data 
                    (user_id, period_start, period_end, revenue, cost_of_goods_sold,
                     gross_profit, operating_expenses, ebitda, depreciation, ebit,
                     interest_expense, tax_expense, net_income)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, period_data["period_start"], period_data["period_end"],
                    period_data["revenue"], period_data.get("cogs", 0),
                    period_data["gross_profit"], period_data["operating_expenses"],
                    period_data["ebitda"], period_data.get("depreciation", 0),
                    period_data["ebit"], period_data.get("interest", 0),
                    period_data.get("tax", 0), period_data["net_income"]
                ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error storing Xero data: {e}")
            return False
    
    def store_forecast(self, user_id: str, forecast_id: str, forecast_data: Dict[str, Any]) -> bool:
        """Store forecast results"""
        try:
            cursor = self.connection.cursor()
            
            for year_data in forecast_data["yearly_forecasts"]:
                cursor.execute("""
                    INSERT INTO forecasts 
                    (user_id, forecast_id, forecast_year, assumptions, revenue,
                     cost_of_goods_sold, gross_profit, operating_expenses, ebitda,
                     depreciation, ebit, interest_expense, tax_expense, net_income)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, forecast_id, year_data["year"],
                    json.dumps(forecast_data["assumptions"]),
                    year_data["revenue"], year_data.get("cogs", 0),
                    year_data["gross_profit"], year_data["operating_expenses"],
                    year_data["ebitda"], year_data.get("depreciation", 0),
                    year_data["ebit"], year_data.get("interest", 0),
                    year_data.get("tax", 0), year_data["net_income"]
                ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error storing forecast: {e}")
            return False
    
    def get_latest_forecast(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get the most recent forecast for a user"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM forecasts 
            WHERE user_id = ? 
            ORDER BY created_at DESC, forecast_year ASC
            LIMIT 5
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()