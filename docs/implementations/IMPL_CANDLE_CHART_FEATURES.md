# Implementation: Candle Chart and Financial Statement Features

## Overview
This document describes the implementation of candle chart functionality and enhanced financial statements display for both Korean and US markets in the Custom HTS application.

## Issue Reference
This implementation addresses the requirements to:
1. Add DAY filter for both Korean/US markets
2. Show financial statements using OpenDart API backend for Korean stocks
3. Show candle chart with options to choose daily/minute intervals

## Implementation Date
February 6, 2026

## Changes Made

### 1. Database Schema Updates

**File Created:** `database/add_korean_financials_table.sql`

Added two new tables to support simplified financial data caching:

```sql
-- korean_financials: Summary table for Korean financial data
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

-- us_financials: Summary table for US financial data
CREATE TABLE IF NOT EXISTS us_financials (
    -- Similar structure for US market data
);
```

**Note:** These tables need to be created in your Supabase database by running the SQL script in the Supabase SQL editor.

### 2. Backend Changes

#### Korean Market (OpenDart API)

**File Modified:** `backend/src/integrations/opendart.py`

- Updated `_load_common_corp_codes()` to automatically download full corp code list from OpenDart on initialization
- Added automatic fallback to hardcoded mapping if download fails
- This fixes the issue where corp codes for stocks like 300120 were not found

```python
def _load_common_corp_codes(self) -> None:
    # ... existing hardcoded mappings ...
    
    # Try to download full corp code list on initialization
    try:
        self.download_corp_code_list()
    except Exception as e:
        logger.warning(f"Could not download full corp code list: {e}. Using hardcoded mapping.")
```

**Existing APIs Used:**
- `GET /api/korean/candle/{symbol}` - Daily/weekly/monthly candles
- `GET /api/korean/candle-minute/{symbol}` - Minute-level candles
- `GET /api/korean/financials/{symbol}` - Financial statements

#### US Market (Yahoo Finance)

**Files Modified:**
- `backend/src/models/us.py` - Added `USCandleData` model
- `backend/src/integrations/yfinance_client.py` - Added `get_historical_data()` method
- `backend/src/services/us_market.py` - Added `get_historical_data()` service method
- `backend/src/api/us.py` - Added `GET /api/us/candle/{symbol}` endpoint

**New API Endpoint:**
```python
GET /api/us/candle/{symbol}
Query Parameters:
  - period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
  - interval: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
  - start: Optional start date (YYYY-MM-DD)
  - end: Optional end date (YYYY-MM-DD)
```

The yfinance client now supports fetching historical OHLCV data with flexible period and interval options:

```python
def get_historical_data(
    self,
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Optional[List[USCandleData]]:
    """Get historical OHLCV data for a US stock."""
    ticker = yf.Ticker(symbol)
    
    if start and end:
        hist = ticker.history(start=start, end=end, interval=interval)
    else:
        hist = ticker.history(period=period, interval=interval)
    
    # Process and return candle data
    # ...
```

### 3. Frontend Changes

#### Shared Components

**File Created:** `frontend/src/components/CandleChart.tsx`

Created a reusable candle chart component using recharts library:

**Features:**
- Displays price lines (close, high, low) with different colors
- Volume bars at the bottom with color-coding (green for up days, red for down days)
- Custom tooltip showing OHLCV data and price changes
- Responsive design with proper formatting for USD and KRW currencies
- Automatic date formatting based on data granularity

**Usage:**
```tsx
<CandleChart 
  data={candleData} 
  currency="KRW" // or "USD"
  height={500} 
/>
```

#### Korean Market Page

**File Modified:** `frontend/src/pages/KoreanMarketPage.tsx`

**New Features:**
1. **Chart Type Selector**: Toggle between daily and minute charts
2. **Period Selector**: For daily charts - Daily (D), Weekly (W), Monthly (M)
3. **Minute Interval Selector**: For minute charts - 1, 5, 30, 60 minutes
4. **Date Picker**: For minute charts, select trading date (required, defaults to today in KST)
5. **Candle Limit Selector**: Choose number of candles (50, 100, 200, 500)
6. **Financial Statement Controls**: Year and quarter selectors with reload button

**Implementation:**
```tsx
// Chart controls state
const [chartInterval, setChartInterval] = useState<ChartInterval>('daily');
const [period, setPeriod] = useState<PeriodType>('D');
const [minuteInterval, setMinuteInterval] = useState<MinuteInterval>(1);
const [selectedDate, setSelectedDate] = useState<string>('');
const [candleLimit, setCandleLimit] = useState(100);

// Financial controls state
const [finYear, setFinYear] = useState<number>(new Date().getFullYear());
const [finQuarter, setFinQuarter] = useState<number | undefined>(undefined);

// Load candle data based on current settings
const loadCandleData = async () => {
  if (chartInterval === 'daily') {
    const candles = await koreanMarketService.getDailyCandle(
      symbol, period, true, candleLimit
    );
    setCandleData(candles);
  } else {
    const candles = await koreanMarketService.getMinuteCandle(
      symbol, minuteInterval, candleLimit, selectedDate
    );
    setCandleData(candles);
  }
};

// Reload when settings change
useEffect(() => {
  if (symbol && quote) {
    loadCandleData();
  }
}, [chartInterval, period, minuteInterval, selectedDate, candleLimit]);
```

#### US Market Page

**File Modified:** `frontend/src/pages/USMarketPage.tsx`

**New Features:**
1. **Period Selector**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max
2. **Interval Selector**: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
3. **Date Range Pickers**: Optional custom start and end dates
4. **Chart Display**: Integrated CandleChart component with USD currency

