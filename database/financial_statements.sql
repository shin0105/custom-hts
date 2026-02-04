-- Enhanced Database schema for Custom HTS
-- This script extends the existing schema with detailed financial statement tables
-- Run this script in your Supabase SQL editor AFTER running the base init.sql

-- ========================================================================
-- BALANCE SHEET TABLES
-- ========================================================================

-- Korean Balance Sheet
CREATE TABLE IF NOT EXISTS korean_balance_sheet (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    report_code VARCHAR(10),
    
    -- Assets
    total_assets NUMERIC(20, 2),
    current_assets NUMERIC(20, 2),
    cash_and_cash_equivalents NUMERIC(20, 2),
    short_term_financial_instruments NUMERIC(20, 2),
    accounts_receivable NUMERIC(20, 2),
    inventory NUMERIC(20, 2),
    other_current_assets NUMERIC(20, 2),
    
    non_current_assets NUMERIC(20, 2),
    long_term_financial_instruments NUMERIC(20, 2),
    property_plant_equipment NUMERIC(20, 2),
    intangible_assets NUMERIC(20, 2),
    investments NUMERIC(20, 2),
    other_non_current_assets NUMERIC(20, 2),
    
    -- Liabilities
    total_liabilities NUMERIC(20, 2),
    current_liabilities NUMERIC(20, 2),
    accounts_payable NUMERIC(20, 2),
    short_term_debt NUMERIC(20, 2),
    other_current_liabilities NUMERIC(20, 2),
    
    non_current_liabilities NUMERIC(20, 2),
    long_term_debt NUMERIC(20, 2),
    other_non_current_liabilities NUMERIC(20, 2),
    
    -- Equity
    total_equity NUMERIC(20, 2),
    paid_in_capital NUMERIC(20, 2),
    retained_earnings NUMERIC(20, 2),
    other_equity NUMERIC(20, 2),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT korean_balance_sheet_unique UNIQUE(symbol, year, quarter)
);

-- US Balance Sheet
CREATE TABLE IF NOT EXISTS us_balance_sheet (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    
    -- Assets
    total_assets NUMERIC(20, 2),
    current_assets NUMERIC(20, 2),
    cash_and_cash_equivalents NUMERIC(20, 2),
    short_term_investments NUMERIC(20, 2),
    receivables NUMERIC(20, 2),
    inventory NUMERIC(20, 2),
    other_current_assets NUMERIC(20, 2),
    
    non_current_assets NUMERIC(20, 2),
    long_term_investments NUMERIC(20, 2),
    property_plant_equipment NUMERIC(20, 2),
    goodwill NUMERIC(20, 2),
    intangible_assets NUMERIC(20, 2),
    other_non_current_assets NUMERIC(20, 2),
    
    -- Liabilities
    total_liabilities NUMERIC(20, 2),
    current_liabilities NUMERIC(20, 2),
    accounts_payable NUMERIC(20, 2),
    short_term_debt NUMERIC(20, 2),
    current_portion_long_term_debt NUMERIC(20, 2),
    other_current_liabilities NUMERIC(20, 2),
    
    non_current_liabilities NUMERIC(20, 2),
    long_term_debt NUMERIC(20, 2),
    deferred_tax_liabilities NUMERIC(20, 2),
    other_non_current_liabilities NUMERIC(20, 2),
    
    -- Equity
    stockholders_equity NUMERIC(20, 2),
    common_stock NUMERIC(20, 2),
    retained_earnings NUMERIC(20, 2),
    treasury_stock NUMERIC(20, 2),
    other_equity NUMERIC(20, 2),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT us_balance_sheet_unique UNIQUE(symbol, year, quarter)
);

-- ========================================================================
-- INCOME STATEMENT TABLES
-- ========================================================================

-- Korean Income Statement
CREATE TABLE IF NOT EXISTS korean_income_statement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    report_code VARCHAR(10),
    
    -- Revenue
    revenue NUMERIC(20, 2),
    cost_of_revenue NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    
    -- Operating
    operating_expenses NUMERIC(20, 2),
    selling_general_admin NUMERIC(20, 2),
    research_development NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    
    -- Non-operating
    non_operating_income NUMERIC(20, 2),
    non_operating_expenses NUMERIC(20, 2),
    financial_income NUMERIC(20, 2),
    financial_expenses NUMERIC(20, 2),
    
    -- Profit
    income_before_tax NUMERIC(20, 2),
    income_tax_expense NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    
    -- Additional metrics
    ebitda NUMERIC(20, 2),
    earnings_per_share NUMERIC(10, 4),
    diluted_eps NUMERIC(10, 4),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT korean_income_statement_unique UNIQUE(symbol, year, quarter)
);

