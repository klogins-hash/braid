# 🏦 Autonomous Accounts Receivable Clerk

An intelligent agent that automates the complete accounts receivable lifecycle from contract ingestion to cash collection, replacing manual AR processes with intelligent automation.

## 🎯 **What This Agent Does**

### **Core Capabilities**
- **Contract Monitoring**: Monitors Google Drive for new signed contracts
- **Data Extraction**: AI-powered parsing of contract terms and billing information
- **Client Management**: Automatically creates clients in Xero accounting system
- **Invoice Automation**: Generates and schedules invoices based on contract terms
- **Payment Tracking**: Monitors payment status and identifies overdue accounts
- **Collections Automation**: Multi-stage escalation process for overdue payments

### **Business Value**
- **Eliminates Manual AR Work**: Automates 80%+ of routine accounts receivable tasks
- **Improves Cash Flow**: Faster invoice generation and systematic collections
- **Reduces Human Error**: Consistent processing and accurate data entry
- **Scales Operations**: Handles unlimited contracts without additional staff
- **Provides Audit Trail**: Complete history of all AR activities and communications

## 🔧 **Technical Architecture**

### **Workflow Overview**
```
Contract Detection → Data Extraction → Client/Invoice Creation → Payment Monitoring → Collections
```

### **State Management**
The agent maintains persistent state across the AR lifecycle:
```python
ARClerkState:
  - contract_data: Extracted contract information
  - client_info: Xero client details
  - invoice_schedule: Billing timeline and milestones
  - collection_status: Overdue tracking and escalation stages
  - processed_files: Avoid duplicate contract processing
```

### **Integration Points**
- **Xero API**: Client management, invoice creation, payment tracking
- **Google Workspace**: Contract monitoring, email communications
- **Slack**: Internal notifications and escalations
- **Twilio**: SMS reminders for overdue accounts
- **Perplexity**: AI-powered contract data extraction

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
cd agents/accounts-receivable-clerk/
pip install -r requirements.txt
cp .env.template .env
# Configure your API keys in .env
```

### **2. Required API Keys**
```bash
# Core LLM
OPENAI_API_KEY=your_openai_key

# Financial Integration
XERO_ACCESS_TOKEN=your_xero_token
XERO_TENANT_ID=your_tenant_id

# Document Processing
PERPLEXITY_API_KEY=your_perplexity_key

# Communication (Optional)
SLACK_BOT_TOKEN=your_slack_token
TWILIO_API_KEY=your_twilio_key

# Google Workspace
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account.json

