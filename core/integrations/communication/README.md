# Twilio Direct API Integration

Direct API integration for Twilio communication services, providing comprehensive messaging, voice, and verification capabilities without MCP server dependencies.

## 🚀 Features

### Core Communication
- **SMS/MMS Messaging**: Send text and multimedia messages
- **Voice Calls**: Initiate calls with TwiML or webhook support
- **WhatsApp Business**: Send WhatsApp messages via Business API
- **Email**: Send emails using SendGrid integration

### Verification & Lookup
- **Phone Verification**: Send 2FA codes via SMS, voice, or email
- **Phone Lookup**: Validate numbers and get carrier information

### Advanced Features
- **Serverless Functions**: Upload JavaScript functions to Twilio Functions
- **Static Assets**: Upload HTML, CSS, JS, and media files
- **Conversations**: Create multi-party messaging channels
- **Video Rooms**: Start video conferencing sessions
- **Sync Data**: Real-time data synchronization across devices

## 📋 Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```bash
# Required: Twilio Authentication (choose one method)

# Method 1: API Key (Recommended)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_API_KEY=your-api-key-sid
TWILIO_API_SECRET=your-api-key-secret

# Method 2: Auth Token (Alternative)  
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token

# Optional: Default Phone Numbers
TWILIO_PHONE_NUMBER=+1234567890       # For SMS/Voice
TWILIO_WHATSAPP_NUMBER=+1234567890    # For WhatsApp

# Optional: SendGrid Email
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Optional: Verification Service
TWILIO_VERIFY_SERVICE_SID=your-verify-service-sid
```

### 2. Get Twilio Credentials

1. **Sign up**: [Twilio Console](https://console.twilio.com/)
2. **Get Account SID**: Available on the console dashboard
3. **Create API Key** (Recommended):
   - Go to Console > Settings > API Keys
   - Click "Create API Key"
   - Choose "Standard" key type
   - Copy the SID and Secret

### 3. Install Dependencies

```bash
pip install requests python-dotenv
```

## 🔧 Usage Examples

### Basic Messaging

```python
from core.integrations.twilio.tools import send_sms, send_mms, send_whatsapp

# Send SMS
sms_result = send_sms.invoke({
    "to": "+1234567890",
    "from": "+1987654321",
    "body": "Hello from your AI assistant!"
})

# Send MMS with image
mms_result = send_mms.invoke({
    "to": "+1234567890", 
    "from": "+1987654321",
    "body": "Here's your receipt:",
    "media_url": ["https://example.com/receipt.jpg"]
})

# Send WhatsApp message
whatsapp_result = send_whatsapp.invoke({
    "to": "whatsapp:+1234567890",
    "from": "whatsapp:+1987654321", 
    "body": "Your appointment reminder"
})
```

### Voice Calls

```python
from core.integrations.twilio.tools import make_call

# Simple voice message
call_result = make_call.invoke({
    "to": "+1234567890",
    "from": "+1987654321",
    "twiml": '<Response><Say>Your order is ready!</Say></Response>'
})

# Dynamic call with webhook
ivr_call = make_call.invoke({
    "to": "+1234567890",
    "from": "+1987654321", 
    "url": "https://yourapp.com/call-handler"
})
```

### Email Notifications

```python
from core.integrations.twilio.tools import send_email

# Send email notification
email_result = send_email.invoke({
    "to": "customer@example.com",
    "from": "noreply@yourapp.com",
    "subject": "Order Confirmation",
    "html_content": "<h1>Thank you for your order!</h1>",
    "text_content": "Thank you for your order!"
})
```

### Phone Verification

```python
from core.integrations.twilio.tools import verify_phone, lookup_phone

# Send verification code
verification = verify_phone.invoke({
    "phone_number": "+1234567890",
    "channel": "sms"
})

# Lookup phone information
lookup_result = lookup_phone.invoke({
    "phone_number": "+1234567890",
    "lookup_type": ["carrier", "caller-name"]
})
```

### Agent Integration

```python
from core.integrations.twilio.tools import get_twilio_tools, get_messaging_tools

# In your agent setup
all_tools = get_twilio_tools()  # All Twilio tools
messaging_tools = get_messaging_tools()  # SMS/MMS/WhatsApp only

# Use in LangGraph agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)
```

## 🔍 Tool Reference

### Messaging Tools
- `send_sms()` - Send SMS messages
- `send_mms()` - Send multimedia messages  
- `send_whatsapp()` - Send WhatsApp messages

### Voice Tools
- `make_call()` - Initiate voice calls

### Email Tools
- `send_email()` - Send emails via SendGrid

### Verification Tools
- `verify_phone()` - Send verification codes
- `lookup_phone()` - Phone number lookup

### Serverless Tools
- `upload_function()` - Upload Twilio Functions
- `upload_asset()` - Upload static assets

### Advanced Tools
- `create_conversation()` - Multi-party messaging
- `start_video_room()` - Video conferencing
- `sync_data()` - Real-time data sync

### Tool Collections
- `get_twilio_tools()` - All tools
- `get_messaging_tools()` - Messaging only
- `get_voice_tools()` - Voice only
- `get_verification_tools()` - Verification only

## 🔒 Security Best Practices

1. **Use API Keys**: Prefer API Keys over Auth Tokens
2. **Environment Variables**: Never hardcode credentials
3. **Minimal Permissions**: Create API Keys with required permissions only
4. **Rate Limiting**: Monitor usage to avoid limits
5. **Rotate Credentials**: Regularly update API Keys

## 🚨 Error Handling

All tools return JSON responses with error information:

```json
{
  "error": true,
  "message": "Authentication failed",
  "status": "failed"
}
```

Successful responses include relevant data:

```json
{
  "sid": "SM1234567890abcdef",
  "status": "sent",
  "to": "+1234567890",
  "from": "+1987654321"
}
```

## 💰 Cost Considerations

- **Usage-Based Pricing**: Twilio charges per message, call, and API request
- **International Rates**: Higher costs for international communications
- **Monitor Usage**: Set up billing alerts in Twilio Console
- **Optimize**: Use appropriate message types and avoid unnecessary calls

## 📚 Additional Resources

- [Twilio Documentation](https://www.twilio.com/docs)
- [Twilio Console](https://console.twilio.com/)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [WhatsApp Business API](https://www.twilio.com/whatsapp)

## 🔄 Migration from MCP

This integration provides the same functionality as the Twilio MCP server but with direct API calls:

**Before (MCP)**:
```bash
npx @twilio-alpha/mcp
```

**After (Direct Integration)**:
```python
from core.integrations.twilio.tools import get_twilio_tools
tools = get_twilio_tools()
```

All tool names and functionality remain the same, ensuring easy migration from MCP-based agents.