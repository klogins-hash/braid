# Braid Tool Reference

Complete reference for all available tools in the Braid agent ecosystem. Use this guide when creating agents to select the optimal tool combination for your specific use case.

## Tool Categories Overview

```
📁 External Integrations (core/integrations/)
   🏢 Business & Productivity Services
   
📁 In-House Tools (core/tools/)
   📊 Data Processing & Analysis
   🌐 Network & Communication  
   ⚙️ Workflow Control & Automation
```

---

## 🏢 External Integrations

### Google Workspace (`gworkspace`)
**Use for**: Gmail, Google Calendar, Google Sheets, Google Drive integration

**Tools Available**: 4 tools
- **gmail_send**: Send emails through Gmail
- **gmail_search**: Search and retrieve emails
- **google_calendar_create_event**: Create calendar appointments
- **google_calendar_list_events**: List calendar events
- **google_sheets_read**: Read data from spreadsheets
- **google_sheets_write**: Write data to spreadsheets

**Common Use Cases**:
- Email automation and notifications
- Calendar scheduling and management
- Spreadsheet data processing
- Document management workflows

**Dependencies**: Google API credentials required

---

### Slack (`slack`)
**Use for**: Team communication, notifications, bot interactions

**Tools Available**: 12 tools
- **slack_send_message**: Send messages to channels/users
- **slack_get_channels**: List available channels
- **slack_get_users**: Get user information
- **slack_upload_file**: Upload files to Slack
- **slack_get_channel_history**: Retrieve message history
- And 7 more specialized tools

**Common Use Cases**:
- Team notifications and alerts
- Status updates and reporting
- File sharing and collaboration
- Interactive bot responses

**Dependencies**: Slack workspace and bot token required

---

## 📊 Data Processing & Analysis

### File Operations (`files`)
**Use for**: Basic file system operations

**Tools Available**: 3 tools
- **file_store**: Save content to files with safety checks
- **file_read**: Read file content with size limits and metadata
- **file_list**: List directory contents with pattern matching

**Common Use Cases**:
- Save agent outputs to files
- Read configuration or input files
- Manage file-based workflows
- Create reports and logs

**Dependencies**: None (standard library)

---

### CSV Processing (`csv`)
**Use for**: Structured data analysis and processing

**Tools Available**: 1 tool
- **csv_processor**: Read, analyze, filter, and process CSV files
  - Operations: read, info, sample, filter, summary
  - Automatic delimiter detection
  - Statistical summaries

**Common Use Cases**:
- Process data exports
- Generate reports from structured data
- Data cleaning and analysis
- Import/export workflows

**Dependencies**: None (standard library)

---

### Data Transformation (`transform`)
**Use for**: ETL-style data processing and manipulation

**Tools Available**: 5 tools
- **edit_fields**: Rename, add, or remove fields on data items
- **filter_items**: Keep only items matching conditions (SQL-like operators)
- **date_time**: Manipulate dates/times and calculate intervals  
- **sort_items**: Order items by one or more fields
- **rename_keys**: Bulk-rename field names via mapping

**Common Use Cases**:
- Clean and normalize incoming data
- Filter datasets by criteria
- Date calculations and formatting
- Data standardization pipelines
- ETL workflows

**Dependencies**: None (standard library)

---

## 🌐 Network & Communication

### HTTP Operations (`http`)
**Use for**: API integration, web scraping, external service communication

**Tools Available**: 2 tools
- **http_request**: Make HTTP requests (GET, POST, PUT, DELETE, PATCH)
  - Custom headers and parameters
  - Automatic retries and JSON parsing
  - Comprehensive error handling
- **web_scrape**: Extract content from web pages
  - CSS selector support
  - Link extraction
  - Page metadata

**Common Use Cases**:
- Integrate with REST APIs
- Fetch data from external services
- Web scraping for data collection
- Webhook integrations

**Dependencies**: requests, beautifulsoup4

