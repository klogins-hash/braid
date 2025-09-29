-- Braid AI Agent System - Supabase Database Schema

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Agent Sessions Table
CREATE TABLE agent_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    session_data JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Agent Memory/State Table
CREATE TABLE agent_memory (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    memory_type VARCHAR(100) NOT NULL, -- 'conversation', 'context', 'tools', etc.
    content JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Action Logs Table
CREATE TABLE agent_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) DEFAULT 'info' -- 'debug', 'info', 'warning', 'error'
);

-- Integration Configurations Table
CREATE TABLE integrations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Definitions Table
CREATE TABLE agents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB NOT NULL DEFAULT '{}',
    tools JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow Executions Table
CREATE TABLE workflow_executions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_agent_sessions_agent_id ON agent_sessions(agent_id);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);
CREATE INDEX idx_agent_memory_agent_id ON agent_memory(agent_id);
CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX idx_agent_logs_timestamp ON agent_logs(timestamp);
CREATE INDEX idx_workflow_executions_agent_id ON workflow_executions(agent_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_agent_sessions_updated_at BEFORE UPDATE ON agent_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_memory_updated_at BEFORE UPDATE ON agent_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_executions ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (adjust based on your authentication needs)
CREATE POLICY "Allow all operations for service role" ON agent_sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON agent_memory FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON agent_logs FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON integrations FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON agents FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON workflow_executions FOR ALL USING (true);

-- Insert some default integrations
INSERT INTO integrations (name, config) VALUES 
('openai', '{"api_key_env": "OPENAI_API_KEY", "model": "gpt-4"}'),
('anthropic', '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-3-sonnet-20240229"}'),
('google_workspace', '{"credentials_env": "GOOGLE_APPLICATION_CREDENTIALS_JSON"}'),
('slack', '{"bot_token_env": "SLACK_BOT_TOKEN"}'),
('notion', '{"token_env": "NOTION_TOKEN"}'),
('perplexity', '{"api_key_env": "PERPLEXITY_API_KEY"}')
