# Stock Master File Manager - Implementation

## Overview

This module provides functionality to download and parse Korean stock master files (.mst) from Korea Investment Securities' download server.

## What Are Master Files?

Master files (.mst) contain comprehensive information about all listed stocks in Korean markets:
- Stock codes (short 6-digit and standard 12-digit)
- Company names in Korean
- Market classification (KOSPI, KOSDAQ, KONEX)
- Financial metrics (market cap, ROE, sales, profit)
- Trading information (base price, trading units, margin ratio)
- Various flags (KRX indices, trading suspensions, etc.)

## Features

### 1. Download Master Files

Download master files for KOSPI, KOSDAQ, and KONEX markets from the official KIS server:

```python
from src.integrations.stock_master import master_file_manager

# Download all markets
results = master_file_manager.download_all_markets()

# Or download specific market
master_file_manager.download_market_file("kospi", force=True)
```

### 2. Parse Master Files

Parse the binary .mst files into pandas DataFrames:

```python
# Parse KOSPI master file
kospi_df = master_file_manager.parse_kospi_master()
print(f"Total KOSPI stocks: {len(kospi_df)}")

# Parse KOSDAQ master file
kosdaq_df = master_file_manager.parse_kosdaq_master()
print(f"Total KOSDAQ stocks: {len(kosdaq_df)}")
```

### 3. Query Stock Information

Look up specific stocks by their code:

```python
# Get information for Samsung Electronics (005930)
info = master_file_manager.get_stock_info("kospi", "005930")
print(f"Name: {info['한글명']}")
print(f"Base Price: {info['기준가']}")
print(f"Market Cap: {info['시가총액']}")
```

### 4. Export to Excel

Export parsed data to Excel files for analysis:

```python
# Export KOSPI data to Excel
master_file_manager.save_to_excel("kospi")

# Export to custom location
master_file_manager.save_to_excel("kosdaq", output_file="my_kosdaq_data.xlsx")
```

### 5. Search Stocks by Name

```python
# Parse master file
df = master_file_manager.parse_kospi_master()

# Search for stocks containing "삼성"
samsung_stocks = df[df['한글명'].str.contains("삼성", na=False)]
for idx, row in samsung_stocks.iterrows():
    print(f"{row['단축코드']} - {row['한글명']}")
```

## File Formats

### KOSPI Master File (kospi_code.mst)

- Downloaded from: `https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip`
- File format: Fixed-width text file (cp949 encoding)
- Record length: Variable (last 228 characters contain detailed info)
- Total columns: 73 columns including:
  - Basic: 단축코드, 표준코드, 한글명
  - Market: 그룹코드, 시가총액규모, 업종분류
  - Trading: 기준가, 매매수량단위, 증거금비율
  - Flags: KRX indices, KOSPI200, ETP, etc.
  - Financial: 매출액, 영업이익, 당기순이익, ROE

### KOSDAQ Master File (kosdaq_code.mst)

- Downloaded from: `https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip`
- File format: Fixed-width text file (cp949 encoding)
- Record length: Variable (last 222 characters contain detailed info)
- Total columns: 66 columns
- Similar structure to KOSPI with KOSDAQ-specific fields

### KONEX Master File (konex_code.mst)

- Downloaded from: `https://new.real.download.dws.co.kr/common/master/konex_code.mst.zip`
- Simpler structure with basic stock information

## Data Directory Structure

```
backend/
├── src/
│   ├── integrations/
│   │   └── stock_master.py          # Main implementation
│   └── data/
│       └── master_files/             # Downloaded and parsed files
│           ├── kospi_code.mst        # Downloaded KOSPI master file
│           ├── kosdaq_code.mst       # Downloaded KOSDAQ master file
│           ├── konex_code.mst        # Downloaded KONEX master file
│           ├── kospi_code.xlsx       # Exported Excel file
│           └── kosdaq_code.xlsx      # Exported Excel file
└── examples/
    └── stock_master_example.py       # Usage examples
```

## Key Columns

### Common Columns (All Markets)
- `단축코드`: 6-digit stock code used in trading
- `표준코드`: 12-digit standard code (ISIN-like)
- `한글명` / `한글종목명`: Company name in Korean

### KOSPI/KOSDAQ Financial Columns
- `기준가`: Base price
- `시가총액`: Market capitalization
- `매출액`: Revenue
- `영업이익`: Operating profit
- `당기순이익`: Net income
- `ROE`: Return on equity

### Trading Information
- `매매수량단위`: Trading unit quantity
- `증거금비율`: Margin ratio
- `상장일자`: Listing date
- `상장주수`: Listed shares

### Market Classification Flags
- `KRX`, `KRX100`, `KRX300`: KRX index membership
- `KOSPI200`: KOSPI 200 index membership
- `ETP`: Exchange Traded Product flag
- `거래정지`: Trading suspension
- `관리종목`: Under supervision

## Usage Examples

See `backend/examples/stock_master_example.py` for complete working examples:

```bash
cd backend
uv run python examples/stock_master_example.py
```

## Implementation Details

The implementation follows the pattern from the reference repository:
- https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

Key differences from reference:
1. **Class-based design**: Wrapped in `StockMasterFileManager` class
2. **Flexible data directory**: Configurable data directory path
3. **Better error handling**: Comprehensive logging and error messages
4. **Additional features**: Search, query by code, Excel export

## API Reference

### StockMasterFileManager

#### `__init__(data_dir: Optional[str] = None)`
Initialize manager with optional custom data directory.

#### `download_market_file(market: str, force: bool = False) -> bool`
Download master file for a specific market.

#### `download_all_markets(force: bool = False) -> Dict[str, bool]`
Download master files for all markets (KOSPI, KOSDAQ, KONEX).

#### `parse_kospi_master() -> Optional[pd.DataFrame]`
Parse KOSPI master file into DataFrame.

#### `parse_kosdaq_master() -> Optional[pd.DataFrame]`
Parse KOSDAQ master file into DataFrame.

#### `parse_konex_master() -> Optional[pd.DataFrame]`
Parse KONEX master file into DataFrame.

#### `get_stock_info(market: str, stock_code: str) -> Optional[Dict[str, Any]]`
Get information for a specific stock by code.

#### `save_to_excel(market: str, output_file: Optional[str] = None) -> bool`
Save parsed master file to Excel format.

## Notes

- Master files are typically updated daily by KIS
- Files use Korean encoding (cp949)
- Download server may not be accessible outside Korea
- Files can be large (several MB each)
- Parsing may take a few seconds due to fixed-width format

## Reference

- Official GitHub repo: https://github.com/koreainvestment/open-trading-api
- Stock info directory: https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
- Download server: https://new.real.download.dws.co.kr/common/master/
