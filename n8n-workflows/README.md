# Braid AI Agent - n8n Integration

## 🚀 Quick Setup

### 1. Import Workflows to n8n

1. **Access your n8n instance**: Go to your n8n-testing-1 Railway deployment
2. **Import workflows**:
   - Go to **Workflows** → **Import from File**
   - Import `braid-chat-workflow.json`
   - Import `braid-agent-manager.json`

### 2. Configure Webhooks

Both workflows will create webhook URLs you can use:

**Chat Workflow Webhook:**
```
POST https://your-n8n-url.railway.app/webhook/braid-chat
```

**Agent Manager Webhook:**
```
POST https://your-n8n-url.railway.app/webhook/braid-manage
```

## 💬 Using the Chat Interface

### Start a Chat Session
```bash
curl -X POST "https://your-n8n-url.railway.app/webhook/braid-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with research",
    "user_id": "user123",
    "agent_type": "research"
  }'
```

### Create a Specific Agent
```bash
curl -X POST "https://your-n8n-url.railway.app/webhook/braid-manage" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "agent_type": "financial",
    "config": {
      "model": "claude-4-opus-20250101",
      "temperature": 0.3
    },
    "tools": ["web_search", "calculator"]
  }'
```

## 🔧 Workflow Features

### Braid Chat Workflow
- **Trigger**: Webhook receives chat messages
- **Creates**: New Braid agent for each conversation
- **Executes**: Chat workflow with Claude 4
- **Returns**: Agent ID and execution status

### Braid Agent Manager
- **Create Agents**: Different types (research, financial, etc.)
- **Get Agent Info**: Retrieve agent details
- **Configure Models**: Choose Claude 4 variants
- **Set Tools**: Add integrations (Slack, Notion, etc.)

## 🎯 Integration Options

### Connect to Chat Platforms

**Slack Integration:**
- Add Slack trigger node before Braid chat workflow
- Route Slack messages to Braid agents
- Send responses back to Slack channels

**Discord Integration:**
- Use Discord webhook trigger
- Process Discord messages through Braid
- Send AI responses to Discord channels

**Telegram Integration:**
- Telegram bot webhook trigger
- Route messages to appropriate Braid agents
- Send responses back to Telegram chats

### Advanced Workflows

**Multi-Agent Conversations:**
- Create different agents for different tasks
- Route messages based on content/intent
- Coordinate between multiple AI agents

**Integration Workflows:**
- Connect to Google Workspace
- Automate Notion updates
- Process emails through AI agents
- Generate reports and summaries

## 🔑 Environment Variables

Make sure your n8n instance can access:
- `BRAID_API_URL=https://braid-production.up.railway.app`
- Any integration API keys (Slack, Discord, etc.)

## 📊 Monitoring

Use n8n's built-in execution monitoring to:
- Track agent creation and usage
- Monitor workflow performance
- Debug integration issues
- View conversation logs

## 🚀 Next Steps

1. **Import the workflows** to your n8n instance
2. **Test the webhooks** with the provided curl commands
3. **Add chat platform integrations** (Slack, Discord, etc.)
4. **Customize agent configurations** for your use cases
5. **Set up monitoring and logging** for production use

Your Braid AI agents are now accessible through n8n's powerful workflow automation! 🤖✨