-- US Income Statement
CREATE TABLE IF NOT EXISTS us_income_statement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    
    -- Revenue
    total_revenue NUMERIC(20, 2),
    cost_of_revenue NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    
    -- Operating
    operating_expense NUMERIC(20, 2),
    selling_general_admin NUMERIC(20, 2),
    research_development NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    
    -- Non-operating
    interest_income NUMERIC(20, 2),
    interest_expense NUMERIC(20, 2),
    other_income_expense NUMERIC(20, 2),
    
    -- Profit
    pretax_income NUMERIC(20, 2),
    tax_provision NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    net_income_common_stockholders NUMERIC(20, 2),
    
    -- Additional metrics
    ebitda NUMERIC(20, 2),
    basic_eps NUMERIC(10, 4),
    diluted_eps NUMERIC(10, 4),
    basic_average_shares NUMERIC(20, 2),
    diluted_average_shares NUMERIC(20, 2),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT us_income_statement_unique UNIQUE(symbol, year, quarter)
);

-- ========================================================================
-- CASH FLOW STATEMENT TABLES
-- ========================================================================

-- Korean Cash Flow Statement
CREATE TABLE IF NOT EXISTS korean_cashflow_statement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    report_code VARCHAR(10),
    
    -- Operating Activities
    operating_cash_flow NUMERIC(20, 2),
    net_income_for_cf NUMERIC(20, 2),
    depreciation_amortization NUMERIC(20, 2),
    change_working_capital NUMERIC(20, 2),
    change_accounts_receivable NUMERIC(20, 2),
    change_inventory NUMERIC(20, 2),
    change_accounts_payable NUMERIC(20, 2),
    other_operating_activities NUMERIC(20, 2),
    
    -- Investing Activities
    investing_cash_flow NUMERIC(20, 2),
    capital_expenditure NUMERIC(20, 2),
    acquisition_investments NUMERIC(20, 2),
    sale_of_investments NUMERIC(20, 2),
    other_investing_activities NUMERIC(20, 2),
    
    -- Financing Activities
    financing_cash_flow NUMERIC(20, 2),
    proceeds_debt NUMERIC(20, 2),
    repayment_debt NUMERIC(20, 2),
    proceeds_stock_issuance NUMERIC(20, 2),
    dividends_paid NUMERIC(20, 2),
    stock_repurchase NUMERIC(20, 2),
    other_financing_activities NUMERIC(20, 2),
    
    -- Summary
    net_change_cash NUMERIC(20, 2),
    free_cash_flow NUMERIC(20, 2),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT korean_cashflow_statement_unique UNIQUE(symbol, year, quarter)
);

-- US Cash Flow Statement
CREATE TABLE IF NOT EXISTS us_cashflow_statement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    
    -- Operating Activities
    operating_cash_flow NUMERIC(20, 2),
    net_income_from_continuing_ops NUMERIC(20, 2),
    depreciation_amortization NUMERIC(20, 2),
    deferred_income_tax NUMERIC(20, 2),
    stock_based_compensation NUMERIC(20, 2),
    change_working_capital NUMERIC(20, 2),
    change_receivables NUMERIC(20, 2),
    change_inventory NUMERIC(20, 2),
    change_payables NUMERIC(20, 2),
    other_operating_cash_flows NUMERIC(20, 2),
    
    -- Investing Activities
    investing_cash_flow NUMERIC(20, 2),
    capital_expenditure NUMERIC(20, 2),
    net_intangibles NUMERIC(20, 2),
    net_investment_purchase_sale NUMERIC(20, 2),
    sale_purchase_investment NUMERIC(20, 2),
    other_investing_cash_flows NUMERIC(20, 2),
    
    -- Financing Activities
    financing_cash_flow NUMERIC(20, 2),
    long_term_debt_issuance NUMERIC(20, 2),
    long_term_debt_payments NUMERIC(20, 2),
    short_term_debt_issuance NUMERIC(20, 2),
    common_stock_issuance NUMERIC(20, 2),
    common_stock_payments NUMERIC(20, 2),
    cash_dividends_paid NUMERIC(20, 2),
    repurchase_capital_stock NUMERIC(20, 2),
    other_financing_cash_flows NUMERIC(20, 2),
    
    -- Summary
    net_change_cash NUMERIC(20, 2),
    free_cash_flow NUMERIC(20, 2),
    
    -- Raw data storage for additional fields
    raw_data JSONB,
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT us_cashflow_statement_unique UNIQUE(symbol, year, quarter)
);

-- ========================================================================
-- INDEXES
-- ========================================================================

