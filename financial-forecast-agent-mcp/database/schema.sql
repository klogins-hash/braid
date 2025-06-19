-- Financial Forecasting Agent Database Schema
-- SQLite database for storing historical data and forecast results

-- Client information and business context
CREATE TABLE IF NOT EXISTS clients (
    user_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry TEXT,
    business_age INTEGER,
    location TEXT,
    business_strategy TEXT,
    employees INTEGER,
    current_revenue REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historical financial data from Xero MCP
CREATE TABLE IF NOT EXISTS historical_financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    data_source TEXT DEFAULT 'xero_mcp',
    report_type TEXT NOT NULL, -- 'profit_and_loss', 'balance_sheet', 'trial_balance'
    period_start DATE,
    period_end DATE,
    -- P&L line items
    revenue REAL,
    cogs REAL,
    gross_profit REAL,
    operating_expenses REAL,
    ebitda REAL,
    depreciation REAL,
    ebit REAL,
    interest_expense REAL,
    tax_expense REAL,
    net_income REAL,
    -- Balance sheet items (basic)
    total_assets REAL,
    total_liabilities REAL,
    equity REAL,
    -- Raw data storage
    raw_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES clients(user_id)
);

-- Market research and forecast assumptions
CREATE TABLE IF NOT EXISTS forecast_assumptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    forecast_date DATE DEFAULT (date('now')),
    -- Quantitative assumptions
    revenue_growth_rate REAL,
    cogs_percentage REAL,
    opex_growth_rate REAL,
    tax_rate REAL,
    depreciation_rate REAL,
    -- Market context
    market_research TEXT,
    industry_outlook TEXT,
    -- Qualitative assumptions
    qualitative_assumptions JSON,
    risk_factors JSON,
    growth_drivers JSON,
    -- Validation status
    validated BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES clients(user_id)
);

-- Forecast results with annual projections
CREATE TABLE IF NOT EXISTS forecast_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    assumptions_id INTEGER NOT NULL,
    forecast_year INTEGER NOT NULL,
    -- P&L projections
    revenue REAL,
    cogs REAL,
    gross_profit REAL,
    operating_expenses REAL,
    ebitda REAL,
    depreciation REAL,
    ebit REAL,
    interest_expense REAL,
    tax_expense REAL,
    net_income REAL,
    -- Key metrics
    gross_margin REAL,
    ebitda_margin REAL,
    net_margin REAL,
    -- Validation and approval
    validated BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE,
    validation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES clients(user_id),
    FOREIGN KEY (assumptions_id) REFERENCES forecast_assumptions(id)
);

-- Notion reports generated
CREATE TABLE IF NOT EXISTS notion_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    forecast_assumptions_id INTEGER,
    notion_page_id TEXT,
    notion_page_url TEXT,
    report_title TEXT,
    report_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES clients(user_id),
    FOREIGN KEY (forecast_assumptions_id) REFERENCES forecast_assumptions(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_historical_financials_user_id ON historical_financials(user_id);
CREATE INDEX IF NOT EXISTS idx_historical_financials_period ON historical_financials(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_forecast_assumptions_user_id ON forecast_assumptions(user_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_user_id ON forecast_results(user_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_assumptions ON forecast_results(assumptions_id);

-- Sample client data for testing
INSERT OR IGNORE INTO clients (user_id, company_name, industry, business_age, location, business_strategy, employees, current_revenue) VALUES 
('user_123', 'Northeast Logistics Co', 'Software Development', 5, 'San Francisco, CA', 'Aggressive growth through digital transformation', 25, 1000000.0),
('demo_company', 'Demo Tech Solutions', 'Technology Services', 3, 'Boston, MA', 'Market expansion and product development', 15, 750000.0);