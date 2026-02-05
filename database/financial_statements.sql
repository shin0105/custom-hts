-- Enhanced Database schema for Custom HTS with Field Mapping Comments
-- This script extends the existing schema with detailed financial statement tables
-- Run this script in your Supabase SQL editor AFTER running the base init.sql
--
-- IMPORTANT NOTES:
-- - US values (yfinance): Actual USD amounts (e.g., 100000000 = $100M)
-- - Korean values (OPENDART): Millions of KRW (e.g., 100000 = 100B KRW = 100,000 백만원)
-- - All numeric fields use NUMERIC(20, 2) to handle large values and decimal precision
--
-- VERSION: 2.0 - Updated with field mapping comments and corrected units
-- DATE: February 2026

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
    
    -- Assets (단위: 백만원 - Unit: Millions of KRW)
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
    
    -- Liabilities (단위: 백만원 - Unit: Millions of KRW)
    total_liabilities NUMERIC(20, 2),
    current_liabilities NUMERIC(20, 2),
    accounts_payable NUMERIC(20, 2),
    short_term_debt NUMERIC(20, 2),
    other_current_liabilities NUMERIC(20, 2),
    
    non_current_liabilities NUMERIC(20, 2),
    long_term_debt NUMERIC(20, 2),
    other_non_current_liabilities NUMERIC(20, 2),
    
    -- Equity (단위: 백만원 - Unit: Millions of KRW)
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
    
    -- Assets (Unit: USD - Actual dollar amounts)
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
    
    -- Liabilities (Unit: USD - Actual dollar amounts)
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
    
    -- Equity (Unit: USD - Actual dollar amounts)
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
    
    -- Revenue (단위: 백만원 - Unit: Millions of KRW)
    revenue NUMERIC(20, 2),
    cost_of_revenue NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    
    -- Operating (단위: 백만원 - Unit: Millions of KRW)
    operating_expenses NUMERIC(20, 2),
    selling_general_admin NUMERIC(20, 2),
    research_development NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    
    -- Non-operating (단위: 백만원 - Unit: Millions of KRW)
    non_operating_income NUMERIC(20, 2),
    non_operating_expenses NUMERIC(20, 2),
    financial_income NUMERIC(20, 2),
    financial_expenses NUMERIC(20, 2),
    
    -- Profit (단위: 백만원 - Unit: Millions of KRW)
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
    
    -- Revenue (Unit: USD - Actual dollar amounts)
    total_revenue NUMERIC(20, 2),
    cost_of_revenue NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    
    -- Operating (Unit: USD - Actual dollar amounts)
    operating_expense NUMERIC(20, 2),
    selling_general_admin NUMERIC(20, 2),
    research_development NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    
    -- Non-operating (Unit: USD - Actual dollar amounts)
    interest_income NUMERIC(20, 2),
    interest_expense NUMERIC(20, 2),
    other_income_expense NUMERIC(20, 2),
    
    -- Profit (Unit: USD - Actual dollar amounts)
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
    
    -- Operating Activities (단위: 백만원 - Unit: Millions of KRW)
    operating_cash_flow NUMERIC(20, 2),
    net_income_for_cf NUMERIC(20, 2),
    depreciation_amortization NUMERIC(20, 2),
    change_working_capital NUMERIC(20, 2),
    change_accounts_receivable NUMERIC(20, 2),
    change_inventory NUMERIC(20, 2),
    change_accounts_payable NUMERIC(20, 2),
    other_operating_activities NUMERIC(20, 2),
    
    -- Investing Activities (단위: 백만원 - Unit: Millions of KRW)
    investing_cash_flow NUMERIC(20, 2),
    capital_expenditure NUMERIC(20, 2),
    acquisition_investments NUMERIC(20, 2),
    sale_of_investments NUMERIC(20, 2),
    other_investing_activities NUMERIC(20, 2),
    
    -- Financing Activities (단위: 백만원 - Unit: Millions of KRW)
    financing_cash_flow NUMERIC(20, 2),
    proceeds_debt NUMERIC(20, 2),
    repayment_debt NUMERIC(20, 2),
    proceeds_stock_issuance NUMERIC(20, 2),
    dividends_paid NUMERIC(20, 2),
    stock_repurchase NUMERIC(20, 2),
    other_financing_activities NUMERIC(20, 2),
    
    -- Summary (단위: 백만원 - Unit: Millions of KRW)
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
    
    -- Operating Activities (Unit: USD - Actual dollar amounts)
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
    
    -- Investing Activities (Unit: USD - Actual dollar amounts)
    investing_cash_flow NUMERIC(20, 2),
    capital_expenditure NUMERIC(20, 2),
    net_intangibles NUMERIC(20, 2),
    net_investment_purchase_sale NUMERIC(20, 2),
    sale_purchase_investment NUMERIC(20, 2),
    other_investing_cash_flows NUMERIC(20, 2),
    
    -- Financing Activities (Unit: USD - Actual dollar amounts)
    financing_cash_flow NUMERIC(20, 2),
    long_term_debt_issuance NUMERIC(20, 2),
    long_term_debt_payments NUMERIC(20, 2),
    short_term_debt_issuance NUMERIC(20, 2),
    common_stock_issuance NUMERIC(20, 2),
    common_stock_payments NUMERIC(20, 2),
    cash_dividends_paid NUMERIC(20, 2),
    repurchase_capital_stock NUMERIC(20, 2),
    other_financing_cash_flows NUMERIC(20, 2),
    
    -- Summary (Unit: USD - Actual dollar amounts)
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
-- COLUMN COMMENTS - API FIELD MAPPING
-- ========================================================================

