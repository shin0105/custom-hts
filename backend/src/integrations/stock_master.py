"""
Stock master file downloader and parser for Korean markets.

This module provides functionality to download and parse stock master files (.mst)
from Korea Investment Securities for KOSPI, KOSDAQ, and KONEX markets.

Reference: https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
"""

import urllib.request
import ssl
import zipfile
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class StockMasterFileManager:
    """
    Manager for downloading and parsing Korean stock master files.
    
    Master files contain comprehensive information about all listed stocks including:
    - Stock codes (short and standard)
    - Company names
    - Market classification
    - Financial metrics
    - Trading information
    """
    
    BASE_URL = "https://new.real.download.dws.co.kr/common/master"
    
    MARKETS = {
        "kospi": "kospi_code.mst.zip",
        "kosdaq": "kosdaq_code.mst.zip",
        "konex": "konex_code.mst.zip"
    }
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the master file manager.
        
        Args:
            data_dir: Directory to store master files. Defaults to backend/data/master_files
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent / "data" / "master_files"
        else:
            self.data_dir = Path(data_dir)
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Master file directory: {self.data_dir}")
    
    def download_market_file(
        self, 
        market: str, 
        force: bool = False
    ) -> bool:
        """
        Download master file for a specific market.
        
        Args:
            market: Market name ("kospi", "kosdaq", or "konex")
            force: Force download even if file exists
            
        Returns:
            True if download successful, False otherwise
        """
        if market not in self.MARKETS:
            logger.error(f"Unknown market: {market}. Valid markets: {list(self.MARKETS.keys())}")
            return False
        
        zip_filename = self.MARKETS[market]
        mst_filename = zip_filename.replace(".zip", "")
        
        zip_path = self.data_dir / zip_filename
        mst_path = self.data_dir / mst_filename
        
        # Check if already downloaded
        if mst_path.exists() and not force:
            logger.info(f"{market} master file already exists: {mst_path}")
            return True
        
        try:
            # Disable SSL verification for download
            ssl._create_default_https_context = ssl._create_unverified_context
            
            url = f"{self.BASE_URL}/{zip_filename}"
            logger.info(f"Downloading {market} master file from {url}...")
            
            urllib.request.urlretrieve(url, str(zip_path))
            logger.info(f"Downloaded to {zip_path}")
            
            # Extract zip file
            logger.info(f"Extracting {zip_filename}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            logger.info(f"Extracted to {mst_path}")
            
            # Remove zip file
            if zip_path.exists():
                zip_path.unlink()
                logger.info(f"Removed temporary zip file")
            
            logger.info(f"✓ Successfully downloaded {market} master file")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {market} master file: {e}")
            return False
    
    def download_all_markets(self, force: bool = False) -> Dict[str, bool]:
        """
        Download master files for all markets.
        
        Args:
            force: Force download even if files exist
            
        Returns:
            Dictionary mapping market names to download success status
        """
        logger.info("Downloading master files for all markets...")
        results = {}
        
        for market in self.MARKETS.keys():
            results[market] = self.download_market_file(market, force=force)
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Downloaded {success_count}/{len(results)} market files successfully")
        
        return results
    
    def parse_kospi_master(self) -> Optional[pd.DataFrame]:
        """
        Parse KOSPI master file into a DataFrame.
        
        Returns:
            DataFrame with KOSPI stock information, or None if parsing fails
        """
        return self._parse_master_file("kospi")
    
    def parse_kosdaq_master(self) -> Optional[pd.DataFrame]:
        """
        Parse KOSDAQ master file into a DataFrame.
        
        Returns:
            DataFrame with KOSDAQ stock information, or None if parsing fails
        """
        return self._parse_master_file("kosdaq")
    
    def parse_konex_master(self) -> Optional[pd.DataFrame]:
        """
        Parse KONEX master file into a DataFrame.
        
        Returns:
            DataFrame with KONEX stock information, or None if parsing fails
        """
        return self._parse_master_file("konex")
    
    def _parse_master_file(self, market: str) -> Optional[pd.DataFrame]:
        """
        Parse master file for a specific market.
        
        Args:
            market: Market name ("kospi", "kosdaq", or "konex")
            
        Returns:
            DataFrame with stock information, or None if parsing fails
        """
        if market not in self.MARKETS:
            logger.error(f"Unknown market: {market}")
            return None
        
        mst_filename = self.MARKETS[market].replace(".zip", "")
        mst_path = self.data_dir / mst_filename
        
        if not mst_path.exists():
            logger.error(f"Master file not found: {mst_path}")
            logger.info(f"Please run download_market_file('{market}') first")
            return None
        
        try:
            if market == "kospi":
                return self._parse_kospi(mst_path)
            elif market == "kosdaq":
                return self._parse_kosdaq(mst_path)
            elif market == "konex":
                return self._parse_konex(mst_path)
        except Exception as e:
            logger.error(f"Failed to parse {market} master file: {e}")
            return None
    
    def _parse_kospi(self, file_path: Path) -> pd.DataFrame:
        """Parse KOSPI master file."""
        logger.info(f"Parsing KOSPI master file: {file_path}")
        
        tmp_fil1 = self.data_dir / "kospi_code_part1.tmp"
        tmp_fil2 = self.data_dir / "kospi_code_part2.tmp"
        
        with open(tmp_fil1, "w") as wf1, open(tmp_fil2, "w") as wf2:
            with open(file_path, "r", encoding="cp949") as f:
                for row in f:
                    # Part 1: First part without last 228 characters
                    rf1 = row[0:len(row) - 228]
                    rf1_1 = rf1[0:9].rstrip()  # 단축코드
                    rf1_2 = rf1[9:21].rstrip()  # 표준코드
                    rf1_3 = rf1[21:].strip()  # 한글명
                    wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                    
                    # Part 2: Last 228 characters
                    rf2 = row[-228:]
                    wf2.write(rf2)
        
        # Read part 1
        part1_columns = ['단축코드', '표준코드', '한글명']
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')
        
        # Read part 2 with fixed width format
        field_specs = [2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 5, 5, 1, 1, 1, 2, 1, 1,
                       1, 2, 2, 2, 3, 1, 3, 12, 12, 8, 15, 21, 2, 7, 1, 1, 1, 1, 1,
                       9, 9, 9, 5, 9, 8, 9, 3, 1, 1, 1]
        
        part2_columns = ['그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
                         '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
                         'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
                         'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
                         'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
                         'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
                         'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
                         '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
                         '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
                         '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
                         '상장주수', '자본금', '결산월', '공모가', '우선주',
                         '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
                         '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
                         '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능']
        
        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        
        # Merge dataframes
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)
        
        # Clean up temporary files
        tmp_fil1.unlink()
        tmp_fil2.unlink()
        
        logger.info(f"✓ Parsed KOSPI master file: {len(df)} stocks")
        return df
    
    def _parse_kosdaq(self, file_path: Path) -> pd.DataFrame:
        """Parse KOSDAQ master file."""
        logger.info(f"Parsing KOSDAQ master file: {file_path}")
        
        tmp_fil1 = self.data_dir / "kosdaq_code_part1.tmp"
        tmp_fil2 = self.data_dir / "kosdaq_code_part2.tmp"
        
        with open(tmp_fil1, "w") as wf1, open(tmp_fil2, "w") as wf2:
            with open(file_path, "r", encoding="cp949") as f:
                for row in f:
                    # Part 1: First part without last 222 characters
                    rf1 = row[0:len(row) - 222]
                    rf1_1 = rf1[0:9].rstrip()  # 단축코드
                    rf1_2 = rf1[9:21].rstrip()  # 표준코드
                    rf1_3 = rf1[21:].strip()  # 한글종목명
                    wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                    
                    # Part 2: Last 222 characters
                    rf2 = row[-222:]
                    wf2.write(rf2)
        
        # Read part 1
        part1_columns = ['단축코드', '표준코드', '한글종목명']
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')
        
        # Read part 2 with fixed width format
        field_specs = [2, 1, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1, 1, 9, 5, 5, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 3,
                       1, 3, 12, 12, 8, 15, 21, 2, 7, 1, 1, 1, 1, 9, 9, 9, 5, 9, 8,
                       9, 3, 1, 1, 1]
        
        part2_columns = ['증권그룹구분코드', '시가총액 규모 구분 코드 유가',
                         '지수업종 대분류 코드', '지수 업종 중분류 코드', '지수업종 소분류 코드',
                         '벤처기업 여부 (Y/N)', '저유동성종목 여부', 'KRX 종목 여부',
                         'ETP 상품구분코드', 'KRX100 종목 여부 (Y/N)', 'KRX 자동차 여부',
                         'KRX 반도체 여부', 'KRX 바이오 여부', 'KRX 은행 여부', '기업인수목적회사여부',
                         'KRX 에너지 화학 여부', 'KRX 철강 여부', '단기과열종목구분코드',
                         'KRX 미디어 통신 여부', 'KRX 건설 여부', '(코스닥)투자주의환기종목여부',
                         'KRX 증권 구분', 'KRX 선박 구분', 'KRX섹터지수 보험여부',
                         'KRX섹터지수 운송여부', 'KOSDAQ150지수여부 (Y,N)', '주식 기준가',
                         '정규 시장 매매 수량 단위', '시간외 시장 매매 수량 단위',
                         '거래정지 여부', '정리매매 여부', '관리 종목 여부', '시장 경고 구분 코드',
                         '시장 경고위험 예고 여부', '불성실 공시 여부', '우회 상장 여부',
                         '락구분 코드', '액면가 변경 구분 코드', '증자 구분 코드', '증거금 비율',
                         '신용주문 가능 여부', '신용기간', '전일 거래량', '주식 액면가',
                         '주식 상장 일자', '상장 주수(천)', '자본금', '결산 월', '공모 가격',
                         '우선주 구분 코드', '공매도과열종목여부', '이상급등종목여부',
                         'KRX300 종목 여부 (Y/N)', '매출액', '영업이익', '경상이익', '단기순이익',
                         'ROE(자기자본이익률)', '기준년월', '전일기준 시가총액 (억)', '그룹사 코드',
                         '회사신용한도초과여부', '담보대출가능여부', '대주가능여부']
        
        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        
        # Merge dataframes
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)
        
        # Clean up temporary files
        tmp_fil1.unlink()
        tmp_fil2.unlink()
        
        logger.info(f"✓ Parsed KOSDAQ master file: {len(df)} stocks")
        return df
    
    def _parse_konex(self, file_path: Path) -> pd.DataFrame:
        """Parse KONEX master file (simplified version)."""
        logger.info(f"Parsing KONEX master file: {file_path}")
        
        # KONEX has simpler structure
        tmp_fil1 = self.data_dir / "konex_code_part1.tmp"
        
        with open(tmp_fil1, "w") as wf1:
            with open(file_path, "r", encoding="cp949") as f:
                for row in f:
                    # Extract basic information
                    rf1_1 = row[0:9].rstrip()  # 단축코드
                    rf1_2 = row[9:21].rstrip()  # 표준코드
                    rf1_3 = row[21:61].strip()  # 한글명
                    wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
        
        # Read data
        part1_columns = ['단축코드', '표준코드', '한글명']
        df = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')
        
        # Clean up temporary file
        tmp_fil1.unlink()
        
        logger.info(f"✓ Parsed KONEX master file: {len(df)} stocks")
        return df
    
    def get_stock_info(self, market: str, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific stock.
        
        Args:
            market: Market name ("kospi", "kosdaq", or "konex")
            stock_code: Stock code (6-digit code)
            
        Returns:
            Dictionary with stock information, or None if not found
        """
        df = self._parse_master_file(market)
        if df is None:
            return None
        
        # Search by stock code
        result = df[df['단축코드'] == stock_code]
        if len(result) == 0:
            logger.warning(f"Stock code {stock_code} not found in {market}")
            return None
        
        return result.iloc[0].to_dict()
    
    def save_to_excel(self, market: str, output_file: Optional[str] = None) -> bool:
        """
        Save parsed master file to Excel.
        
        Args:
            market: Market name ("kospi", "kosdaq", or "konex")
            output_file: Output Excel file path. If None, saves to data directory
            
        Returns:
            True if save successful, False otherwise
        """
        df = self._parse_master_file(market)
        if df is None:
            return False
        
        if output_file is None:
            output_file = self.data_dir / f"{market}_code.xlsx"
        
        try:
            df.to_excel(output_file, index=False)
            logger.info(f"✓ Saved {market} data to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            return False


# Global instance
master_file_manager = StockMasterFileManager()
