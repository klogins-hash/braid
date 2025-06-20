# Twilio MCP Server

Twilio MCP provides comprehensive communication capabilities through the Model Context Protocol, enabling AI agents to send SMS/MMS, make voice calls, send WhatsApp messages, handle email, and manage serverless functions using Twilio's APIs.

## Overview

The Twilio MCP Server is an official alpha implementation from Twilio Labs that exposes Twilio's Public APIs to AI tools through the Model Context Protocol. It provides dynamic access to all Twilio communication services including messaging, voice, video, email, and serverless platform management.

## Capabilities

### Messaging Services

- **`twilio_send_sms`**: Send text messages to phone numbers
  - Input: To number, from number, message body
  - Output: Message SID and delivery status
  - Supports: International numbers, delivery receipts, message scheduling

- **`twilio_send_mms`**: Send multimedia messages with images and media
  - Input: To number, from number, message body, media URLs
  - Output: Message SID and media delivery status
  - Supports: Images, audio, video, multiple media attachments

- **`twilio_send_whatsapp`**: Send WhatsApp messages via WhatsApp Business API
  - Input: WhatsApp number, message content, media (optional)
  - Output: Message SID and WhatsApp delivery status
  - Supports: Rich media, templates, interactive messages

### Voice Services

- **`twilio_make_call`**: Initiate voice calls and handle call flow
  - Input: To number, from number, TwiML instructions or webhook URL
  - Output: Call SID and call status
  - Supports: Interactive voice response (IVR), call recording, conferencing

### Email Services

- **`twilio_send_email`**: Send emails using SendGrid integration
  - Input: Recipient, sender, subject, content (HTML/text)
  - Output: Email message ID and delivery status
  - Supports: Templates, attachments, tracking, personalization

### Verification and Lookup

- **`twilio_verify_phone`**: Verify phone numbers and send two-factor authentication codes
  - Input: Phone number, verification channel (SMS/call/email)
  - Output: Verification SID and status
  - Supports: Custom code length, international numbers, fraud detection

- **`twilio_lookup_phone`**: Validate and get information about phone numbers
  - Input: Phone number, lookup type
  - Output: Number format, carrier info, line type
  - Supports: International formatting, carrier detection, fraud scoring

### Serverless Platform

- **`twilio_upload_function`**: Upload JavaScript serverless functions to Twilio Functions
  - Input: Service SID, function path, JavaScript code, environment variables
  - Output: Function SID and deployment status
  - Supports: Dependencies, environment configuration, versioning

- **`twilio_upload_asset`**: Upload static assets for serverless applications
  - Input: Service SID, asset path, content, content type
  - Output: Asset SID and upload status
  - Supports: HTML, CSS, JavaScript, images, custom MIME types

### Advanced Communication

- **`twilio_create_conversation`**: Create conversation channels for multi-party messaging
  - Input: Conversation name, participants, webhook URLs
  - Output: Conversation SID and participant details
  - Supports: Group messaging, media sharing, participant management

- **`twilio_start_video_room`**: Create video rooms for video conferencing and calls
  - Input: Room name, type, recording options
  - Output: Room SID and connection details
  - Supports: Peer-to-peer, group rooms, recording, screen sharing

- **`twilio_sync_data`**: Manage real-time data synchronization across devices
  - Input: Sync service SID, document/list/map data
  - Output: Sync object SID and update status
  - Supports: Real-time updates, conflict resolution, TTL

## Setup Instructions

### Prerequisites

- Node.js ≥20.0.0
- npm ≥10.0.0
- Twilio account with API credentials

### Authentication Setup

#### Step 1: Create Twilio Account

