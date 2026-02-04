-- Database schema creation script for Custom HTS
-- Run this script in your Supabase SQL editor

-- Create korean_financials table
CREATE TABLE IF NOT EXISTS korean_financials (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    revenue NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    total_equity NUMERIC(20, 2),
    eps NUMERIC(10, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT korean_financials_unique UNIQUE(symbol, year, quarter)
);

-- Create indexes for korean_financials
CREATE INDEX IF NOT EXISTS idx_korean_financials_symbol 
ON korean_financials(symbol);

CREATE INDEX IF NOT EXISTS idx_korean_financials_year 
ON korean_financials(year);

CREATE INDEX IF NOT EXISTS idx_korean_financials_updated 
ON korean_financials(updated_at);

-- Create us_financials table
CREATE TABLE IF NOT EXISTS us_financials (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    revenue NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    total_equity NUMERIC(20, 2),
    eps NUMERIC(10, 4),
    pe_ratio NUMERIC(10, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT us_financials_unique UNIQUE(symbol, year, quarter)
);

-- Create indexes for us_financials
CREATE INDEX IF NOT EXISTS idx_us_financials_symbol 
ON us_financials(symbol);

CREATE INDEX IF NOT EXISTS idx_us_financials_year 
ON us_financials(year);

CREATE INDEX IF NOT EXISTS idx_us_financials_updated 
ON us_financials(updated_at);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to update updated_at on modification
CREATE TRIGGER update_korean_financials_updated_at
BEFORE UPDATE ON korean_financials
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_us_financials_updated_at
BEFORE UPDATE ON us_financials
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE korean_financials IS 'Financial statements for Korean companies from OPENDART';
COMMENT ON TABLE us_financials IS 'Financial statements for US companies from Yahoo Finance';

COMMENT ON COLUMN korean_financials.symbol IS 'Korean stock code (e.g., 005930 for Samsung)';
COMMENT ON COLUMN us_financials.symbol IS 'US stock ticker symbol (e.g., AAPL for Apple)';

-- ========================================================================
-- DETAILED FINANCIAL STATEMENT TABLES
-- ========================================================================
-- For comprehensive financial data, see financial_statements.sql
-- This includes separate tables for:
-- - Balance Sheet (korean_balance_sheet, us_balance_sheet)
-- - Income Statement (korean_income_statement, us_income_statement)  
-- - Cash Flow Statement (korean_cashflow_statement, us_cashflow_statement)