-- Korean Balance Sheet Indexes
CREATE INDEX IF NOT EXISTS idx_kr_bs_symbol ON korean_balance_sheet(symbol);
CREATE INDEX IF NOT EXISTS idx_kr_bs_year ON korean_balance_sheet(year);
CREATE INDEX IF NOT EXISTS idx_kr_bs_updated ON korean_balance_sheet(updated_at);

-- US Balance Sheet Indexes
CREATE INDEX IF NOT EXISTS idx_us_bs_symbol ON us_balance_sheet(symbol);
CREATE INDEX IF NOT EXISTS idx_us_bs_year ON us_balance_sheet(year);
CREATE INDEX IF NOT EXISTS idx_us_bs_updated ON us_balance_sheet(updated_at);

-- Korean Income Statement Indexes
CREATE INDEX IF NOT EXISTS idx_kr_is_symbol ON korean_income_statement(symbol);
CREATE INDEX IF NOT EXISTS idx_kr_is_year ON korean_income_statement(year);
CREATE INDEX IF NOT EXISTS idx_kr_is_updated ON korean_income_statement(updated_at);

-- US Income Statement Indexes
CREATE INDEX IF NOT EXISTS idx_us_is_symbol ON us_income_statement(symbol);
CREATE INDEX IF NOT EXISTS idx_us_is_year ON us_income_statement(year);
CREATE INDEX IF NOT EXISTS idx_us_is_updated ON us_income_statement(updated_at);

-- Korean Cash Flow Indexes
CREATE INDEX IF NOT EXISTS idx_kr_cf_symbol ON korean_cashflow_statement(symbol);
CREATE INDEX IF NOT EXISTS idx_kr_cf_year ON korean_cashflow_statement(year);
CREATE INDEX IF NOT EXISTS idx_kr_cf_updated ON korean_cashflow_statement(updated_at);

-- US Cash Flow Indexes
CREATE INDEX IF NOT EXISTS idx_us_cf_symbol ON us_cashflow_statement(symbol);
CREATE INDEX IF NOT EXISTS idx_us_cf_year ON us_cashflow_statement(year);
CREATE INDEX IF NOT EXISTS idx_us_cf_updated ON us_cashflow_statement(updated_at);

-- ========================================================================
-- TRIGGERS
-- ========================================================================

-- Korean Balance Sheet Trigger
CREATE TRIGGER update_korean_balance_sheet_updated_at
BEFORE UPDATE ON korean_balance_sheet
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- US Balance Sheet Trigger
CREATE TRIGGER update_us_balance_sheet_updated_at
BEFORE UPDATE ON us_balance_sheet
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Korean Income Statement Trigger
CREATE TRIGGER update_korean_income_statement_updated_at
BEFORE UPDATE ON korean_income_statement
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- US Income Statement Trigger
CREATE TRIGGER update_us_income_statement_updated_at
BEFORE UPDATE ON us_income_statement
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Korean Cash Flow Trigger
CREATE TRIGGER update_korean_cashflow_statement_updated_at
BEFORE UPDATE ON korean_cashflow_statement
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- US Cash Flow Trigger
CREATE TRIGGER update_us_cashflow_statement_updated_at
BEFORE UPDATE ON us_cashflow_statement
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ========================================================================
-- COMMENTS
-- ========================================================================

-- Korean tables
COMMENT ON TABLE korean_balance_sheet IS 'Detailed balance sheet data for Korean companies from OPENDART';
COMMENT ON TABLE korean_income_statement IS 'Detailed income statement data for Korean companies from OPENDART';
COMMENT ON TABLE korean_cashflow_statement IS 'Detailed cash flow statement data for Korean companies from OPENDART';

-- US tables
COMMENT ON TABLE us_balance_sheet IS 'Detailed balance sheet data for US companies from Yahoo Finance';
COMMENT ON TABLE us_income_statement IS 'Detailed income statement data for US companies from Yahoo Finance';
COMMENT ON TABLE us_cashflow_statement IS 'Detailed cash flow statement data for US companies from Yahoo Finance';

-- Column comments
COMMENT ON COLUMN korean_balance_sheet.raw_data IS 'JSONB storage for all additional fields from OPENDART API';
COMMENT ON COLUMN us_balance_sheet.raw_data IS 'JSONB storage for all additional fields from yfinance API';
COMMENT ON COLUMN korean_income_statement.raw_data IS 'JSONB storage for all additional fields from OPENDART API';
COMMENT ON COLUMN us_income_statement.raw_data IS 'JSONB storage for all additional fields from yfinance API';
COMMENT ON COLUMN korean_cashflow_statement.raw_data IS 'JSONB storage for all additional fields from OPENDART API';
COMMENT ON COLUMN us_cashflow_statement.raw_data IS 'JSONB storage for all additional fields from yfinance API';
