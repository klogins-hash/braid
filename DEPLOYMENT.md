# Braid AI Agent System - Railway + Supabase Deployment Guide

## Overview

This guide covers deploying Braid AI Agent System on Railway with Supabase as the backend database.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
3. **GitHub Repository**: Fork of braid-ink/braid
4. **API Keys**: OpenAI, Anthropic, and integration APIs

## Step 1: Set Up Supabase

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Choose a database password and region
3. Wait for the project to be ready

### 1.2 Set Up Database Schema
1. Go to SQL Editor in your Supabase dashboard
2. Copy and paste the contents of `database/supabase_schema.sql`
3. Run the SQL to create all necessary tables and indexes

### 1.3 Get Supabase Credentials
From your Supabase project settings, note down:
- `SUPABASE_URL`: Your project URL
- `SUPABASE_ANON_KEY`: Anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key (keep secret!)

## Step 2: Deploy to Railway

### 2.1 Connect Repository
1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repository (the forked braid repo)
3. Railway will automatically detect the `railway.toml` configuration

### 2.2 Set Environment Variables
In Railway dashboard, go to Variables and set:

**Required Variables:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

**Optional Integration Variables:**
```
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
SLACK_BOT_TOKEN=xoxb-your-slack-token
NOTION_TOKEN=secret_your-notion-token
PERPLEXITY_API_KEY=pplx-your-perplexity-key
```

### 2.3 Deploy
1. Railway will automatically build and deploy using the Dockerfile
2. Monitor the deployment logs for any issues
3. Once deployed, you'll get a Railway URL like `https://your-app.railway.app`

## Step 3: Verify Deployment

### 3.1 Health Check
Visit `https://your-app.railway.app/health` to verify the service is running and connected to Supabase.

### 3.2 API Documentation
Visit `https://your-app.railway.app/docs` to see the interactive API documentation.

### 3.3 Test Agent Creation
```bash
curl -X POST "https://your-app.railway.app/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "research",
    "config": {"model": "gpt-4"},
    "tools": ["web_search", "notion"]
  }'
```

## Step 4: Integration Setup

### 4.1 Google Workspace
1. Create a Google Cloud Project
2. Enable necessary APIs (Gmail, Calendar, Drive, Sheets)
3. Create a service account and download JSON credentials
4. Set `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable

### 4.2 Slack
1. Create a Slack app at [api.slack.com](https://api.slack.com)
2. Add necessary scopes (chat:write, files:write, etc.)
3. Install app to workspace and get bot token
4. Set `SLACK_BOT_TOKEN` environment variable

### 4.3 Notion
1. Create a Notion integration at [notion.so/my-integrations](https://notion.so/my-integrations)
2. Get the integration token
3. Set `NOTION_TOKEN` environment variable

## Step 5: Monitoring and Maintenance

### 5.1 Logs
- Railway provides built-in logging
- Agent actions are logged to Supabase `agent_logs` table
- Monitor both Railway logs and Supabase logs

### 5.2 Database Monitoring
- Use Supabase dashboard to monitor database performance
- Set up alerts for high usage or errors
- Regular backups are handled automatically by Supabase

### 5.3 Scaling
- Railway automatically scales based on traffic
- Monitor resource usage and upgrade plan if needed
- Supabase scales automatically for database needs

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check
- `POST /agents` - Create new agent
- `GET /agents/{agent_id}` - Get agent details
- `POST /agents/{agent_id}/workflows` - Execute workflow
- `GET /workflows/{execution_id}` - Get workflow status
- `GET /agents/{agent_id}/memory` - Get agent memory
- `GET /agents/{agent_id}/logs` - Get agent logs

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check Supabase credentials
   - Verify database schema is created
   - Check network connectivity

2. **Agent Creation Failed**
   - Verify API keys are set correctly
   - Check integration configurations
   - Review agent logs in Supabase

3. **Workflow Execution Timeout**
   - Check Railway resource limits
   - Monitor long-running processes
   - Implement proper error handling

### Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Supabase Documentation: [supabase.com/docs](https://supabase.com/docs)
- Braid Issues: [GitHub Issues](https://github.com/your-username/braid/issues)

## Security Considerations

1. **Environment Variables**: Never commit API keys to version control
2. **Supabase RLS**: Configure Row Level Security policies as needed
3. **CORS**: Configure CORS settings for production domains
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Authentication**: Add proper authentication for production use