**Implementation:**
```tsx
// Chart controls state
const [period, setPeriod] = useState<USPeriod>('1mo');
const [interval, setInterval] = useState<USInterval>('1d');
const [startDate, setStartDate] = useState<string>('');
const [endDate, setEndDate] = useState<string>('');

// Load candle data
const loadCandleData = async () => {
  const candles = await usMarketService.getHistoricalData(
    symbol,
    period,
    interval,
    startDate || undefined,
    endDate || undefined
  );
  setCandleData(candles);
};

// Reload when settings change
useEffect(() => {
  if (symbol && quote) {
    loadCandleData();
  }
}, [period, interval, startDate, endDate]);
```

#### Type Definitions

**Files Modified:**
- `frontend/src/types/korean.ts` - Added `KoreanCandleData`, `ChartInterval`, `MinuteInterval`, `PeriodType`
- `frontend/src/types/us.ts` - Added `USCandleData`, `USPeriod`, `USInterval`

**Files Modified:**
- `frontend/src/services/koreanMarket.ts` - Added `getDailyCandle()` and `getMinuteCandle()` methods
- `frontend/src/services/usMarket.ts` - Added `getHistoricalData()` method

## Testing

### Manual Testing Steps

#### Korean Market Testing

1. **Basic Stock Quote**
   ```
   - Navigate to Korean Market page
   - Enter stock code: 005930 (Samsung Electronics)
   - Click Search
   - Verify stock price and info displays
   ```

2. **Daily Chart**
   ```
   - Ensure "Daily" is selected in Type dropdown
   - Try different periods: Daily, Weekly, Monthly
   - Verify chart displays with correct data
   - Check volume bars show correct colors
   ```

3. **Minute Chart**
   ```
   - Select "Minute" in Type dropdown
   - Select interval: 1, 5, 30, or 60 minutes
   - Select a trading date (e.g., today)
   - Verify intraday chart displays
   ```

4. **Financial Statements**
   ```
   - Try different years from dropdown
   - Try different quarters (Annual, Q1, Q2, Q3, Q4)
   - Click Reload button
   - Verify financial data updates
   ```

#### US Market Testing

1. **Basic Stock Quote**
   ```
   - Navigate to US Market page
   - Enter ticker: AAPL
   - Click Search
   - Verify stock price and market cap display
   ```

2. **Historical Chart**
   ```
   - Try different periods: 1mo, 3mo, 6mo, 1y, etc.
   - Verify chart data range matches selection
   ```

3. **Intraday Chart**
   ```
   - Select interval: 1m, 5m, 15m, 30m, or 60m
   - Select period: 1d or 5d
   - Verify intraday chart displays
   ```

4. **Custom Date Range**
   ```
   - Enter start date and end date
   - Verify chart displays data for specified range
   ```

5. **Financial Statements**
   ```
   - Verify financial table displays
   - Check multiple years of data
   ```

### Known Limitations

1. **Korean Minute Charts**: Require a specific trading date. Only shows data for that single day.
2. **US Intraday Data**: Yahoo Finance limits intraday data to recent 7-60 days depending on interval.
3. **Corp Code Mapping**: Stock 300120 and other less common stocks may not have corp codes unless the full list is downloaded successfully.
4. **Database Tables**: The new `korean_financials` and `us_financials` tables must be created manually in Supabase.

## Configuration Required

### Environment Variables

Ensure these environment variables are set:

```bash
# Korean Investment Securities API
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_NUMBER=your_account_number

# OpenDart API
DART_API_KEY=your_dart_api_key
DART_BASE_URL=https://opendart.fss.or.kr/api

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Database Setup

Run the SQL script in your Supabase SQL editor:
```bash
# Copy contents of database/add_korean_financials_table.sql
# Paste into Supabase SQL Editor
# Execute the script
```

## Future Enhancements

1. **Candlestick Rendering**: Upgrade chart to show true candlesticks instead of line charts
2. **Technical Indicators**: Add moving averages, RSI, MACD, etc.
3. **Chart Annotations**: Allow users to draw lines and add notes
4. **Export Functionality**: Download chart data as CSV
5. **Real-time Updates**: WebSocket integration for live price updates
6. **Comparison Charts**: Compare multiple stocks on same chart
7. **More Financial Data**: Add balance sheet, cash flow, ratios in detailed views

## Files Changed

### Backend
- `backend/src/integrations/opendart.py` - Corp code auto-download
- `backend/src/models/us.py` - Added USCandleData model
- `backend/src/integrations/yfinance_client.py` - Added historical data fetching
- `backend/src/services/us_market.py` - Added service method
- `backend/src/api/us.py` - Added candle endpoint

### Frontend
- `frontend/src/components/CandleChart.tsx` - New chart component
- `frontend/src/pages/KoreanMarketPage.tsx` - Enhanced with charts and controls
- `frontend/src/pages/USMarketPage.tsx` - Enhanced with charts and controls
- `frontend/src/types/korean.ts` - Added candle data types
- `frontend/src/types/us.ts` - Added candle data types
- `frontend/src/services/koreanMarket.ts` - Added candle data methods
- `frontend/src/services/usMarket.ts` - Added historical data method

### Database
- `database/add_korean_financials_table.sql` - New summary tables

## Conclusion

This implementation provides comprehensive charting capabilities for both Korean and US markets with flexible filtering options. Users can now:

- View daily, weekly, and monthly charts
- Analyze intraday price movements with minute-level data
- Compare financial statements across different periods
- Customize chart display with various interval and period options

The architecture is extensible and can easily support additional features like technical indicators and real-time updates in the future.