---

## ⚙️ Workflow Control & Automation

### Execution Control (`execution`)
**Use for**: Workflow orchestration and process coordination

**Tools Available**: 3 tools
- **workflow_wait**: Pause execution for time delays or external events
  - Time-based delays
  - File existence waiting
  - Configurable timeouts
- **execution_data**: Store execution metadata and debugging information
- **sub_workflow**: Execute sub-workflows for modular agent architectures
  - File-based Python script execution
  - Function-based execution
  - Input/output data marshaling

**Common Use Cases**:
- Multi-step workflows with delays
- Process coordination
- Modular agent architectures
- Debugging and monitoring
- Scheduled operations

**Dependencies**: None (standard library)

---

### Code Execution (`code`)
**Use for**: Custom logic and dynamic code execution

**Tools Available**: 2 tools
- **python_code**: Execute Python code with safety restrictions
  - Context variable injection
  - Safe execution environment
  - Stdout/stderr capture
- **javascript_code**: Execute JavaScript code via Node.js
  - NPM module support
  - Context variable injection
  - Error handling

**Common Use Cases**:
- Custom calculations and logic
- Data transformations beyond built-in tools
- Integration with existing code libraries
- Dynamic script execution

**Dependencies**: Node.js required for JavaScript execution

---

## Tool Selection Guide

### By Problem Type

**📊 Data Processing & Analytics**
```bash
braid new data-analyzer --tools transform,csv,files
```
- Use for: ETL pipelines, data cleaning, report generation

**🔗 API Integration & Web Services**  
```bash
braid new api-integrator --tools http,files,transform
```
- Use for: REST API workflows, data fetching, external service integration

**📧 Business Communication**
```bash
braid new business-assistant --tools gworkspace,slack,files
```
- Use for: Email automation, calendar management, team notifications

**🤖 Advanced Automation**
```bash
braid new automation-bot --tools execution,code,http,files
```
- Use for: Complex workflows, custom logic, process orchestration

**📈 Comprehensive Business Agent**
```bash
braid new enterprise-agent --tools gworkspace,slack,transform,http,files,execution
```
- Use for: Full-featured business automation with all capabilities

### Common Tool Combinations

| Use Case | Recommended Tools | Why |
|----------|------------------|-----|
| **Data Pipeline** | `transform,csv,files,http` | ETL + file I/O + API integration |
| **Team Assistant** | `slack,gworkspace,files` | Communication + productivity + storage |
| **Web Scraper** | `http,transform,files,csv` | Scraping + processing + output |
| **Workflow Engine** | `execution,code,http,files` | Control flow + custom logic + I/O |
| **Reporting Bot** | `gworkspace,transform,csv,files` | Data + processing + output to business tools |

### Performance Considerations

- **Lightweight**: `files`, `transform`, `execution` (no external dependencies)
- **Medium**: `http`, `csv`, `code` (minimal dependencies)  
- **Heavy**: `gworkspace`, `slack` (require external service credentials)

---

## Quick Reference Commands

```bash
# List all available tools
braid new my-agent --tools [TAB]  # Shows: gworkspace,slack,files,csv,transform,http,execution,code

# Create agents for common scenarios
braid new data-processor --tools transform,csv,files
braid new api-client --tools http,transform,files  
braid new team-bot --tools slack,gworkspace,files
braid new workflow-engine --tools execution,code,http,files

# Get tool-specific help
braid new test-agent --tools transform  # Then check generated tools/ directory
```

---

## Integration Notes

- **Authentication**: Google Workspace and Slack require proper credentials in `.env`
- **Dependencies**: Run `pip install -r requirements.txt` after agent creation
- **Documentation**: Each tool includes comprehensive docstrings and error messages
- **Safety**: All tools include input validation and error handling
- **Extensibility**: New tools can be added to the organized structure easily

This reference enables intelligent tool selection based on specific use cases and requirements.