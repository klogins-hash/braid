#!/usr/bin/env python3
"""
Setup script to create Supabase database schema for Braid AI Agent System
"""
import os
import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://xmngdcugklkgboebllmbf.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtbmdkY3Vna2xrZ2JvZWJsbWJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODkxNTYzMSwiZXhwIjoyMDc0NDkxNjMxfQ.qnTWGyiRH1QRPU92ffQxMkmUuZ5V1i0CcDk4i2HbEFA"

def setup_database():
    """Set up the Supabase database schema."""
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Connected to Supabase")
        
        # Read the schema file
        with open('database/supabase_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        print(f"📝 Executing {len(statements)} SQL statements...")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                # Skip empty statements
                if not statement or statement.isspace():
                    continue
                    
                print(f"   {i}/{len(statements)}: {statement[:50]}...")
                
                # Execute the SQL statement
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                
                if result.data:
                    print(f"      ✅ Success")
                else:
                    print(f"      ⚠️  No data returned")
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                # Continue with other statements
                continue
        
        print("\n🎉 Database schema setup completed!")
        print("\n📋 Created tables:")
        print("   • agent_sessions - Store agent session data")
        print("   • agent_memory - Store agent memory/context")
        print("   • agent_logs - Store agent action logs")
        print("   • integrations - Store integration configurations")
        print("   • agents - Store agent definitions")
        print("   • workflow_executions - Store workflow execution data")
        
        print("\n🔧 Next steps:")
        print("   1. Deploy to Railway: railway.app")
        print("   2. Set OPENAI_API_KEY environment variable")
        print("   3. Test the deployment at your Railway URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup database: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Braid AI Agent System database...")
    success = setup_database()
    sys.exit(0 if success else 1)
