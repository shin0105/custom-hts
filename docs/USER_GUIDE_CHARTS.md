# User Guide: Stock Chart Features

## Overview
This guide explains how to use the new candle chart and financial statement features in the Custom HTS application for both Korean and US markets.

## Korean Market Features

### Accessing the Korean Market
1. Navigate to the Korean Market page from the main navigation
2. The page displays a search bar at the top

### Searching for a Korean Stock
1. Enter a 6-digit stock code (e.g., 005930 for Samsung Electronics)
2. Press Enter or click the "Search" button
3. The stock quote will appear showing:
   - Stock symbol and company name
   - Current price in Korean Won (₩)
   - Price change and percentage change
   - Color-coded gains (green) and losses (red)

### Using the Price Chart

#### Daily Charts
1. **Chart Type**: Ensure "Daily" is selected in the Type dropdown
2. **Period Selection**: Choose from:
   - **Daily (D)**: Shows daily candles
   - **Weekly (W)**: Shows weekly candles
   - **Monthly (M)**: Shows monthly candles
3. **Candles**: Select how many candles to display (50, 100, 200, or 500)

#### Minute Charts (Intraday)
1. **Chart Type**: Select "Minute" from the Type dropdown
2. **Interval**: Choose the minute interval:
   - **1 Minute**: Most detailed intraday view
   - **5 Minutes**: Balanced detail
   - **30 Minutes**: Broader intraday view
   - **60 Minutes**: Hourly candles
3. **Date**: Select a specific trading date
   - Defaults to today (Korean Standard Time)
   - Only shows data for the selected day
4. **Candles**: Adjust the number of candles to display

### Understanding the Chart
- **Price Lines**: 
  - Blue line: Closing prices
  - Green dashed line: High prices
  - Red dashed line: Low prices
- **Volume Bars**: 
  - Green bars: Days/periods when price increased
  - Red bars: Days/periods when price decreased
  - Height indicates trading volume
- **Tooltip**: Hover over the chart to see:
  - Date/time
  - Open, High, Low, Close (OHLC) prices
  - Price change and percentage
  - Trading volume

### Viewing Financial Statements

#### Basic View
- After searching for a stock, scroll down to see the Financial Statements section
- Displays key metrics:
  - Company name
  - Reporting period (Year and Quarter)
  - Revenue (매출액)
  - Operating Income (영업이익)
  - Net Income (당기순이익)
  - Total Assets (자산총계)
  - Total Liabilities (부채총계)
  - Total Equity (자본총계)

#### Changing the Period
1. **Year Selector**: Choose from the last 5 years
2. **Quarter Selector**: Choose from:
   - **Annual**: Full year data
   - **Q1**: First quarter (Jan-Mar)
   - **Q2**: Second quarter (Apr-Jun)
   - **Q3**: Third quarter (Jul-Sep)
   - **Q4**: Fourth quarter (Oct-Dec)
3. Click the **Reload** button to fetch updated data

#### Understanding the Values
- All financial values are displayed in Korean Won
- Large numbers are shown in 억 (hundred millions)
- Example: ₩123.45억 = 12.345 billion won

### Tips for Korean Market
- Use major stock codes for best results:
  - 005930: Samsung Electronics
  - 000660: SK Hynix
  - 005380: Hyundai Motor
  - 035420: Naver
  - 035720: Kakao
- Minute charts only show data for one trading day
- Korean market hours: 9:00 AM - 3:30 PM KST
- Financial data comes from OpenDart (공시시스템)

## US Market Features

### Accessing the US Market
1. Navigate to the US Market page from the main navigation
2. The page displays a search bar at the top

### Searching for a US Stock
1. Enter a ticker symbol (e.g., AAPL for Apple)
2. Press Enter or click the "Search" button
3. The stock quote will appear showing:
   - Ticker symbol and company name
   - Current price in US Dollars ($)
   - Price change and percentage change
   - Market capitalization

### Using the Price Chart

#### Period Selection
Choose how much historical data to display:
- **1d**: One day (intraday)
- **5d**: Five days
- **1mo**: One month
- **3mo**: Three months
- **6mo**: Six months
- **1y**: One year
- **2y**: Two years
- **5y**: Five years
- **ytd**: Year to date
- **max**: Maximum available history

#### Interval Selection
Choose the data granularity:

**For Daily and Longer:**
- **1d**: Daily candles
- **1wk**: Weekly candles
- **1mo**: Monthly candles