-- ========== KOREAN BALANCE SHEET ==========
COMMENT ON TABLE korean_balance_sheet IS 'Balance sheet data from OPENDART API - Values in millions of KRW (백만원)';

-- Assets
COMMENT ON COLUMN korean_balance_sheet.total_assets IS 'OPENDART: 자산총계 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.current_assets IS 'OPENDART: 유동자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.cash_and_cash_equivalents IS 'OPENDART: 현금및현금성자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.short_term_financial_instruments IS 'OPENDART: 단기금융상품 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.accounts_receivable IS 'OPENDART: 매출채권 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.inventory IS 'OPENDART: 재고자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.other_current_assets IS 'OPENDART: 기타유동자산 | Unit: 백만원 (millions KRW)';

COMMENT ON COLUMN korean_balance_sheet.non_current_assets IS 'OPENDART: 비유동자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.long_term_financial_instruments IS 'OPENDART: 장기금융상품 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.property_plant_equipment IS 'OPENDART: 유형자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.intangible_assets IS 'OPENDART: 무형자산 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.investments IS 'OPENDART: 관계기업 및 공동기업 투자 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.other_non_current_assets IS 'OPENDART: 기타비유동자산 | Unit: 백만원 (millions KRW)';

-- Liabilities
COMMENT ON COLUMN korean_balance_sheet.total_liabilities IS 'OPENDART: 부채총계 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.current_liabilities IS 'OPENDART: 유동부채 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.accounts_payable IS 'OPENDART: 매입채무 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.short_term_debt IS 'OPENDART: 단기차입금 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.other_current_liabilities IS 'OPENDART: 기타유동부채 | Unit: 백만원 (millions KRW)';

COMMENT ON COLUMN korean_balance_sheet.non_current_liabilities IS 'OPENDART: 비유동부채 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.long_term_debt IS 'OPENDART: 장기차입금 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.other_non_current_liabilities IS 'OPENDART: 기타비유동부채 | Unit: 백만원 (millions KRW)';

-- Equity
COMMENT ON COLUMN korean_balance_sheet.total_equity IS 'OPENDART: 자본총계 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.paid_in_capital IS 'OPENDART: 자본잉여금 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.retained_earnings IS 'OPENDART: 이익잉여금 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_balance_sheet.other_equity IS 'OPENDART: 기타자본항목 | Unit: 백만원 (millions KRW)';

COMMENT ON COLUMN korean_balance_sheet.raw_data IS 'Full JSONB data from OPENDART API for additional fields';

-- ========== US BALANCE SHEET ==========
COMMENT ON TABLE us_balance_sheet IS 'Balance sheet data from yfinance API - Values in actual USD (not millions)';

