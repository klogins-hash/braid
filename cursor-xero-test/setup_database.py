#!/usr/bin/env python3
"""
Database setup script - creates tables and populates with dummy client data.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import init_db, DatabaseOperations, engine
from src.database.models import Client, Base

def create_tables():
    """Create all database tables."""
    print("🗄️ Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    return True

def create_dummy_clients():
    """Create dummy client data for testing."""
    print("👥 Creating dummy client data...")
    
    db_ops = DatabaseOperations()
    
    # Sample client data
    clients_data = [
        {
            "user_id": "test_user_123",
            "company_name": "TechFlow Solutions",
            "industry": "Technology Services", 
            "business_age": "3 years",
            "location": "San Francisco, CA",
            "business_strategy": "SaaS platform for workflow automation",
            "employees": 25,
            "current_revenue": 2500000.0
        },
        {
            "user_id": "demo_user_456",
            "company_name": "GreenBuild Construction",
            "industry": "Construction",
            "business_age": "8 years", 
            "location": "Austin, TX",
            "business_strategy": "Sustainable construction and renovation",
            "employees": 45,
            "current_revenue": 5200000.0
        },
        {
            "user_id": "sample_user_789",
            "company_name": "DataInsight Analytics", 
            "industry": "Data Analytics",
            "business_age": "2 years",
            "location": "New York, NY", 
            "business_strategy": "AI-powered business intelligence platform",
            "employees": 15,
            "current_revenue": 1800000.0
        }
    ]
    
    try:
        for client_data in clients_data:
            # Check if client already exists
            existing = db_ops.db.query(Client).filter(Client.user_id == client_data["user_id"]).first()
            if existing:
                print(f"⚠️ Client {client_data['user_id']} already exists, skipping...")
                continue
                
            # Create new client
            client = Client(
                user_id=client_data["user_id"],
                company_name=client_data["company_name"],
                industry=client_data["industry"],
                business_age=client_data["business_age"],
                location=client_data["location"],
                business_strategy=client_data["business_strategy"],
                employees=client_data["employees"],
                current_revenue=client_data["current_revenue"]
            )
            
            db_ops.db.add(client)
            print(f"✅ Added client: {client_data['company_name']} ({client_data['user_id']})")
        
        db_ops.db.commit()
        print("✅ All dummy clients created successfully")
        
    except Exception as e:
        print(f"❌ Error creating dummy clients: {e}")
        db_ops.db.rollback()
        return False
    
    return True

def verify_setup():
    """Verify the database setup."""
    print("🔍 Verifying database setup...")
    
    try:
        db_ops = DatabaseOperations()
        
        # Test client lookup
        test_client = db_ops.get_client_info("test_user_123")
        if test_client:
            print(f"✅ Test client found: {test_client['company_name']}")
            print(f"   Industry: {test_client['industry']}")
            print(f"   Location: {test_client['location']}")
            print(f"   Employees: {test_client['employees']}")
            print(f"   Revenue: ${test_client['current_revenue']:,.2f}")
        else:
            print("❌ Test client not found")
            return False
            
        # List all clients
        all_clients = db_ops.db.query(Client).all()
        print(f"📊 Total clients in database: {len(all_clients)}")
        for client in all_clients:
            print(f"   - {client.company_name} ({client.user_id})")
            
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Financial Forecast Database")
    print("=" * 50)
    
    # Step 1: Create tables
    if not create_tables():
        print("❌ Database setup failed at table creation")
        return 1
    
    # Step 2: Create dummy clients
    if not create_dummy_clients():
        print("❌ Database setup failed at client creation")
        return 1
    
    # Step 3: Verify setup
    if not verify_setup():
        print("❌ Database setup failed at verification")
        return 1
    
    print("\n🎉 Database setup completed successfully!")
    print("=" * 50)
    print("You can now run the agent with:")
    print("  python test_full_agent.py")
    print("  python -c \"from src.agent import FinancialForecastAgent; agent = FinancialForecastAgent(); result = agent.run_forecast('test_user_123')\"")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)