**For Intraday (works best with 1d or 5d period):**
- **1m**: 1-minute candles (most detailed)
- **5m**: 5-minute candles
- **15m**: 15-minute candles
- **30m**: 30-minute candles
- **60m**: 60-minute candles (hourly)

#### Custom Date Range (Optional)
1. Leave the date fields empty to use the Period selection
2. OR enter specific dates:
   - **Start Date**: Beginning of date range
   - **End Date**: End of date range
3. When dates are provided, the Period selection is ignored

### Understanding the US Chart
- **Price Lines**:
  - Blue line: Closing prices
  - Green dashed line: High prices
  - Red dashed line: Low prices
- **Volume Bars**:
  - Green bars: Periods when price increased
  - Red bars: Periods when price decreased
- **Tooltip**: Hover to see detailed information
  - All prices in USD
  - Volume in shares

### Viewing Financial Statements

#### Financial Table
- Displays multiple years of financial data in a table format
- Shows up to 5 most recent years
- Columns include:
  - **Year**: Fiscal year
  - **Revenue**: Total revenue
  - **Operating Income**: Operating profit
  - **Net Income**: Bottom line profit
  - **EPS**: Earnings per share

#### Understanding the Values
- All values in US Dollars
- Large numbers abbreviated:
  - K = Thousands ($1,000)
  - M = Millions ($1,000,000)
  - B = Billions ($1,000,000,000)
- EPS shown to 2 decimal places

### Tips for US Market
- Popular tickers to try:
  - AAPL: Apple
  - MSFT: Microsoft
  - GOOGL: Google/Alphabet
  - AMZN: Amazon
  - TSLA: Tesla
  - NVDA: NVIDIA
- Intraday data (minute intervals) limited to recent 7-60 days
- US market hours: 9:30 AM - 4:00 PM EST
- Financial data from Yahoo Finance

## Common Features

### Chart Interactions
1. **Hover**: Move mouse over chart to see detailed information
2. **Automatic Updates**: Chart reloads when you change settings
3. **Error Handling**: If data fails to load, an error message appears

### Loading States
- "Loading..." appears while fetching data
- Search button disabled during loading
- Chart shows "No chart data available" if fetch fails

### Responsive Design
- Charts adapt to screen width
- Works on desktop and tablet (mobile may be limited)

## Troubleshooting

### Chart Not Displaying
- Verify you clicked Search after entering a symbol
- Check that you have internet connection
- For Korean minute charts, ensure you selected a valid trading date
- Try refreshing the page

### Financial Data Not Loading
- Some stocks may not have complete financial data
- For Korean stocks, ensure the stock code is correct (6 digits)
- For US stocks, try a major company ticker first
- Click the Reload button to retry

### Error Messages
- **"Failed to load stock data"**: Invalid symbol or API issue
- **"No chart data available"**: No historical data for selected period
- **"No financial data available"**: Company may not have published financials

### Performance
- Large numbers of candles (500) may load slowly
- Minute data with many candles may take longer
- Consider reducing the candle count for faster loading

## Keyboard Shortcuts
- **Enter**: After typing a symbol, press Enter to search
- **Tab**: Navigate between form fields

## Best Practices

### Korean Market
1. Start with daily charts before exploring minute charts
2. Use minute charts only when you need intraday detail
3. Remember to select a trading date for minute charts
4. Check multiple quarters to see trends in financials

### US Market
1. Start with 1mo or 3mo period for recent overview
2. Use 1d interval for daily chart analysis
3. Switch to minute intervals only for very short periods (1d or 5d)
4. Use custom date ranges for specific event analysis

## Data Sources

### Korean Market
- **Stock Quotes**: KDevelopers (한국투자증권 OpenAPI)
- **Financial Statements**: OpenDart (금융감독원 전자공시시스템)
- **Historical Data**: KDevelopers API

### US Market
- **Stock Quotes**: Yahoo Finance
- **Financial Statements**: Yahoo Finance
- **Historical Data**: Yahoo Finance

## Data Refresh Rates
- **Stock Quotes**: Real-time during market hours
- **Charts**: Historical data, not real-time
- **Financials**: Quarterly/Annual, updated after company reports

## Privacy and Security
- No personal data is collected
- API keys are securely stored on server
- No trading capabilities - display only
- Data cached to reduce API calls

## Support
For issues or questions:
1. Check this user guide first
2. Verify your internet connection
3. Try refreshing the page
4. Check if the stock symbol/code is correct

## Future Features (Coming Soon)
- Real-time price updates
- More technical indicators
- Ability to compare multiple stocks
- Export chart data
- Save favorite stocks
- Custom watchlists
