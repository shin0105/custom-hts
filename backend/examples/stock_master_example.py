"""
Example script for downloading and using stock master files.

This script demonstrates how to:
1. Download master files from KIS servers
2. Parse the files into pandas DataFrames
3. Query stock information
4. Export to Excel files

Usage:
    cd backend
    uv run python examples/stock_master_example.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integrations.stock_master import master_file_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_download_all_markets():
    """Example 1: Download master files for all markets."""
    logger.info("=" * 70)
    logger.info("Example 1: Download Master Files for All Markets")
    logger.info("=" * 70)
    
    results = master_file_manager.download_all_markets(force=False)
    
    logger.info("\nDownload Results:")
    for market, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"  {market.upper()}: {status}")
    
    logger.info("")


def example_parse_and_display():
    """Example 2: Parse master files and display sample data."""
    logger.info("=" * 70)
    logger.info("Example 2: Parse Master Files and Display Data")
    logger.info("=" * 70)
    
    # Parse KOSPI
    logger.info("\nParsing KOSPI master file...")
    kospi_df = master_file_manager.parse_kospi_master()
    if kospi_df is not None:
        logger.info(f"  Total KOSPI stocks: {len(kospi_df)}")
        logger.info(f"  Columns: {len(kospi_df.columns)}")
        logger.info("\n  Sample data (first 3 stocks):")
        for idx, row in kospi_df.head(3).iterrows():
            logger.info(f"    {row['단축코드']} - {row['한글명']}")
    
    # Parse KOSDAQ
    logger.info("\nParsing KOSDAQ master file...")
    kosdaq_df = master_file_manager.parse_kosdaq_master()
    if kosdaq_df is not None:
        logger.info(f"  Total KOSDAQ stocks: {len(kosdaq_df)}")
        logger.info(f"  Columns: {len(kosdaq_df.columns)}")
        logger.info("\n  Sample data (first 3 stocks):")
        for idx, row in kosdaq_df.head(3).iterrows():
            logger.info(f"    {row['단축코드']} - {row['한글종목명']}")
    
    logger.info("")


def example_query_stock_info():
    """Example 3: Query specific stock information."""
    logger.info("=" * 70)
    logger.info("Example 3: Query Specific Stock Information")
    logger.info("=" * 70)
    
    # Query Samsung Electronics (005930) from KOSPI
    stock_code = "005930"
    logger.info(f"\nQuerying {stock_code} (Samsung Electronics) from KOSPI...")
    
    info = master_file_manager.get_stock_info("kospi", stock_code)
    if info:
        logger.info("  Stock Information:")
        logger.info(f"    Code: {info.get('단축코드')}")
        logger.info(f"    Name: {info.get('한글명')}")
        logger.info(f"    Standard Code: {info.get('표준코드')}")
        logger.info(f"    Base Price: {info.get('기준가')}")
        logger.info(f"    Listed Date: {info.get('상장일자')}")
        logger.info(f"    Market Cap: {info.get('시가총액')}")
    else:
        logger.error(f"  Stock {stock_code} not found")
    
    logger.info("")


def example_export_to_excel():
    """Example 4: Export master data to Excel files."""
    logger.info("=" * 70)
    logger.info("Example 4: Export Master Data to Excel")
    logger.info("=" * 70)
    
    # Export KOSPI
    logger.info("\nExporting KOSPI data to Excel...")
    if master_file_manager.save_to_excel("kospi"):
        logger.info("  ✓ KOSPI data exported successfully")
    else:
        logger.error("  ✗ Failed to export KOSPI data")
    
    # Export KOSDAQ
    logger.info("\nExporting KOSDAQ data to Excel...")
    if master_file_manager.save_to_excel("kosdaq"):
        logger.info("  ✓ KOSDAQ data exported successfully")
    else:
        logger.error("  ✗ Failed to export KOSDAQ data")
    
    logger.info("")


def example_search_stocks_by_name():
    """Example 5: Search stocks by company name."""
    logger.info("=" * 70)
    logger.info("Example 5: Search Stocks by Company Name")
    logger.info("=" * 70)
    
    search_term = "삼성"
    logger.info(f"\nSearching for stocks containing '{search_term}'...")
    
    # Search in KOSPI
    kospi_df = master_file_manager.parse_kospi_master()
    if kospi_df is not None:
        matches = kospi_df[kospi_df['한글명'].str.contains(search_term, na=False)]
        logger.info(f"\n  Found {len(matches)} matches in KOSPI:")
        for idx, row in matches.head(5).iterrows():
            logger.info(f"    {row['단축코드']} - {row['한글명']}")
    
    # Search in KOSDAQ
    kosdaq_df = master_file_manager.parse_kosdaq_master()
    if kosdaq_df is not None:
        matches = kosdaq_df[kosdaq_df['한글종목명'].str.contains(search_term, na=False)]
        logger.info(f"\n  Found {len(matches)} matches in KOSDAQ:")
        for idx, row in matches.head(5).iterrows():
            logger.info(f"    {row['단축코드']} - {row['한글종목명']}")
    
    logger.info("")


def main():
    """Run all examples."""
    logger.info("\n" + "=" * 70)
    logger.info("Stock Master File Manager Examples")
    logger.info("=" * 70 + "\n")
    
    try:
        # Example 1: Download all market files
        example_download_all_markets()
        
        # Example 2: Parse and display data
        example_parse_and_display()
        
        # Example 3: Query specific stock
        example_query_stock_info()
        
        # Example 4: Export to Excel
        example_export_to_excel()
        
        # Example 5: Search by name
        example_search_stocks_by_name()
        
        logger.info("=" * 70)
        logger.info("All examples completed!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