-- Assets
COMMENT ON COLUMN us_balance_sheet.total_assets IS 'yfinance: Total Assets | Unit: USD | Example avg: $115B';
COMMENT ON COLUMN us_balance_sheet.current_assets IS 'yfinance: Current Assets | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.cash_and_cash_equivalents IS 'yfinance: Cash And Cash Equivalents | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.short_term_investments IS 'yfinance: Other Short Term Investments | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.receivables IS 'yfinance: Receivables | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.inventory IS 'yfinance: Inventory | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.other_current_assets IS 'yfinance: Other Current Assets | Unit: USD';

COMMENT ON COLUMN us_balance_sheet.non_current_assets IS 'yfinance: Total Non Current Assets | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.long_term_investments IS 'yfinance: Long Term Investments | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.property_plant_equipment IS 'yfinance: Net PPE | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.goodwill IS 'yfinance: Goodwill | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.intangible_assets IS 'yfinance: Other Intangible Assets | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.other_non_current_assets IS 'yfinance: Other Non Current Assets | Unit: USD';

-- Liabilities
COMMENT ON COLUMN us_balance_sheet.total_liabilities IS 'yfinance: Total Liabilities Net Minority Interest | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.current_liabilities IS 'yfinance: Current Liabilities | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.accounts_payable IS 'yfinance: Accounts Payable | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.short_term_debt IS 'yfinance: Current Debt | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.current_portion_long_term_debt IS 'yfinance: Current Portion Long Term Debt | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.other_current_liabilities IS 'yfinance: Other Current Liabilities | Unit: USD';

COMMENT ON COLUMN us_balance_sheet.non_current_liabilities IS 'yfinance: Total Non Current Liabilities Net Minority Interest | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.long_term_debt IS 'yfinance: Long Term Debt | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.deferred_tax_liabilities IS 'yfinance: Deferred Tax Liabilities | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.other_non_current_liabilities IS 'yfinance: Other Non Current Liabilities | Unit: USD';

-- Equity
COMMENT ON COLUMN us_balance_sheet.stockholders_equity IS 'yfinance: Stockholders Equity | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.common_stock IS 'yfinance: Common Stock | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.retained_earnings IS 'yfinance: Retained Earnings | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.treasury_stock IS 'yfinance: Treasury Stock | Unit: USD';
COMMENT ON COLUMN us_balance_sheet.other_equity IS 'yfinance: Other Equity Adjustments | Unit: USD';

COMMENT ON COLUMN us_balance_sheet.raw_data IS 'Full JSONB data from yfinance API for additional fields';

-- ========== KOREAN INCOME STATEMENT ==========
COMMENT ON TABLE korean_income_statement IS 'Income statement data from OPENDART API - Values in millions of KRW (백만원)';

-- Revenue
COMMENT ON COLUMN korean_income_statement.revenue IS 'OPENDART: 매출액 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.cost_of_revenue IS 'OPENDART: 매출원가 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.gross_profit IS 'OPENDART: 매출총이익 | Unit: 백만원 (millions KRW)';

-- Operating
COMMENT ON COLUMN korean_income_statement.operating_expenses IS 'OPENDART: 판매비와관리비 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.selling_general_admin IS 'OPENDART: 판매비와관리비 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.research_development IS 'OPENDART: Research & Development (from 판매비와관리비) | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.operating_income IS 'OPENDART: 영업이익 | Unit: 백만원 (millions KRW)';

-- Non-operating
COMMENT ON COLUMN korean_income_statement.non_operating_income IS 'OPENDART: 기타이익 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.non_operating_expenses IS 'OPENDART: 기타비용 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.financial_income IS 'OPENDART: 금융수익 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.financial_expenses IS 'OPENDART: 금융비용 | Unit: 백만원 (millions KRW)';

-- Profit
COMMENT ON COLUMN korean_income_statement.income_before_tax IS 'OPENDART: 법인세비용차감전순이익 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.income_tax_expense IS 'OPENDART: 법인세비용 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.net_income IS 'OPENDART: 당기순이익 or 연결당기순이익 | Unit: 백만원 (millions KRW)';

-- Additional metrics
COMMENT ON COLUMN korean_income_statement.ebitda IS 'Calculated: EBITDA | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_income_statement.earnings_per_share IS 'OPENDART: 보통주기본주당이익(손실) | Unit: KRW per share';
COMMENT ON COLUMN korean_income_statement.diluted_eps IS 'OPENDART: 보통주희석주당이익 | Unit: KRW per share';

