# Agent Requirements Template

## Core Tasks and Sequences of Agent

**Description**: Create a Sales Intelligence Agent that automates daily sales insights and team coordination.

**Your Requirements**: 
The agent should run every weekday morning and:

1. **Data Collection Phase**:
   - Fetch overnight CRM data from our REST API (new leads, deal updates, customer interactions)
   - Scrape competitor pricing from 3 competitor websites
   - Pull yesterday's website analytics from our analytics API

2. **Data Processing Phase**:
   - Clean and normalize the CRM data (standardize field names, filter relevant deals)
   - Calculate daily metrics: new leads count, deal progression, revenue pipeline changes
   - Analyze competitor pricing trends and identify significant changes
   - Generate priority lead scores based on engagement data

3. **Intelligence Generation Phase**:
   - Create a daily sales intelligence report with:
     - Top 5 hottest leads requiring immediate attention
     - Competitor pricing alerts (if changes > 5%)
     - Pipeline health summary with visual trends
     - Action items for each sales rep based on their deals

4. **Distribution Phase**:
   - Post executive summary to #sales-leadership Slack channel
   - Send personalized updates to individual sales reps via DM
   - Update the "Daily Sales Dashboard" Google Sheet with metrics
   - Store detailed report as CSV for historical analysis
   - Schedule follow-up reminders for high-priority leads

**Example Workflow**: Every weekday at 8 AM, fetch CRM data → process and analyze → generate insights → post "#sales-leadership: 🔥 5 hot leads, 2 competitor price drops, $50K pipeline added" → send personalized DMs → update dashboard → schedule follow-ups.

## Tools Agent Should Use

**📋 Complete Tool Reference**: See [TOOL_REFERENCE.md](./TOOL_REFERENCE.md) for detailed documentation of all available tools.

**Your Required Tools**: 

Based on the requirements analysis:

- **http**: Fetch CRM data, analytics data, scrape competitor websites
- **transform**: Clean CRM data, calculate metrics, normalize fields, generate scores  
- **slack**: Post to #sales-leadership, send personalized DMs, schedule reminders
- **gworkspace**: Update Google Sheets dashboard with daily metrics
- **files**: Store daily reports, maintain historical data, log processing
- **execution**: Schedule daily workflow, coordinate multi-step process, handle delays
- **csv**: Process CRM exports, generate historical analysis files

**Rationale**: This is a "Comprehensive Business Agent" pattern requiring data integration (http), processing (transform), communication (slack), business tools (gworkspace), storage (files), workflow control (execution), and structured data handling (csv).

## Preventative Rules Agent to Follow

**Safety and Confirmation Rules**: 

1. **Data Sensitivity**: Never post individual customer details or deal amounts in public channels - only aggregated metrics
2. **API Rate Limits**: Wait 2 seconds between competitor website scraping requests to avoid being blocked
3. **Pricing Alerts**: Only alert on competitor price changes > 5% to avoid noise
4. **Lead Scoring**: Confirm lead scores above 90 with sales manager before flagging as "immediate attention"
5. **Error Handling**: If any data source fails, continue with available data and note missing sources in report
6. **Personal DMs**: Only send personalized updates to reps who have deals in the pipeline
7. **Sheet Updates**: Always backup existing Google Sheet data before writing new metrics

## Technical Configuration Requirements

### Environment Variables Needed:
- OPENAI_API_KEY (required)
- SLACK_BOT_TOKEN (for posting to channels)
- SLACK_USER_TOKEN (for DMs and user lookup)
- GOOGLE_CREDENTIALS_PATH (for Sheets access)
- CRM_API_KEY (for customer data)
- ANALYTICS_API_KEY (for website metrics)
- SALES_MANAGER_SLACK_ID (for lead score confirmations)

### Expected Output Format:
- **Slack Messages**: Formatted with emojis, bullet points, and mentions
- **Google Sheets**: Structured data with date, metrics, trends
- **CSV Reports**: Historical data with timestamps and source attribution
- **DMs**: Personalized bullet points with action items

### Error Handling Preferences:
- **API Failures**: Continue workflow with partial data, log failures
- **Data Quality Issues**: Flag anomalies but don't stop processing
- **Rate Limiting**: Implement exponential backoff with 5 retry attempts
- **Sheet Access**: Graceful degradation if Google Sheets unavailable

## Success Criteria

**How to measure if the agent is working correctly**:
- Daily sales intelligence report posted to Slack every weekday by 8:30 AM
- Google Sheets dashboard updated with accurate metrics within 15 minutes
- Sales reps receive personalized DMs with relevant action items
- Competitor price alerts triggered only for significant changes (>5%)
- Historical CSV data maintained with 100% data integrity
- Zero false positive on "immediate attention" leads
- Average processing time under 10 minutes for complete workflow

## Testing Scenarios

**Test Case 1**: Normal daily run with all data sources available
- Expected: Complete workflow execution, all channels updated, personalized DMs sent
- Validation: Check Slack posts, Google Sheets updates, CSV file creation

**Test Case 2**: CRM API down, other sources available  
- Expected: Workflow continues with analytics and competitor data, notes missing CRM data
- Validation: Partial report posted with clear indication of missing data source

**Test Case 3**: High-priority lead detected (score > 90)
- Expected: Sales manager confirmation requested before flagging as immediate attention
- Validation: Check for confirmation DM to sales manager, delayed public posting

**Test Case 4**: Competitor price change of 8% detected
- Expected: Price alert included in daily report and separate urgent notification
- Validation: Alert appears in leadership channel with specific pricing details

**Test Case 5**: Weekend execution attempt
- Expected: Agent recognizes non-weekday and skips execution
- Validation: No messages posted, execution log shows "weekend skip"

---

**Note for Cursor/AI Development Tools**: This template provides structured requirements for creating LangGraph agents using the Braid toolkit. 

**Tool Selection Process**:
1. Review the user requirements in "Core Tasks and Sequences"
2. Consult [TOOL_REFERENCE.md](./TOOL_REFERENCE.md) to understand available capabilities
3. Select optimal tool combination based on the task requirements
4. Use `braid new <agent-name> --tools <tool-list>` to scaffold the agent structure
5. Customize the agent.py file with the specific logic described above

**Example Command**: `braid new sales-intelligence-agent --tools http,transform,slack,gworkspace,files,execution,csv`