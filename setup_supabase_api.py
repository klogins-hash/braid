#!/usr/bin/env python3
"""
Setup script using Supabase REST API to create database schema
"""
import requests
import json
import sys

# Supabase configuration
SUPABASE_URL = "https://xmngdcugklkgboeblmbf.supabase.co"
SUPABASE_ACCESS_TOKEN = "sbp_cff450b5ef378df52bcbe951af3b793107cf38d7"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtbmdkY3Vna2xrZ2JvZWJsbWJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODkxNTYzMSwiZXhwIjoyMDc0NDkxNjMxfQ.qnTWGyiRH1QRPU92ffQxMkmUuZ5V1i0CcDk4i2HbEFA"

def execute_sql(sql_statement):
    """Execute SQL using Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    payload = {
        "sql": sql_statement
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def setup_database():
    """Set up the database schema using direct SQL execution."""
    print("🚀 Setting up Braid AI Agent System database via REST API...")
    
    # SQL statements to execute
    sql_statements = [
        # Enable extensions
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
        
        # Create tables
        '''CREATE TABLE IF NOT EXISTS agent_sessions (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            session_data JSONB NOT NULL DEFAULT '{}',
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE
        );''',
        
        '''CREATE TABLE IF NOT EXISTS agent_memory (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            memory_type VARCHAR(100) NOT NULL,
            content JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );''',
        
        '''CREATE TABLE IF NOT EXISTS agent_logs (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            action VARCHAR(255) NOT NULL,
            details JSONB NOT NULL DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            level VARCHAR(20) DEFAULT 'info'
        );''',
        
        '''CREATE TABLE IF NOT EXISTS integrations (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            config JSONB NOT NULL DEFAULT '{}',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );''',
        
        '''CREATE TABLE IF NOT EXISTS agents (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            config JSONB NOT NULL DEFAULT '{}',
            tools JSONB NOT NULL DEFAULT '[]',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );''',
        
        '''CREATE TABLE IF NOT EXISTS workflow_executions (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            workflow_name VARCHAR(255) NOT NULL,
            input_data JSONB NOT NULL DEFAULT '{}',
            output_data JSONB,
            status VARCHAR(50) DEFAULT 'running',
            error_message TEXT,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE
        );''',
        
        # Create indexes
        'CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON agent_sessions(agent_id);',
        'CREATE INDEX IF NOT EXISTS idx_agent_sessions_status ON agent_sessions(status);',
        'CREATE INDEX IF NOT EXISTS idx_agent_memory_agent_id ON agent_memory(agent_id);',
        'CREATE INDEX IF NOT EXISTS idx_agent_memory_type ON agent_memory(memory_type);',
        'CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_id ON agent_logs(agent_id);',
        'CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);',
        'CREATE INDEX IF NOT EXISTS idx_workflow_executions_agent_id ON workflow_executions(agent_id);',
        'CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);',
    ]
    
    success_count = 0
    total_statements = len(sql_statements)
    
    print(f"📝 Executing {total_statements} SQL statements...")
    
    for i, statement in enumerate(sql_statements, 1):
        print(f"   {i}/{total_statements}: {statement[:60]}...")
        success, result = execute_sql(statement)
        
        if success:
            print(f"      ✅ Success")
            success_count += 1
        else:
            print(f"      ❌ Error: {result}")
    
    # Insert default integrations
    print("\n📦 Inserting default integrations...")
    integrations_sql = '''
    INSERT INTO integrations (name, config) VALUES 
    ('openai', '{"api_key_env": "OPENAI_API_KEY", "model": "gpt-4"}'),
    ('anthropic', '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-3-sonnet-20240229"}'),
    ('google_workspace', '{"credentials_env": "GOOGLE_APPLICATION_CREDENTIALS_JSON"}'),
    ('slack', '{"bot_token_env": "SLACK_BOT_TOKEN"}'),
    ('notion', '{"token_env": "NOTION_TOKEN"}'),
    ('perplexity', '{"api_key_env": "PERPLEXITY_API_KEY"}')
    ON CONFLICT (name) DO NOTHING;
    '''
    
    success, result = execute_sql(integrations_sql)
    if success:
        print("      ✅ Default integrations added")
    else:
        print(f"      ⚠️  Integrations warning: {result}")
    
    print(f"\n🎉 Database setup completed! ({success_count}/{total_statements} statements successful)")
    
    if success_count == total_statements:
        print("\n📋 Successfully created:")
        print("   • agent_sessions - Store agent session data")
        print("   • agent_memory - Store agent memory/context") 
        print("   • agent_logs - Store agent action logs")
        print("   • integrations - Store integration configurations")
        print("   • agents - Store agent definitions")
        print("   • workflow_executions - Store workflow execution data")
        print("   • All indexes and default integrations")
        
        print("\n🚀 Ready for Railway deployment!")
        print("   1. Go to railway.app")
        print("   2. Deploy from your GitHub repo")
        print("   3. Add OPENAI_API_KEY environment variable")
        print("   4. Test at your Railway URL/health")
        
        return True
    else:
        print(f"\n⚠️  Some statements failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
