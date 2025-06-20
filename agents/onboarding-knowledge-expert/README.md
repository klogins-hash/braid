# Onboarding & Internal Knowledge Expert Agent

A long-running LangGraph agent that automates employee onboarding and serves as a conversational expert on company knowledge.

## 🎯 Core Capabilities

### 1. Automated Onboarding Workflows
- **Multi-week Journey Management**: Personalized 30-day onboarding plans
- **Scheduled Task Execution**: Drip campaigns with welcome messages, check-ins, and milestone tracking
- **Meeting Coordination**: Automatic scheduling of intro meetings with managers, team leads, and buddies
- **Progress Monitoring**: Real-time tracking of onboarding completion and intervention when needed

### 2. RAG-Powered Knowledge Expert
- **Instant Q&A**: Natural language queries about policies, processes, and procedures
- **Cited Responses**: Always includes source document links for transparency
- **Multi-Category Search**: Policies, technical guides, contact information, and service forms
- **Context-Aware**: Understands intent and routes to appropriate information or services

### 3. Service Request Routing
- **Smart Form Detection**: Automatically routes requests to correct forms (IT, HR, Facilities)
- **Urgency Handling**: Escalation paths for urgent requests with immediate Slack notifications
- **Self-Service**: Direct links to common request forms and documentation

## 🏗️ Architecture

### LangGraph Workflow
```
Entry → parse_request_type → {
  "onboarding" → initiate_onboarding → agent → tools
  "knowledge_query" → search_knowledge → agent → tools  
  "service_request" → handle_service_request → agent → tools
}
```

### State Management
- **User Memory**: Individual onboarding progress and preferences
- **Task Scheduling**: Persistent queue for drip campaigns and reminders
- **Knowledge Index**: Company document embeddings and metadata

### Core Integrations
- **Slack**: DMs, channel mentions, user detection, notifications
- **Notion**: Company wiki, task assignments, document creation
- **Google Calendar**: Meeting scheduling for onboarding
- **Google Drive**: Document access and knowledge base
- **Perplexity**: Fallback research for uncovered topics

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Required API keys
OPENAI_API_KEY=your_openai_key
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
NOTION_API_KEY=your_notion_integration_token
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json

# Optional integrations
PERPLEXITY_API_KEY=your_perplexity_key
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Interactive Agent
```bash
python agent.py
```

### 4. Test Scenarios
```
# Onboarding
"New hire Sarah Johnson started today in Engineering"

# Knowledge Queries  
"How do I submit an expense report?"
"What are our remote work policies?"
"Who is the product manager for Project Alpha?"

# Service Requests
"I need access to Figma"
"How do I request a software license?"
```

## 📋 Usage Examples

### New Employee Onboarding
When a new hire joins, the agent automatically:

1. **Day 1 Welcome Package**
   - Personalized welcome DM
   - Essential document links
   - Scheduled intro meetings

2. **Ongoing Support** (Days 3, 7, 14, 21, 30)
   - Progress check-ins
   - Resource sharing
   - Task assignments
   - Feedback collection

3. **Completion Tracking**
   - Milestone completion monitoring
   - Intervention for blockers
   - Graduation to regular support

### Knowledge Base Queries
The agent provides instant, cited answers to:

- **Policy Questions**: "What's our PTO policy?"
- **Process Inquiries**: "How does code review work?"
- **Contact Finding**: "Who manages the backend team?"
- **Technical Help**: "How do I access the VPN?"

### Service Request Handling
Intelligent routing for common requests:

- **IT Support**: Hardware, software, access issues
- **Software Licenses**: Figma, Adobe, development tools
- **HR Requests**: Benefits, time off, workplace issues
- **Facilities**: Office supplies, room booking

## 🔧 Customization

### Adding Knowledge Documents
Edit `knowledge_tools.py` to add new documents:
```python
KNOWLEDGE_BASE["policies"]["new_policy"] = {
    "title": "New Policy Title",
    "content": "Policy content...",
    "source_url": "https://company.notion.so/new-policy",
    "keywords": ["keyword1", "keyword2"]
}
```

