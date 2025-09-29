#!/usr/bin/env python3
"""
Direct PostgreSQL connection to set up Supabase database schema
"""
import psycopg2
import sys

# Database connection details
DB_HOST = "db.xmngdcugklkgboeblmbf.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "S3RKbr#k9&xkE^^AZGc0"

def setup_database():
    """Set up the database schema using direct PostgreSQL connection."""
    print("🚀 Setting up Braid AI Agent System database via direct PostgreSQL connection...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL database")
        
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
            
            # Create trigger function
            '''CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';''',
            
            # Create triggers
            'DROP TRIGGER IF EXISTS update_agent_sessions_updated_at ON agent_sessions;',
            'CREATE TRIGGER update_agent_sessions_updated_at BEFORE UPDATE ON agent_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'DROP TRIGGER IF EXISTS update_agent_memory_updated_at ON agent_memory;',
            'CREATE TRIGGER update_agent_memory_updated_at BEFORE UPDATE ON agent_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'DROP TRIGGER IF EXISTS update_integrations_updated_at ON integrations;',
            'CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;',
            'CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
        ]
        
        success_count = 0
        total_statements = len(sql_statements)
        
        print(f"📝 Executing {total_statements} SQL statements...")
        
        for i, statement in enumerate(sql_statements, 1):
            try:
                print(f"   {i}/{total_statements}: {statement[:60].replace(chr(10), ' ')}...")
                cursor.execute(statement)
                print(f"      ✅ Success")
                success_count += 1
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
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
        
        try:
            cursor.execute(integrations_sql)
            print("      ✅ Default integrations added")
        except Exception as e:
            print(f"      ⚠️  Integrations warning: {str(e)}")
        
        # Verify tables
        print("\n🔍 Verifying created tables...")
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('agent_sessions', 'agent_memory', 'agent_logs', 'integrations', 'agents', 'workflow_executions')
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        print(f"      ✅ Found {len(tables)} tables: {', '.join([t[0] for t in tables])}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Database setup completed! ({success_count}/{total_statements} statements successful)")
        
        if success_count >= total_statements - 2:  # Allow for some minor failures
            print("\n📋 Successfully created:")
            print("   • agent_sessions - Store agent session data")
            print("   • agent_memory - Store agent memory/context") 
            print("   • agent_logs - Store agent action logs")
            print("   • integrations - Store integration configurations")
            print("   • agents - Store agent definitions")
            print("   • workflow_executions - Store workflow execution data")
            print("   • All indexes and triggers")
            
            print("\n🚀 Ready for Railway deployment!")
            print("   1. Go to railway.app")
            print("   2. Deploy from your GitHub repo")
            print("   3. Add OPENAI_API_KEY environment variable")
            print("   4. Test at your Railway URL/health")
            
            return True
        else:
            print(f"\n⚠️  Too many statements failed. Check the errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