COMMENT ON COLUMN korean_income_statement.raw_data IS 'Full JSONB data from OPENDART API for additional fields';

-- ========== US INCOME STATEMENT ==========
COMMENT ON TABLE us_income_statement IS 'Income statement data from yfinance API - Values in actual USD (not millions)';

-- Revenue
COMMENT ON COLUMN us_income_statement.total_revenue IS 'yfinance: Total Revenue | Unit: USD | Example avg: $41B';
COMMENT ON COLUMN us_income_statement.cost_of_revenue IS 'yfinance: Cost Of Revenue | Unit: USD';
COMMENT ON COLUMN us_income_statement.gross_profit IS 'yfinance: Gross Profit | Unit: USD';

-- Operating
COMMENT ON COLUMN us_income_statement.operating_expense IS 'yfinance: Operating Expense | Unit: USD';
COMMENT ON COLUMN us_income_statement.selling_general_admin IS 'yfinance: Selling General And Administration | Unit: USD';
COMMENT ON COLUMN us_income_statement.research_development IS 'yfinance: Research And Development | Unit: USD';
COMMENT ON COLUMN us_income_statement.operating_income IS 'yfinance: Operating Income | Unit: USD';

-- Non-operating
COMMENT ON COLUMN us_income_statement.interest_income IS 'yfinance: Interest Income | Unit: USD';
COMMENT ON COLUMN us_income_statement.interest_expense IS 'yfinance: Interest Expense | Unit: USD';
COMMENT ON COLUMN us_income_statement.other_income_expense IS 'yfinance: Other Income Expense | Unit: USD';

-- Profit
COMMENT ON COLUMN us_income_statement.pretax_income IS 'yfinance: Pretax Income | Unit: USD';
COMMENT ON COLUMN us_income_statement.tax_provision IS 'yfinance: Tax Provision | Unit: USD';
COMMENT ON COLUMN us_income_statement.net_income IS 'yfinance: Net Income | Unit: USD';
COMMENT ON COLUMN us_income_statement.net_income_common_stockholders IS 'yfinance: Net Income Common Stockholders | Unit: USD';

-- Additional metrics
COMMENT ON COLUMN us_income_statement.ebitda IS 'yfinance: EBITDA | Unit: USD';
COMMENT ON COLUMN us_income_statement.basic_eps IS 'yfinance: Basic EPS | Unit: USD per share';
COMMENT ON COLUMN us_income_statement.diluted_eps IS 'yfinance: Diluted EPS | Unit: USD per share';
COMMENT ON COLUMN us_income_statement.basic_average_shares IS 'yfinance: Basic Average Shares | Unit: shares';
COMMENT ON COLUMN us_income_statement.diluted_average_shares IS 'yfinance: Diluted Average Shares | Unit: shares';

COMMENT ON COLUMN us_income_statement.raw_data IS 'Full JSONB data from yfinance API for additional fields';

-- ========== KOREAN CASH FLOW STATEMENT ==========
COMMENT ON TABLE korean_cashflow_statement IS 'Cash flow statement data from OPENDART API - Values in millions of KRW (백만원)';

-- Operating Activities
COMMENT ON COLUMN korean_cashflow_statement.operating_cash_flow IS 'OPENDART: 영업활동현금흐름 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.net_income_for_cf IS 'OPENDART: 당기순이익 (for cash flow) | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.depreciation_amortization IS 'OPENDART: Depreciation/Amortization (from 조정) | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.change_working_capital IS 'OPENDART: 영업활동으로 인한 자산부채의 변동 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.change_accounts_receivable IS 'OPENDART: Accounts receivable changes | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.change_inventory IS 'OPENDART: Inventory changes | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.change_accounts_payable IS 'OPENDART: Accounts payable changes | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.other_operating_activities IS 'OPENDART: Other operating activities | Unit: 백만원 (millions KRW)';

-- Investing Activities
COMMENT ON COLUMN korean_cashflow_statement.investing_cash_flow IS 'OPENDART: 투자활동현금흐름 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.capital_expenditure IS 'OPENDART: 유형자산의 취득 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.acquisition_investments IS 'OPENDART: Investment acquisitions | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.sale_of_investments IS 'OPENDART: Investment sales | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.other_investing_activities IS 'OPENDART: Other investing activities | Unit: 백만원 (millions KRW)';