### Customizing Onboarding Journeys
Modify `onboarding_tools.py` templates:
```python
ONBOARDING_TEMPLATES["custom_30_day"] = {
    "duration_days": 30,
    "tasks": [
        {
            "day": 1,
            "task_id": "custom_welcome",
            "title": "Custom Welcome",
            "action_type": "automated_message"
        }
    ]
}
```

### Adding New Service Routes
Extend service request routing in `knowledge_tools.py`:
```python
service_routes["new_service"] = {
    "form_url": "https://company.form.com",
    "slack_channel": "#new-service",
    "description": "Service description"
}
```

## 🎯 Production Deployment

### Memory Store Configuration
For production, replace in-memory storage with persistent store:
```python
# In agent.py, configure LangGraph memory
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string="postgresql://...")
```

### Slack App Setup
1. Create Slack app with bot permissions
2. Subscribe to message events
3. Install to workspace
4. Configure slash commands (optional)

### Vector Database (RAG)
For large knowledge bases, implement vector search:
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Replace keyword search with semantic search
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./knowledge_db"
)
```

### Scheduling Service
Implement proper task scheduling:
```python
# Use Celery, Airflow, or cloud scheduler
from celery import Celery
app = Celery('onboarding_scheduler')

@app.task
def send_scheduled_onboarding_message(user_id, message_template):
    # Execute scheduled onboarding task
    pass
```

## 📊 Monitoring & Analytics

### Onboarding Metrics
- Completion rates by journey type
- Time to complete milestones
- Drop-off points and interventions
- User satisfaction scores

### Knowledge Usage
- Most frequently asked questions
- Search success rates
- Document engagement metrics
- Knowledge gap identification

### Service Request Analytics
- Request volume by category
- Resolution times
- Escalation rates
- User satisfaction

## 🔒 Security & Privacy

### Data Handling
- No sensitive data in logs
- User data encrypted at rest
- API keys stored securely
- Audit trail for all actions

### Access Control
- Slack workspace membership required
- Role-based access to sensitive documents
- Manager approval for certain onboarding tasks
- IT approval for system access requests

## 🤝 Contributing

### Adding New Features
1. Follow existing tool patterns in `*_tools.py`
2. Update agent state schema if needed
3. Add appropriate workflow nodes
4. Include tests and documentation

### Testing
```bash
# Run unit tests
pytest tests/

# Test individual tools
python -m pytest tests/test_onboarding_tools.py
python -m pytest tests/test_knowledge_tools.py
```

## 📚 Architecture Details

### Tool Categories
- **Communication**: Slack messaging and user management
- **Onboarding**: Journey scheduling and progress tracking  
- **Knowledge**: RAG search and document retrieval
- **Service**: Request routing and form management
- **Scheduling**: Task automation and reminders

### State Persistence
- **Onboarding Progress**: Individual journey tracking
- **Conversation Memory**: Context across interactions
- **Knowledge Cache**: Frequently accessed documents
- **Task Queue**: Scheduled onboarding activities

### Integration Patterns
- **Direct API Calls**: Following `core/integrations/` patterns
- **Error Handling**: Graceful fallbacks and user communication
- **Rate Limiting**: Respectful API usage
- **Webhook Support**: Real-time Slack events

## 🎉 Benefits Delivered

### For New Hires
- Consistent, personalized onboarding experience
- Always-available support and information
- Clear progression tracking and milestones
- Reduced anxiety about company processes

### For HR & Management
- Automated administrative tasks
- Data-driven onboarding insights
- Scalable process standardization
- Reduced repetitive question load

### For All Employees
- Instant access to company knowledge
- Self-service for common requests
- Consistent, accurate information
- Reduced friction for internal processes

This agent demonstrates sophisticated LangGraph capabilities while solving real organizational challenges around onboarding efficiency and knowledge accessibility.