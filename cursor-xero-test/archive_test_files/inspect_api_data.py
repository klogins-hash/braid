#!/usr/bin/env python3
"""
Detailed API Data Inspector - Shows exactly what Xero and Perplexity return
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.xero_tools import XeroTools
from src.tools.perplexity_tools import PerplexityTools
from src.database.database import DatabaseOperations

def print_separator(title: str):
    """Print a visual separator."""
    print(f"\n{'='*80}")
    print(f"📊 {title.upper()}")
    print(f"{'='*80}")

def inspect_xero_data():
    """Inspect Xero API data in detail."""
    print_separator("Xero API Data Inspection")
    
    xero = XeroTools()
    
    print(f"🔧 Xero Configuration:")
    print(f"   Token Present: {bool(xero.access_token)}")
    print(f"   Token Length: {len(xero.access_token) if xero.access_token else 0}")
    print(f"   Token Prefix: {xero.access_token[:20] + '...' if xero.access_token else 'None'}")
    
    print(f"\n🔄 Calling Xero API...")
    
    try:
        data = xero.get_profit_and_loss()
        
        print(f"✅ Xero Response Received:")
        print(f"   Data Type: {type(data)}")
        print(f"   Number of Records: {len(data) if isinstance(data, list) else 'Not a list'}")
        
        if data and isinstance(data, list):
            for i, record in enumerate(data):
                print(f"\n📋 Record {i+1}:")
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key in ['revenue', 'cost_of_goods_sold', 'gross_profit', 'operating_expenses', 'ebitda', 'net_income']:
                            print(f"   {key}: ${value:,.2f}")
                        else:
                            print(f"   {key}: {value}")
                    else:
                        print(f"   {key}: {value}")
        
        print(f"\n📄 Raw JSON Data:")
        print(json.dumps(data, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error calling Xero API: {e}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")

def inspect_perplexity_data():
    """Inspect Perplexity API data in detail."""
    print_separator("Perplexity API Data Inspection")
    
    perplexity = PerplexityTools()
    
    print(f"🔧 Perplexity Configuration:")
    print(f"   API Key Present: {bool(perplexity.api_key)}")
    print(f"   API Key Length: {len(perplexity.api_key) if perplexity.api_key else 0}")
    print(f"   API Key Prefix: {perplexity.api_key[:10] + '...' if perplexity.api_key else 'None'}")
    
    print(f"\n🔄 Calling Perplexity API...")
    
    try:
        # Test with a specific query
        industry = "Technology Services"
        location = "San Francisco, CA"
        
        research = perplexity.conduct_market_research(industry, location)
        
        print(f"✅ Perplexity Response Received:")
        print(f"   Data Type: {type(research)}")
        print(f"   Content Length: {len(research) if research else 0} characters")
        
        if research:
            print(f"\n📋 Market Research Content:")
            print(f"   First 200 characters: {research[:200]}...")
            print(f"   Last 200 characters: ...{research[-200:]}")
            
            # Check for specific sections
            sections = [
                "Market size", "Growth projections", "Industry trends", 
                "Competitive landscape", "Regulatory", "Economic factors",
                "Technology trends", "Risks", "Opportunities"
            ]
            
            print(f"\n📊 Content Analysis:")
            for section in sections:
                if section.lower() in research.lower():
                    print(f"   ✅ Contains '{section}' information")
                else:
                    print(f"   ❌ Missing '{section}' information")
        
        print(f"\n📄 Full Content:")
        print("-" * 80)
        print(research)
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error calling Perplexity API: {e}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")

def inspect_database_data():
    """Inspect database client data."""
    print_separator("Database Client Data Inspection")
    
    try:
        db = DatabaseOperations()
        
        # Test with our sample user
        user_id = "test_user_123"
        client_info = db.get_client_info(user_id)
        
        print(f"🔍 Querying client data for: {user_id}")
        
        if client_info:
            print(f"✅ Client Found:")
            for key, value in client_info.items():
                if key == 'current_revenue' and isinstance(value, (int, float)):
                    print(f"   {key}: ${value:,.2f}")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"❌ No client found for user ID: {user_id}")
        
        print(f"\n📄 Raw Client Data:")
        print(json.dumps(client_info, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")

def test_api_integrations():
    """Test both APIs with direct calls."""
    print_separator("Direct API Integration Tests")
    
    print("🧪 Testing Perplexity with simple query...")
    try:
        perplexity = PerplexityTools()
        simple_research = perplexity.conduct_market_research("Technology", "San Francisco")
        print(f"✅ Simple query returned {len(simple_research)} characters")
    except Exception as e:
        print(f"❌ Simple Perplexity test failed: {e}")
    
    print("\n🧪 Testing Xero with date range...")
    try:
        xero = XeroTools()
        date_data = xero.get_profit_and_loss("2023-01-01", "2023-12-31")
        print(f"✅ Date range query returned {len(date_data)} records")
    except Exception as e:
        print(f"❌ Date range Xero test failed: {e}")

def main():
    """Main inspection function."""
    print("🔍 API DATA INSPECTION TOOL")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Inspect each component
    inspect_xero_data()
    inspect_perplexity_data()
    inspect_database_data()
    test_api_integrations()
    
    print_separator("Inspection Complete")
    print("✅ All data sources have been inspected")
    print("📊 Review the output above to verify data quality and format")

if __name__ == "__main__":
    main()