# Observability
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=accounts-receivable-clerk
```

### **3. Test the Agent**
```bash
python agent.py
```

## 💼 **Usage Examples**

### **Process New Contract**
```
"Process new contract for TechCorp Solutions, $25,000 annual software license, Net 30 payment terms"
```

### **Monitor Payments**
```
"Check payment status for all outstanding invoices and run collections if needed"
```

### **Collections Management**
```
"Run collections process for accounts over 30 days past due"
```

## 🔄 **Workflow Details**

### **1. Contract Monitoring**
- Monitors designated Google Drive folder for new contracts
- Identifies signed documents (PDFs, Google Docs)
- Tracks processed files to avoid duplicates

### **2. Data Extraction**
Uses AI to extract critical information:
- **Client Details**: Name, contact information, billing address
- **Service Information**: Description, deliverables, timeline
- **Financial Terms**: Total value, payment schedule, billing terms
- **Contract Dates**: Start date, milestones, completion date

### **3. Client & Invoice Management**
- **Client Creation**: Checks if client exists in Xero, creates new contact if needed
- **Invoice Generation**: Creates invoices based on extracted billing terms
- **Scheduling**: Sets up recurring invoices for subscription/milestone billing
- **Automation**: Sends invoices automatically according to contract terms

### **4. Payment Monitoring**
- **Status Tracking**: Regular checks of invoice payment status
- **Overdue Detection**: Identifies accounts past due date
- **Escalation Triggers**: Automatically initiates collections process

### **5. Collections Automation**
Multi-stage escalation process:

#### **Stage 1: Email Reminder (7+ days overdue)**
- Professional email with invoice copy
- Payment instructions and contact information
- Maintains positive customer relationship

#### **Stage 2: SMS Alert (14+ days overdue)**
- Direct SMS to billing contact
- Urgent but professional tone
- Clear payment deadline

#### **Stage 3: Human Escalation (30+ days overdue)**
- Slack notification to finance team
- Complete account history and communication log
- Recommended next steps for human intervention

## 📊 **Key Features**

### **Intelligent Processing**
- **Contract Recognition**: Identifies contract types and billing structures
- **Term Extraction**: Understands complex billing terms (Net 30, milestone payments, etc.)
- **Client Matching**: Prevents duplicate client creation in Xero
- **Amount Validation**: Verifies extracted amounts against contract language

### **Robust Error Handling**
- **API Fallbacks**: Graceful handling of Xero/Google API failures
- **Data Validation**: Ensures extracted contract data is complete and accurate
- **Human Escalation**: Automatic escalation when automation cannot proceed
- **Audit Logging**: Complete trail of all actions and decisions

### **Communication Management**
- **Multi-Channel**: Email, SMS, and Slack notifications
- **Template-Based**: Consistent, professional communication templates
- **Escalation Logic**: Appropriate communication for each collection stage
- **Response Tracking**: Monitors client responses and adjusts approach

## 🔧 **Configuration Options**

### **Collections Timing**
Customize escalation schedule:
```python
COLLECTION_STAGES = {
    "stage_1_email": 7,    # Days overdue for email reminder
    "stage_2_sms": 14,     # Days overdue for SMS alert
    "stage_3_escalate": 30 # Days overdue for human escalation
}
```

### **Contract Monitoring**
Configure monitoring settings:
```python
DRIVE_FOLDER_ID = "your_google_drive_folder_id"
SUPPORTED_FORMATS = [".pdf", ".docx", ".gdoc"]
PROCESSING_INTERVAL = 300  # Check every 5 minutes
```

### **Invoice Templates**
Customize invoice generation:
```python
DEFAULT_PAYMENT_TERMS = "Net 30"
INVOICE_PREFIX = "INV"
AUTO_SEND_INVOICES = True
```

## 📈 **Production Deployment**

### **Scheduling Options**
- **Cron Jobs**: Schedule regular contract monitoring and payment checks
- **Event-Driven**: Trigger on Google Drive file uploads
- **API Webhooks**: Integrate with existing business systems

### **Monitoring & Alerting**
- **LangSmith Tracing**: Complete workflow observability
- **Error Notifications**: Slack alerts for processing failures
- **Performance Metrics**: Track processing times and success rates
- **Audit Reports**: Regular summaries of AR activities

### **Security Considerations**
- **API Key Rotation**: Regular credential updates
- **Data Encryption**: Secure handling of financial information
- **Access Controls**: Proper scoping of API permissions
- **Compliance**: SOX, PCI DSS considerations for financial data

## 🚨 **Important Notes**

### **Data Accuracy**
- Always validates extracted contract data before creating invoices
- Provides clear audit trail of all automated actions
- Includes human review checkpoints for high-value contracts

### **Client Communications**
- Maintains professional tone in all automated communications
- Respects customer communication preferences
- Provides easy escalation path to human support

### **Financial Integration**
- Works with existing Xero accounting workflows
- Preserves manual override capabilities
- Integrates with existing approval processes

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Contract Extraction Errors**
- Verify contract format is supported (PDF, DOCX, Google Docs)
- Check that contract contains required billing information
- Review Perplexity API response for parsing issues

#### **Xero Integration Problems**
- Validate Xero API credentials and permissions
- Check tenant ID matches your Xero organization
- Verify contact creation permissions in Xero

#### **Communication Failures**
- Confirm email/SMS credentials are configured
- Check recipient contact information is valid
- Review message templates for compliance requirements

### **Debug Mode**
Enable detailed logging:
```bash
export LANGCHAIN_TRACING_V2=true
export LOG_LEVEL=DEBUG
python agent.py
```

## 📞 **Support**

For issues with:
- **Xero Integration**: See `core/integrations/finance/xero/README.md`
- **Google Workspace**: See `core/integrations/productivity/gworkspace/README.md`
- **Agent Development**: See project `CLAUDE.md` for development patterns

---

**This agent represents a production-ready solution for automating accounts receivable operations, designed to integrate seamlessly with existing business processes while providing comprehensive audit trails and human oversight capabilities.**