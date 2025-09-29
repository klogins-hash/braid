#!/bin/bash
# Automated n8n + Braid Integration Setup Script

echo "🚀 Setting up n8n + Braid AI Integration..."

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first."
    exit 1
fi

# Get n8n project details
echo "📋 Available Railway projects:"
railway list

echo ""
echo "🔗 Setting up n8n integration..."

# Check if n8n project exists
read -p "Enter your n8n project name (e.g., n8n-testing-1): " N8N_PROJECT

# Get n8n URL
echo "🌐 Getting n8n URL..."
railway link $N8N_PROJECT 2>/dev/null || echo "⚠️  Could not auto-link to n8n project"

# Create webhook test script
cat > test_braid_chat.sh << 'EOF'
#!/bin/bash
# Test script for Braid + n8n chat integration

N8N_URL="$1"
if [ -z "$N8N_URL" ]; then
    echo "Usage: $0 <n8n-webhook-url>"
    echo "Example: $0 https://your-n8n.railway.app/webhook/braid-chat"
    exit 1
fi

echo "🧪 Testing Braid chat integration..."

curl -X POST "$N8N_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me with a research task?",
    "user_id": "test_user_123",
    "agent_type": "research",
    "tools": ["web_search", "notion"]
  }' \
  -w "\n\nResponse Code: %{http_code}\n"

echo "✅ Test completed!"
EOF

chmod +x test_braid_chat.sh

# Create agent management test script
cat > test_braid_agent.sh << 'EOF'
#!/bin/bash
# Test script for Braid agent management

N8N_URL="$1"
if [ -z "$N8N_URL" ]; then
    echo "Usage: $0 <n8n-webhook-url>"
    echo "Example: $0 https://your-n8n.railway.app/webhook/braid-manage"
    exit 1
fi

echo "🤖 Testing Braid agent creation..."

curl -X POST "$N8N_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "agent_type": "financial",
    "config": {
      "model": "claude-4-sonnet-20250101",
      "temperature": 0.3
    },
    "tools": ["calculator", "web_search"]
  }' \
  -w "\n\nResponse Code: %{http_code}\n"

echo "✅ Agent test completed!"
EOF

chmod +x test_braid_agent.sh

echo ""
echo "✅ Setup scripts created!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your n8n instance: https://your-n8n-project.railway.app"
echo "2. Import these workflow files:"
echo "   - n8n-workflows/braid-chat-workflow.json"
echo "   - n8n-workflows/braid-agent-manager.json"
echo "3. Get your webhook URLs from n8n"
echo "4. Test with: ./test_braid_chat.sh <webhook-url>"
echo "5. Test agents with: ./test_braid_agent.sh <webhook-url>"
echo ""
echo "🎯 Your Braid API: https://braid-production.up.railway.app"
echo "📚 API Docs: https://braid-production.up.railway.app/docs"
echo ""
echo "Need help? Check n8n-workflows/README.md for detailed instructions!"