1. **Sign up at Twilio Console**: [https://console.twilio.com/](https://console.twilio.com/)
2. **Verify your account** and phone number
3. **Get your Account SID** from the console dashboard

#### Step 2: Create API Keys (Recommended)

1. **Navigate to API Keys**: Console > Settings > API Keys
2. **Create a new API Key**:
   - Click "Create API Key"
   - Choose "Standard" key type
   - Set a friendly name (e.g., "AI Agent MCP")
   - Copy the SID and Secret (Secret shown only once)

#### Step 3: Set Environment Variables

Add to your `.env` file:

```bash
# Twilio Credentials (Required)
TWILIO_ACCOUNT_SID=your-account-sid-here
TWILIO_API_KEY=your-api-key-sid-here
TWILIO_API_SECRET=your-api-key-secret-here

# Optional: Service Filtering
TWILIO_SERVICES=messaging,voice,verify
TWILIO_TAGS=send,receive,create
```

### Installation

The MCP server runs via NPX and doesn't require local installation:

```bash
# Test installation
npx -y @twilio-alpha/mcp

# With service filtering
npx -y @twilio-alpha/mcp --services messaging,voice

# With tag filtering  
npx -y @twilio-alpha/mcp --tags send,receive
```

For Braid integration, the server is automatically configured:

```bash
braid new my-communication-agent --mcps twilio
braid package --production
```

## Usage Examples

### SMS and Messaging

```python
# Send a simple SMS
sms_result = agent.twilio_send_sms(
    to="+1234567890",
    from_="+1987654321", 
    body="Hello from your AI assistant! Your order #12345 has shipped."
)
print(f"SMS sent: {sms_result['sid']}")

# Send an MMS with image
mms_result = agent.twilio_send_mms(
    to="+1234567890",
    from_="+1987654321",
    body="Here's your receipt:",
    media_url=["https://example.com/receipt.jpg"]
)

# Send WhatsApp message
whatsapp_result = agent.twilio_send_whatsapp(
    to="whatsapp:+1234567890",
    from_="whatsapp:+1987654321",
    body="Your appointment reminder: Tomorrow at 2 PM"
)
```

### Voice Calls and IVR

```python
# Make a simple voice call
call_result = agent.twilio_make_call(
    to="+1234567890",
    from_="+1987654321",
    twiml='<Response><Say>Hello! Your order is ready for pickup.</Say></Response>'
)

# Interactive voice response
ivr_call = agent.twilio_make_call(
    to="+1234567890", 
    from_="+1987654321",
    url="https://myapp.com/ivr-webhook"  # TwiML webhook for dynamic responses
)
print(f"Call initiated: {call_result['sid']}")
```

### Email and Notifications

```python
# Send email notification
email_result = agent.twilio_send_email(
    to="customer@example.com",
    from_="noreply@myapp.com",
    subject="Order Confirmation #12345",
    html_content="<h1>Thank you for your order!</h1><p>We'll ship it soon.</p>",
    text_content="Thank you for your order! We'll ship it soon."
)

# Send with template
template_email = agent.twilio_send_email(
    to="customer@example.com",
    template_id="d-1234567890abcdef",
    dynamic_template_data={
        "customer_name": "John Doe",
        "order_number": "12345",
        "total": "$99.99"
    }
)
```

### Phone Verification and Security

```python
# Send verification code
verification = agent.twilio_verify_phone(
    phone_number="+1234567890",
    channel="sms",  # or "call", "email"
    locale="en"
)
print(f"Verification sent: {verification['sid']}")

# Lookup phone number info
lookup_result = agent.twilio_lookup_phone(
    phone_number="+1234567890",
    type=["carrier", "caller-name"]
)
print(f"Carrier: {lookup_result['carrier']['name']}")
print(f"Line type: {lookup_result['carrier']['type']}")
```

### Serverless Functions

```python
# Upload a Twilio Function
function_code = '''
exports.handler = function(context, event, callback) {
    const response = new Twilio.Response();
    response.appendHeader('Content-Type', 'application/json');
    response.setBody({
        message: 'Hello from Twilio Functions!',
        timestamp: new Date().toISOString()
    });
    callback(null, response);
};
'''

function_result = agent.twilio_upload_function(
    service_sid="ZS1234567890abcdef",
    function_sid="ZH1234567890abcdef", 
    path="/hello-world",
    visibility="public",
    content=function_code
)

# Upload static asset
asset_result = agent.twilio_upload_asset(
    service_sid="ZS1234567890abcdef",
    asset_sid="ZH1234567890abcdef",
    path="/style.css",
    visibility="public",
    content="body { font-family: Arial; }",
    content_type="text/css"
)
```

### Advanced Communication Flows

```python
# Create a group conversation
conversation = agent.twilio_create_conversation(
    unique_name="support-chat-12345",
    friendly_name="Customer Support Chat"
)

# Add participants
participants = agent.add_conversation_participants(
    conversation_sid=conversation['sid'],
    participants=[
        {"identity": "customer", "address": "+1234567890"},
        {"identity": "agent", "address": "+1987654321"}
    ]
)

# Start video room
video_room = agent.twilio_start_video_room(
    unique_name="support-call-12345",
    type="group",
    record_participants_on_connect=True,
    video_codecs=["VP8", "H264"]
)
print(f"Video room: {video_room['sid']}")
```

## Use Cases

### Customer Support Automation

- **Multi-channel Support**: Handle SMS, voice, WhatsApp, and email inquiries
- **Escalation Management**: Route complex issues to human agents
- **Automated Responses**: Send instant acknowledgments and status updates
- **Call Center Integration**: Manage inbound/outbound calls with IVR

### Marketing and Engagement

- **Campaign Management**: Send targeted SMS and email campaigns
- **Event Notifications**: Automated reminders and confirmations
- **Customer Onboarding**: Welcome sequences across multiple channels
- **Feedback Collection**: Post-purchase surveys via SMS or voice

### Security and Verification

- **Two-Factor Authentication**: SMS and voice verification codes
- **Fraud Prevention**: Phone number validation and risk scoring
- **Account Security**: Login notifications and security alerts
- **Identity Verification**: Phone number ownership confirmation

### Business Operations

- **Order Management**: Shipping notifications and delivery updates
- **Appointment Systems**: Automated booking confirmations and reminders
- **Payment Processing**: Transaction confirmations and alerts
- **Emergency Notifications**: Critical system alerts and status updates

### Development and Integration

- **Serverless Workflows**: Deploy communication logic as Twilio Functions
- **Webhook Management**: Handle incoming messages and call events
- **API Integration**: Connect Twilio with existing business systems
- **Custom Applications**: Build communication features into applications

## Configuration Options

### Service Filtering

Limit which Twilio services are exposed to optimize performance:

```bash
# Only messaging and voice
npx @twilio-alpha/mcp --services messaging,voice

# Add verification and lookup
npx @twilio-alpha/mcp --services messaging,voice,verify,lookups
```

Available services:
- `messaging` - SMS, MMS, WhatsApp
- `voice` - Voice calls, conferencing, recordings
- `verify` - Phone verification and 2FA
- `lookups` - Phone number information
- `conversations` - Multi-party messaging
- `video` - Video calling and rooms
- `sync` - Real-time data synchronization
- `serverless` - Functions and assets
- `notify` - Push notifications

### Tag Filtering

Filter API endpoints by functionality:

```bash
# Only create and send operations
npx @twilio-alpha/mcp --tags send,create

# Read and list operations
npx @twilio-alpha/mcp --tags read,list
```

### Environment Configuration

```bash
# Core credentials
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_API_KEY=your-api-key-sid  
TWILIO_API_SECRET=your-api-key-secret

# Optional filtering
TWILIO_SERVICES=messaging,voice,verify
TWILIO_TAGS=send,receive,create,read

# Performance tuning
TWILIO_TIMEOUT=30000
TWILIO_RETRY_ATTEMPTS=3
```

## Security Best Practices

### Credential Management

- **Use API Keys**: Prefer API Keys over Account SID/Auth Token
- **Scope Permissions**: Create API Keys with minimal required permissions
- **Rotate Regularly**: Rotate API Keys periodically for security
- **Environment Variables**: Never hardcode credentials in code

### API Access Control

- **Service Filtering**: Limit exposed services to what's needed
- **Tag Filtering**: Restrict API endpoints by functionality
- **Rate Limiting**: Monitor API usage and implement rate limits
- **IP Allowlisting**: Restrict API access to known IP addresses

### Monitoring and Auditing

- **Usage Tracking**: Monitor API calls and usage patterns
- **Error Logging**: Log and alert on authentication failures
- **Cost Management**: Set up billing alerts for unexpected usage
- **Compliance**: Ensure communication complies with regulations (TCPA, GDPR)

## Performance Optimization

### Context Management

```bash
# Reduce context size by filtering services
npx @twilio-alpha/mcp --services messaging,verify

# Limit API surface with tags
npx @twilio-alpha/mcp --tags send,receive
```

### Connection Optimization

- **Persistent Connections**: MCP maintains connection pools
- **Request Batching**: Group related API calls when possible
- **Caching**: Cache lookup results and configuration data
- **Async Operations**: Use async patterns for better performance

### Memory Management

- **Resource Cleanup**: Properly dispose of resources after use
- **Message Queuing**: Queue large volumes of messages appropriately
- **Media Handling**: Stream large media files instead of loading in memory

## Troubleshooting

### Common Issues

**Authentication Errors**
- Verify Account SID and API Key/Secret are correct
- Check API Key permissions and expiration
- Ensure credentials are properly set in environment variables

**Rate Limiting**
- Monitor Twilio console for rate limit notifications
- Implement exponential backoff for retries
- Consider upgrading Twilio account for higher limits

**Message Delivery Issues**
- Verify phone numbers are in correct international format
- Check message content for compliance with carrier requirements
- Review Twilio debugger logs for delivery failures

**WhatsApp Setup**
- Ensure WhatsApp Business API is enabled
- Verify sender number is approved for WhatsApp
- Check message templates are approved for business use

### Debug Mode

Enable debug logging:

```bash
DEBUG=* npx @twilio-alpha/mcp
```

### Support Resources

- **Twilio Documentation**: [https://www.twilio.com/docs](https://www.twilio.com/docs)
- **MCP Repository**: [https://github.com/twilio-labs/mcp](https://github.com/twilio-labs/mcp)
- **Twilio Console**: [https://console.twilio.com/](https://console.twilio.com/)
- **Developer Community**: [https://community.twilio.com/](https://community.twilio.com/)

## Integration with Braid

When using Twilio MCP with Braid agents, tools are automatically available with the `twilio_` prefix:

- `twilio_send_sms()` - Send text messages
- `twilio_make_call()` - Initiate voice calls  
- `twilio_send_whatsapp()` - Send WhatsApp messages
- `twilio_send_email()` - Send emails via SendGrid
- `twilio_verify_phone()` - Send verification codes
- `twilio_upload_function()` - Deploy serverless functions

The MCP runs as a subprocess with proper credential management and API optimization.

## Limitations and Considerations

### Alpha Software

- **Breaking Changes**: API may change between versions
- **Limited Support**: Community support through GitHub issues
- **Stability**: Not recommended for production use yet
- **Documentation**: May be incomplete or outdated

### API Limitations

- **Rate Limits**: Based on Twilio account type and service
- **Context Size**: Large API surface may impact LLM performance
- **Network Dependency**: Requires internet connectivity
- **Account Requirements**: Some features require paid Twilio accounts

### Cost Considerations

- **Usage-Based Pricing**: Twilio charges per message, call, and API request
- **International Rates**: Higher costs for international communications
- **Premium Features**: Advanced features may require higher-tier accounts
- **Monitoring**: Set up billing alerts to avoid unexpected charges

## Advanced Configuration

### Custom Tool Configuration

```bash
# Disable specific services
npx @twilio-alpha/mcp --services messaging,voice

# Focus on specific functionality
npx @twilio-alpha/mcp --tags send,verify
```

### Production Deployment

```bash
# Set production environment variables
export TWILIO_ACCOUNT_SID=prod-account-sid
export TWILIO_API_KEY=prod-api-key
export TWILIO_API_SECRET=prod-api-secret

# Run with service filtering for security
npx @twilio-alpha/mcp --services messaging,verify,lookups
```

### Monitoring Setup

```bash
# Enable comprehensive logging
export DEBUG=twilio-mcp:*
export TWILIO_LOG_LEVEL=info

# Set up alerts for errors
export TWILIO_ERROR_WEBHOOK=https://your-app.com/twilio-errors
```

## Future Roadmap

The Twilio MCP is actively developed with planned improvements:

- **Stable Release**: Move from alpha to stable version
- **Enhanced Documentation**: Comprehensive guides and examples
- **Additional Services**: Support for more Twilio products
- **Performance Optimization**: Better context management and caching
- **Security Enhancements**: Additional authentication methods and controls

## Contributing

The Twilio MCP is open source under MIT license. Contributions welcome:

- **GitHub Repository**: [https://github.com/twilio-labs/mcp](https://github.com/twilio-labs/mcp)
- **Issue Tracking**: Report bugs and request features via GitHub issues
- **Development**: Follow standard open source contribution guidelines
- **Testing**: Help test new features and report compatibility issues