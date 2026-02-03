# Database Schema for Custom HTS

This document describes the database schema for the Custom HTS application using Supabase PostgreSQL.

## Overview

The database is designed to cache financial data from external APIs to minimize API calls and improve performance. The schema is optimized for the 500MB database size limit.

## Tables

### korean_financials

Stores financial statement data for Korean companies from OPENDART API.

```sql
CREATE TABLE korean_financials (
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
    UNIQUE(symbol, year, quarter)
);

CREATE INDEX idx_korean_financials_symbol ON korean_financials(symbol);
CREATE INDEX idx_korean_financials_year ON korean_financials(year);
```

### us_financials

Stores financial statement data for US companies from Yahoo Finance.

```sql
CREATE TABLE us_financials (
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
    UNIQUE(symbol, year, quarter)
);

CREATE INDEX idx_us_financials_symbol ON us_financials(symbol);
CREATE INDEX idx_us_financials_year ON us_financials(year);
```

## Data Retention Policy

To stay within the 500MB database limit:

1. **Financial Statements**: Keep last 5 years of data
2. **Automatic Cleanup**: Run periodic cleanup jobs to remove old data
3. **Priority**: Keep more recent data and frequently accessed symbols

## Caching Strategy

1. **Cache Duration**: Financial statements cached for 24 hours
2. **Cache Invalidation**: Manual refresh available via API parameter
3. **Cache Miss**: Fetch from external API and store in database

## Usage Monitoring

Monitor database size regularly:

```sql
SELECT 
    pg_size_pretty(pg_database_size('postgres')) as database_size,
    pg_size_pretty(pg_total_relation_size('korean_financials')) as korean_size,
    pg_size_pretty(pg_total_relation_size('us_financials')) as us_size;
```

## Future Enhancements

Potential additions if more storage is needed:

1. **User Watchlists**: Store user-selected stocks
2. **Historical Prices**: Cache daily price data
3. **Price Alerts**: Store user price alert configurations
4. **Market Indices**: Cache major market index data

## File Storage

For large datasets that don't fit in database (using 1GB file storage):

1. **Historical CSV Data**: Store exported financial data
2. **Bulk Imports**: Store uploaded data files
3. **Reports**: Store generated PDF reports

## Backup Strategy

1. **Supabase Backups**: Use built-in backup features
2. **Export Scripts**: Regular exports to CSV for safety
3. **Version Control**: Keep schema in version control