-- Financing Activities
COMMENT ON COLUMN korean_cashflow_statement.financing_cash_flow IS 'OPENDART: 재무활동현금흐름 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.proceeds_debt IS 'OPENDART: 장기차입금 및 사채의 차입 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.repayment_debt IS 'OPENDART: 장기차입금 및 사채의 상환 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.proceeds_stock_issuance IS 'OPENDART: Stock issuance proceeds | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.dividends_paid IS 'OPENDART: 배당금의지급 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.stock_repurchase IS 'OPENDART: 자기주식의 취득 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.other_financing_activities IS 'OPENDART: Other financing activities | Unit: 백만원 (millions KRW)';

-- Summary
COMMENT ON COLUMN korean_cashflow_statement.net_change_cash IS 'OPENDART: 현금및현금성자산의 증감 | Unit: 백만원 (millions KRW)';
COMMENT ON COLUMN korean_cashflow_statement.free_cash_flow IS 'Calculated: Free Cash Flow (Operating CF - Capex) | Unit: 백만원 (millions KRW)';

COMMENT ON COLUMN korean_cashflow_statement.raw_data IS 'Full JSONB data from OPENDART API for additional fields';

-- ========== US CASH FLOW STATEMENT ==========
COMMENT ON TABLE us_cashflow_statement IS 'Cash flow statement data from yfinance API - Values in actual USD (not millions)';

-- Operating Activities
COMMENT ON COLUMN us_cashflow_statement.operating_cash_flow IS 'yfinance: Operating Cash Flow | Unit: USD | Example avg: $10B';
COMMENT ON COLUMN us_cashflow_statement.net_income_from_continuing_ops IS 'yfinance: Net Income From Continuing Operations | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.depreciation_amortization IS 'yfinance: Depreciation And Amortization | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.deferred_income_tax IS 'yfinance: Deferred Income Tax | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.stock_based_compensation IS 'yfinance: Stock Based Compensation | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.change_working_capital IS 'yfinance: Change In Working Capital | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.change_receivables IS 'yfinance: Change In Receivables | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.change_inventory IS 'yfinance: Change In Inventory | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.change_payables IS 'yfinance: Change In Payables And Accrued Expense | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.other_operating_cash_flows IS 'yfinance: Other Operating Cash Flows | Unit: USD';

-- Investing Activities
COMMENT ON COLUMN us_cashflow_statement.investing_cash_flow IS 'yfinance: Investing Cash Flow | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.capital_expenditure IS 'yfinance: Capital Expenditure | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.net_intangibles IS 'yfinance: Net Intangibles Purchase And Sale | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.net_investment_purchase_sale IS 'yfinance: Net Investment Purchase And Sale | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.sale_purchase_investment IS 'yfinance: Sale Purchase Investment | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.other_investing_cash_flows IS 'yfinance: Other Investing Cash Flows | Unit: USD';

-- Financing Activities
COMMENT ON COLUMN us_cashflow_statement.financing_cash_flow IS 'yfinance: Financing Cash Flow | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.long_term_debt_issuance IS 'yfinance: Long Term Debt Issuance | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.long_term_debt_payments IS 'yfinance: Long Term Debt Payments | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.short_term_debt_issuance IS 'yfinance: Short Term Debt Issuance | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.common_stock_issuance IS 'yfinance: Common Stock Issuance | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.common_stock_payments IS 'yfinance: Common Stock Payments | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.cash_dividends_paid IS 'yfinance: Cash Dividends Paid | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.repurchase_capital_stock IS 'yfinance: Repurchase Of Capital Stock | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.other_financing_cash_flows IS 'yfinance: Other Financing Cash Flows | Unit: USD';

-- Summary
COMMENT ON COLUMN us_cashflow_statement.net_change_cash IS 'yfinance: Changes In Cash | Unit: USD';
COMMENT ON COLUMN us_cashflow_statement.free_cash_flow IS 'yfinance: Free Cash Flow | Unit: USD';

COMMENT ON COLUMN us_cashflow_statement.raw_data IS 'Full JSONB data from yfinance API for additional fields';
