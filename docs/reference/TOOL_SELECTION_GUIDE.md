# Tool Selection Guide

Quick decision guide for choosing the optimal tool combination based on user requirements and problem types.

## 🎯 Quick Decision Tree

### Step 1: Identify Primary Problem Category

| User Says... | Problem Category | Go To |
|--------------|------------------|-------|
| "Process data", "analyze files", "clean data" | **Data Processing** | [Data Workflows](#data-workflows) |
| "Send emails", "calendar", "Slack notifications" | **Business Communication** | [Communication Workflows](#communication-workflows) |
| "Call API", "fetch data", "scrape website" | **External Integration** | [Integration Workflows](#integration-workflows) |
| "Multi-step process", "if-then logic", "scheduled tasks" | **Complex Automation** | [Automation Workflows](#automation-workflows) |

### Step 2: Select Tools by Workflow Type

---

## 📊 Data Workflows

### Data Processing & ETL
**Indicators**: "clean data", "transform", "filter", "sort", "CSV", "Excel", "reports"

**Core Tools**: `transform,csv,files`
```bash
braid new data-processor --tools transform,csv,files
```

**Add If Needed**:
- `+http` → if fetching data from APIs
- `+gworkspace` → if working with Google Sheets
- `+execution` → if multi-step processing with delays

**Examples**:
- "Clean CSV files and generate reports" → `transform,csv,files`
- "Fetch API data and process into spreadsheets" → `transform,csv,files,http,gworkspace`
- "Daily data pipeline with scheduled processing" → `transform,csv,files,http,execution`

---

## 📞 Communication Workflows

### Team Notifications & Business Integration
**Indicators**: "send email", "Slack message", "calendar", "notify team", "schedule"

**Core Tools**: `gworkspace,slack,files`
```bash
braid new team-assistant --tools gworkspace,slack,files
```

**Add If Needed**:
- `+http` → if integrating external data sources
- `+transform` → if processing data before sending
- `+execution` → if scheduled notifications

**Examples**:
- "Send daily reports to Slack" → `gworkspace,slack,files`
- "Calendar-based notifications with API data" → `gworkspace,slack,http,transform`
- "Scheduled team updates" → `gworkspace,slack,files,execution`

---

## 🔗 Integration Workflows

### API Integration & Web Services
**Indicators**: "API", "REST", "webhook", "external service", "scrape", "fetch data"

**Core Tools**: `http,files`
```bash
braid new api-client --tools http,files
```

**Add If Needed**:
- `+transform` → if processing API responses
- `+gworkspace/slack` → if sending results to business tools
- `+execution` → if coordinating multiple API calls
- `+code` → if custom processing logic needed

**Examples**:
- "Fetch weather data and save to file" → `http,files`
- "API integration with data processing" → `http,transform,files`
- "Web scraping with team notifications" → `http,transform,slack,files`

---

## ⚙️ Automation Workflows

### Complex Multi-Step Processes
**Indicators**: "workflow", "if-then", "conditional", "wait for", "schedule", "multi-step", "orchestrate"

**Core Tools**: `execution,files`
```bash
braid new workflow-engine --tools execution,files
```

**Add If Needed**:
- `+code` → if custom logic or calculations
- `+http` → if calling external services
- `+transform` → if data processing steps
- `+gworkspace/slack` → if business integration

**Examples**:
- "Wait for file, process, then notify" → `execution,transform,files,slack`
- "Complex business workflow with approvals" → `execution,code,http,gworkspace,slack`
- "Scheduled data pipeline with multiple steps" → `execution,http,transform,csv,files`

---

## 🎛️ Tool Combination Patterns

### Common Successful Combinations

| Pattern Name | Tools | Use Case | Example |
|--------------|-------|----------|---------|
| **Data Pipeline** | `transform,csv,files,http` | ETL workflows | Daily sales report generation |
| **Business Assistant** | `gworkspace,slack,files` | Team automation | Meeting summaries and notifications |
| **API Processor** | `http,transform,files` | External data integration | Weather alerts with processing |
| **Workflow Engine** | `execution,code,http,files` | Complex automation | Multi-step approval processes |
| **Communication Hub** | `slack,gworkspace,http,transform` | Team data sharing | API data → processed → shared |
| **File Processor** | `files,transform,csv` | Local data work | Batch file processing |
| **Web Scraper** | `http,transform,files,csv` | Data collection | Competitive analysis automation |
| **Enterprise Suite** | `gworkspace,slack,http,transform,files,execution` | Full automation | Complete business workflows |

---

## 🚨 Decision Criteria

### When to Include Each Tool

**Always Consider**:
- `files` → Almost every agent needs file I/O for logs, outputs, configs
- `transform` → Any data manipulation beyond basic operations

**Include Based on Requirements**:

| Tool | Include When User Mentions... |
|------|-------------------------------|
| `gworkspace` | Gmail, Calendar, Google Sheets, Drive, "email", "schedule" |
| `slack` | Slack, "notify team", "send message", "team communication" |
| `csv` | CSV files, spreadsheets, tabular data, "Excel", "data analysis" |
| `http` | API, REST, webhook, "fetch data", "external service", "scrape" |
| `execution` | "wait for", "schedule", "multi-step", "if-then", "workflow" |
| `code` | "custom logic", "calculation", "JavaScript", "Python", "script" |

**Tool Dependencies**:
- `csv` often pairs with `transform` for data processing
- `http` often pairs with `files` for storing responses
- `execution` often pairs with multiple tools for orchestration
- `gworkspace`/`slack` often pair with `files` for attachments

---

## 📝 Selection Examples

### Example 1: "Create a daily report that fetches sales data from our API, processes it, and emails it to the team"

**Analysis**:
- Fetch data → `http`
- Process data → `transform`  
- Email team → `gworkspace`
- Save report → `files`
- Daily schedule → `execution`

**Recommendation**: `http,transform,gworkspace,files,execution`

### Example 2: "Monitor a folder for new CSV files, clean the data, and post summaries to Slack"

**Analysis**:
- Monitor folder → `execution` (wait for files)
- CSV processing → `csv,transform`
- Post to Slack → `slack`
- File operations → `files`

**Recommendation**: `execution,csv,transform,slack,files`

### Example 3: "Scrape competitor pricing, analyze trends, and update our Google Sheet"

**Analysis**:
- Web scraping → `http`
- Analyze trends → `transform`
- Update Google Sheet → `gworkspace`
- Store data → `files`

**Recommendation**: `http,transform,gworkspace,files`

---

## ⚡ Quick Commands Reference

```bash
# Data Processing
braid new data-pipeline --tools transform,csv,files,http

# Business Communication  
braid new team-bot --tools gworkspace,slack,files

# API Integration
braid new api-client --tools http,transform,files

# Complex Automation
braid new workflow-engine --tools execution,code,http,files

# Comprehensive Agent
braid new enterprise-agent --tools gworkspace,slack,http,transform,csv,files,execution

# Lightweight Processing
braid new simple-processor --tools transform,files

# Web Operations
braid new web-agent --tools http,transform,files,csv
```

This guide ensures optimal tool selection for any user requirement!