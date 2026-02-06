"""
Test script to download masterfiles and convert to JSON format.

This script:
1. Downloads master files (.mst) from Korea Investment Securities
2. Saves raw unzipped files to backend/data/
3. Parses the master files
4. Converts to JSON format with stock code as key
5. Saves JSON files to backend/data/

Usage:
    cd backend
    uv run python test_masterfile_to_json.py
"""

import sys
import os
import json
import logging
from pathlib import Path
import shutil
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.integrations.stock_master import StockMasterFileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MasterFileToJsonConverter:
    """Convert master files to JSON format with stock code as key."""
    
    def __init__(self):
        """Initialize converter."""
        # Use backend/data/master_files for downloads
        self.master_dir = Path(__file__).parent / "data" / "master_files"
        # Save raw and JSON files to backend/data
        self.output_dir = Path(__file__).parent / "data"
        
        self.master_manager = StockMasterFileManager(data_dir=str(self.master_dir))
        
        logger.info(f"Master files directory: {self.master_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def download_all_markets(self, force: bool = False) -> dict:
        """
        Download master files for all markets.
        
        Args:
            force: Force download even if files exist
            
        Returns:
            Dictionary of download results
        """
        logger.info("=" * 70)
        logger.info("Step 1: Downloading Master Files")
        logger.info("=" * 70)
        
        results = self.master_manager.download_all_markets(force=force)
        
        logger.info("\nDownload Results:")
        for market, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"  {market.upper()}: {status}")
        
        return results
    
    def copy_raw_files(self) -> dict:
        """
        Copy raw .mst files to backend/data directory.
        
        Returns:
            Dictionary of copy results
        """
        logger.info("\n" + "=" * 70)
        logger.info("Step 2: Copying Raw Master Files to backend/data")
        logger.info("=" * 70)
        
        results = {}
        markets = ["kospi", "kosdaq", "konex"]
        
        for market in markets:
            mst_file = f"{market}_code.mst"
            source = self.master_dir / mst_file
            destination = self.output_dir / mst_file
            
            try:
                if source.exists():
                    shutil.copy2(source, destination)
                    file_size = destination.stat().st_size / 1024  # KB
                    logger.info(f"  ✓ Copied {mst_file} ({file_size:.1f} KB)")
                    results[market] = True
                else:
                    logger.warning(f"  ✗ Source file not found: {source}")
                    results[market] = False
            except Exception as e:
                logger.error(f"  ✗ Failed to copy {mst_file}: {e}")
                results[market] = False
        
        return results
    
    def convert_to_json(self, market: str) -> bool:
        """
        Convert a market's master file to JSON format.
        
        Args:
            market: Market name ("kospi", "kosdaq", or "konex")
            
        Returns:
            True if conversion successful
        """
        try:
            # Parse master file
            if market == "kospi":
                df = self.master_manager.parse_kospi_master()
                name_column = '한글명'
            elif market == "kosdaq":
                df = self.master_manager.parse_kosdaq_master()
                name_column = '한글종목명'
            elif market == "konex":
                df = self.master_manager.parse_konex_master()
                name_column = '한글명'
            else:
                logger.error(f"Unknown market: {market}")
                return False
            
            if df is None:
                logger.error(f"Failed to parse {market} master file")
                return False
            
            logger.info(f"  Parsed {len(df)} stocks from {market.upper()}")
            
            # Convert DataFrame to dictionary with stock code as key
            json_data = {}
            
            for idx, row in df.iterrows():
                stock_code = str(row['단축코드']).strip()
                
                # Convert row to dictionary, handling NaN and special types
                stock_info = {}
                for col in df.columns:
                    value = row[col]
                    
                    # Handle different data types
                    if pd.isna(value):
                        stock_info[col] = None
                    elif isinstance(value, (int, float)):
                        if pd.isna(value):
                            stock_info[col] = None
                        else:
                            stock_info[col] = value
                    else:
                        stock_info[col] = str(value).strip()
                
                # Add metadata
                stock_info['market'] = market.upper()
                stock_info['last_updated'] = datetime.now().isoformat()
                
                json_data[stock_code] = stock_info
            
            # Save to JSON file
            json_file = self.output_dir / f"{market}_stocks.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            file_size = json_file.stat().st_size / 1024  # KB
            logger.info(f"  ✓ Saved {market.upper()} JSON: {json_file.name} ({file_size:.1f} KB)")
            logger.info(f"    Total stocks: {len(json_data)}")
            
            # Show sample entry
            if json_data:
                sample_code = list(json_data.keys())[0]
                sample_stock = json_data[sample_code]
                logger.info(f"    Sample: {sample_code} - {sample_stock.get(name_column)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert {market} to JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_combined_json(self) -> bool:
        """
        Create a combined JSON file with all markets.
        
        Returns:
            True if creation successful
        """
        logger.info("\n  Creating combined JSON file...")
        
        try:
            combined_data = {}
            markets = ["kospi", "kosdaq", "konex"]
            
            for market in markets:
                json_file = self.output_dir / f"{market}_stocks.json"
                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        market_data = json.load(f)
                        combined_data.update(market_data)
                        logger.info(f"    Added {len(market_data)} stocks from {market.upper()}")
            
            # Save combined file
            combined_file = self.output_dir / "all_stocks.json"
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            file_size = combined_file.stat().st_size / 1024  # KB
            logger.info(f"  ✓ Saved combined JSON: {combined_file.name} ({file_size:.1f} KB)")
            logger.info(f"    Total stocks: {len(combined_data)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create combined JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_all_markets(self) -> dict:
        """
        Convert all markets to JSON format.
        
        Returns:
            Dictionary of conversion results
        """
        logger.info("\n" + "=" * 70)
        logger.info("Step 3: Converting Master Files to JSON")
        logger.info("=" * 70)
        
        results = {}
        markets = ["kospi", "kosdaq", "konex"]
        
        for market in markets:
            logger.info(f"\nProcessing {market.upper()}...")
            results[market] = self.convert_to_json(market)
        
        # Create combined JSON
        results['combined'] = self.create_combined_json()
        
        return results
    
    def show_json_sample(self, market: str, stock_code: str = None):
        """
        Display a sample entry from JSON file.
        
        Args:
            market: Market name
            stock_code: Specific stock code to display (optional)
        """
        logger.info("\n" + "=" * 70)
        logger.info(f"Sample JSON Data for {market.upper()}")
        logger.info("=" * 70)
        
        json_file = self.output_dir / f"{market}_stocks.json"
        if not json_file.exists():
            logger.error(f"JSON file not found: {json_file}")
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get stock code to display
            if stock_code is None:
                stock_code = list(data.keys())[0]
            
            if stock_code not in data:
                logger.error(f"Stock code {stock_code} not found")
                return
            
            stock_info = data[stock_code]
            
            logger.info(f"\nStock Code: {stock_code}")
            logger.info(f"Data (first 10 fields):")
            for i, (key, value) in enumerate(list(stock_info.items())[:10]):
                logger.info(f"  {key}: {value}")
            
            if len(stock_info) > 10:
                logger.info(f"  ... and {len(stock_info) - 10} more fields")
            
        except Exception as e:
            logger.error(f"Failed to read JSON: {e}")
    
    def run_full_test(self, force_download: bool = False):
        """
        Run full test workflow.
        
        Args:
            force_download: Force re-download of files
        """
        logger.info("\n" + "=" * 70)
        logger.info("Master File to JSON Conversion Test")
        logger.info("=" * 70 + "\n")
        
        try:
            # Step 1: Download masterfiles
            download_results = self.download_all_markets(force=force_download)
            
            # Step 2: Copy raw files
            copy_results = self.copy_raw_files()
            
            # Step 3: Convert to JSON
            convert_results = self.convert_all_markets()
            
            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("Test Summary")
            logger.info("=" * 70)
            
            logger.info("\nDownload Results:")
            for market, success in download_results.items():
                status = "✓" if success else "✗"
                logger.info(f"  {status} {market.upper()}")
            
            logger.info("\nCopy Results:")
            for market, success in copy_results.items():
                status = "✓" if success else "✗"
                logger.info(f"  {status} {market.upper()}")
            
            logger.info("\nConversion Results:")
            for market, success in convert_results.items():
                status = "✓" if success else "✗"
                logger.info(f"  {status} {market.upper()}")
            
            # Show sample
            if convert_results.get('kospi'):
                self.show_json_sample('kospi', '005930')  # Samsung Electronics
            
            logger.info("\n" + "=" * 70)
            logger.info("Test completed successfully!")
            logger.info("=" * 70)
            logger.info(f"\nOutput files saved to: {self.output_dir}")
            logger.info("  - kospi_code.mst (raw)")
            logger.info("  - kosdaq_code.mst (raw)")
            logger.info("  - konex_code.mst (raw)")
            logger.info("  - kospi_stocks.json")
            logger.info("  - kosdaq_stocks.json")
            logger.info("  - konex_stocks.json")
            logger.info("  - all_stocks.json (combined)")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert master files to JSON')
    parser.add_argument(
        '--force', 
        action='store_true', 
        help='Force re-download of master files'
    )
    
    args = parser.parse_args()
    
    converter = MasterFileToJsonConverter()
    converter.run_full_test(force_download=args.force)


if __name__ == "__main__":
    main()
