-- Add korean_financials summary table for caching simplified financial data
-- This table provides a simplified view of financial statements
-- Unit: Millions of KRW (백만원)

CREATE TABLE IF NOT EXISTS korean_financials (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    
    -- Income Statement items (단위: 백만원)
    revenue NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    
    -- Balance Sheet items (단위: 백만원)
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    total_equity NUMERIC(20, 2),
    
    -- Per share metrics
    eps NUMERIC(10, 2),
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT korean_financials_unique UNIQUE(symbol, year, quarter)
);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_korean_financials_symbol ON korean_financials(symbol);
CREATE INDEX IF NOT EXISTS idx_korean_financials_year ON korean_financials(year);

-- Add similar table for US market
CREATE TABLE IF NOT EXISTS us_financials (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    
    -- Income Statement items (Unit: USD - actual amounts)
    revenue NUMERIC(20, 2),
    operating_income NUMERIC(20, 2),
    net_income NUMERIC(20, 2),
    
    -- Balance Sheet items (Unit: USD - actual amounts)
    total_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    total_equity NUMERIC(20, 2),
    
    -- Per share metrics
    eps NUMERIC(10, 2),
    
    -- Metadata
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT us_financials_unique UNIQUE(symbol, year, quarter)
);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_us_financials_symbol ON us_financials(symbol);
CREATE INDEX IF NOT EXISTS idx_us_financials_year ON us_financials(year);
