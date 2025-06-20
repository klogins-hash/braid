# Financial Forecast Agent

A LangGraph-based agent for generating financial forecasts using Xero data, market research, and automated reporting.

## Overview

This agent performs a 6-step workflow to create comprehensive financial forecasts:

1. Retrieves historical financial data from Xero
2. Gets client business information from database
3. Conducts market research using Perplexity
4. Generates forecast assumptions
5. Calculates 5-year financial projections
6. Creates detailed report in Notion

## Setup

1. Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd cursor-xero-test
pip install -r requirements.txt
```

2. Create a `.env` file with required API keys:
```env
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Xero
XERO_CLIENT_ID=your_xero_client_id_here
XERO_CLIENT_SECRET=your_xero_client_secret_here
XERO_ACCESS_TOKEN=your_xero_access_token_here

# Notion
NOTION_API_KEY=your_notion_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Perplexity
PERPLEXITY_API_KEY=your_perplexity_key_here

# Database
DATABASE_URL=sqlite:///./financial_forecast.db  # For development
```

3. Initialize the database:
```python
from src.database.database import init_db
init_db()
```

## Usage

```python
from src.agent import FinancialForecastAgent

# Create agent instance
agent = FinancialForecastAgent()

# Run forecast for a user
result = agent.run_forecast(user_id="user_123")

# Access results
print(f"Forecast complete! View the report at: {result['notion_report_url']}")
```

## Project Structure

```
cursor-xero-test/
├── src/
│   ├── database/
│   │   ├── models.py      # SQLAlchemy models
│   │   └── database.py    # Database operations
│   ├── tools/
│   │   ├── xero_tools.py        # Xero API integration
│   │   ├── perplexity_tools.py  # Market research
│   │   ├── notion_tools.py      # Report creation
│   │   └── forecast_tools.py    # Financial calculations
│   ├── agent.py          # Main LangGraph agent
│   └── types.py          # Type definitions
├── tests/
│   ├── test_tools.py
│   └── test_agent.py
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Development

- The agent uses LangGraph for workflow orchestration
- Mock data is provided when API keys are not configured
- SQLite is used for development; configure production database as needed
- All API integrations include error handling and logging

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 


In a new folder: ‘Claude agent test’: We need  a tool that allowed users to perform dynamic financial forecasting using their data from Xero software that was forecasted based on information provided by the user, that existed within their account, and third-party market research. 

Lastly, this response needed to be in a format compatible with our python forecasting tools for validation and create a feedback loop so the agent could utilize a three-statement model to get iterative feedback without using compute for basic calculations like EBITDA. We also need to use LangGraph for traceability.

Therefore, we need an agent to follow the following sequence:

1. Will retrieve the necessary information from Xero tool for the YTD Profit Loss in order to perform the financial analysis and store this into our SQL database as historical values.

2. Will pull ‘client information’ including fields for ‘what the client does’ (E.g. their industry, business age, location, and business strategy over the forecast period) from the SQL database associated with the user ID.

3. Will use the Perplexity tool to perform a single search on the outlook of the given industry based on the industry and location (E.g. last mile logistics in the Northeast)

4. Will generate set of simple qualitative and quantitative assumptions for the basis of the forecast for annual growth rate of revenue, expenses with granularity depending on the data returned from Xero.

5. Will place these assumptions into our ‘financial statement forecaster’ which will use basic python code to calculate the forecasted P&L annually over the next five years based on the assumptions and return the bottom line metrics back to the agent to review and approve or revise the qualitative assumptions.

6. Create an ‘Annual Financial Forecast’ report in a Notion page which includes a table of the historical and forecasted values, along with a summary of the methodology and bulleted list of key assumptions along with a summary of the market research report. 

First, before we do this, we will need to build a ‘Forecast Agent’ toolkit for the purposes of this which will include a mock SQL database we will later replace with our live one to read/write the data to, along with a very simple forecast P&L tool for step 5. Please first make a plan before and then we will go step by step.  Also, all the .env variables you need for this (E.g. Xero, Notion, OpenAI, Perplexity) should be in the .env file in the root. 


