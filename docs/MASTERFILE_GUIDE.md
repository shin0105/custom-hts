# Korean Stock Market Master Files Guide

This document explains how to use the KOSPI and KOSDAQ master files provided by Korea Investment & Securities through their Open Trading API.

## Overview

The master files (`kospi_code.mst` and `kosdaq_code.mst`) are binary data files containing comprehensive information about all stocks listed on the Korean stock markets. These files are structured according to fixed-width record formats defined in C header files.

## File Locations

- **KOSPI Master File**: `backend/data/kospi_code.mst`
- **KOSDAQ Master File**: `backend/data/kosdaq_code.mst`

## Data Structure

Both files follow similar structures but have some market-specific differences. Each record in the file represents one stock and contains fixed-width fields.

### KOSPI Master File Structure (ST_KSP_CODE)

| Field Name | Size | Description | Notes |
|------------|------|-------------|-------|
| mksc_shrn_iscd | 9 bytes | 단축코드 (Short code) | Primary stock identifier |
| stnd_iscd | 12 bytes | 표준코드 (Standard code) | Standard stock code |
| hts_kor_isnm | 40 bytes | 한글종목명 (Korean stock name) | Full Korean name |
| scrt_grp_cls_code | 2 bytes | 증권그룹구분코드 | ST:주권, MF:증권투자회사, RT:부동산투자회사, SC:선박투자회사, IF:사회간접자본투융자회사, DR:주식예탁증서, EW:ELW, EF:ETF, SW:신주인수권증권, SR:신주인수권증서, BC:수익증권, FE:해외ETF, FS:외국주권 |
| avls_scal_cls_code | 1 byte | 시가총액 규모 구분 | 0:제외, 1:대, 2:중, 3:소 |
| bstp_larg_div_code | 4 bytes | 지수 업종 대분류 코드 | Large category index |
| bstp_medm_div_code | 4 bytes | 지수 업종 중분류 코드 | Medium category index |
| bstp_smal_div_code | 4 bytes | 지수 업종 소분류 코드 | Small category index |
| mnin_cls_code_yn | 1 byte | 제조업 구분 | Y/N |
| low_current_yn | 1 byte | 저유동성종목 여부 | Y/N |
| sprn_strr_nmix_issu_yn | 1 byte | 지배 구조 지수 종목 여부 | Y/N |
| kospi200_apnt_cls_code | 1 byte | KOSPI200 섹터업종 | 0:미분류, 1:건설기계, 2:조선운송, 3:철강소재, 4:에너지화학, 5:정보통신, 6:금융, 7:필수소비재, 8:자유소비재 |
| kospi100_issu_yn | 1 byte | KOSPI100 여부 | Y/N |
| kospi50_issu_yn | 1 byte | KOSPI50 종목 여부 | Y/N |
| krx_issu_yn | 1 byte | KRX 종목 여부 | Y/N |
| etp_prod_cls_code | 1 byte | ETP 상품구분코드 | 0:해당없음, 1:투자회사형, 2:수익증권형, 3:ETN, 4:손실제한ETN |
| elw_pblc_yn | 1 byte | ELW 발행여부 | Y/N |
| krx100_issu_yn | 1 byte | KRX100 종목 여부 | Y/N |
| krx_car_yn | 1 byte | KRX 자동차 여부 | Y/N |
| krx_smcn_yn | 1 byte | KRX 반도체 여부 | Y/N |
| krx_bio_yn | 1 byte | KRX 바이오 여부 | Y/N |
| krx_bank_yn | 1 byte | KRX 은행 여부 | Y/N |
| etpr_undt_objt_co_yn | 1 byte | 기업인수목적회사여부 | Y/N |
| krx_enrg_chms_yn | 1 byte | KRX 에너지 화학 여부 | Y/N |
| krx_stel_yn | 1 byte | KRX 철강 여부 | Y/N |
| short_over_cls_code | 1 byte | 단기과열종목구분코드 | 0:해당없음, 1:지정예고, 2:지정, 3:지정연장(해제연기) |
| krx_medi_cmnc_yn | 1 byte | KRX 미디어 통신 여부 | Y/N |
| krx_cnst_yn | 1 byte | KRX 건설 여부 | Y/N |
| krx_scrt_yn | 1 byte | KRX 증권 구분 | Y/N |
| krx_ship_yn | 1 byte | KRX 선박 구분 | Y/N |
| krx_insu_yn | 1 byte | KRX 보험여부 | Y/N |
| krx_trnp_yn | 1 byte | KRX 운송여부 | Y/N |
| sri_nmix_yn | 1 byte | SRI 지수여부 | Y/N |
| stck_sdpr | 9 bytes | 주식 기준가 | Base price |
| frml_mrkt_deal_qty_unit | 5 bytes | 정규 시장 매매 수량 단위 | Regular market trading quantity unit |
| ovtm_mrkt_deal_qty_unit | 5 bytes | 시간외 시장 매매 수량 단위 | After-hours trading quantity unit |
| trht_yn | 1 byte | 거래정지 여부 | Y/N |
| sltr_yn | 1 byte | 정리매매 여부 | Y/N |
| mang_issu_yn | 1 byte | 관리 종목 여부 | Y/N |
| mrkt_alrm_cls_code | 2 bytes | 시장 경고 구분 코드 | 00:해당없음, 01:투자주의, 02:투자경고, 03:투자위험 |
| mrkt_alrm_risk_adnt_yn | 1 byte | 시장 경고위험 예고 여부 | Y/N |
| insn_pbnt_yn | 1 byte | 불성실 공시 여부 | Y/N |
| byps_lstn_yn | 1 byte | 우회 상장 여부 | Y/N |
| flng_cls_code | 2 bytes | 락구분 코드 | 00:해당사항없음, 01:권리락, 02:배당락, 03:분배락, 04:권배락, 05:중간배당락, 06:권리중간배당락, 99:기타 |
| fcam_mod_cls_code | 2 bytes | 액면가 변경 구분 코드 | 00:해당없음, 01:액면분할, 02:액면병합, 99:기타 |
| icic_cls_code | 2 bytes | 증자 구분 코드 | 00:해당없음, 01:유상증자, 02:무상증자, 03:유무상증자, 99:기타 |
| marg_rate | 3 bytes | 증거금 비율 | Margin rate |
| crdt_able | 1 byte | 신용주문 가능 여부 | Y/N |
| crdt_days | 3 bytes | 신용기간 | Credit period in days |
| prdy_vol | 12 bytes | 전일 거래량 | Previous day volume |
| stck_fcam | 12 bytes | 주식 액면가 | Face value |
| stck_lstn_date | 8 bytes | 주식 상장 일자 | Listing date (YYYYMMDD) |
| lstn_stcn | 15 bytes | 상장 주수(천) | Listed shares (thousands) |
| cpfn | 21 bytes | 자본금 | Capital |
| stac_month | 2 bytes | 결산 월 | Fiscal month |
| po_prc | 7 bytes | 공모 가격 | IPO price |
| prst_cls_code | 1 byte | 우선주 구분 코드 | 0:보통주, 1:구형우선주, 2:신형우선주 |
| ssts_hot_yn | 1 byte | 공매도과열종목여부 | Y/N |
| stange_runup_yn | 1 byte | 이상급등종목여부 | Y/N |
| krx300_issu_yn | 1 byte | KRX300 종목 여부 | Y/N |
| kospi_issu_yn | 1 byte | KOSPI여부 | Y/N |
| sale_account | 9 bytes | 매출액 | Sales |
| bsop_prfi | 9 bytes | 영업이익 | Operating profit |
| op_prfi | 9 bytes | 경상이익 | Ordinary income |
| thtr_ntin | 5 bytes | 당기순이익 | Net income |
| roe | 9 bytes | ROE(자기자본이익률) | Return on equity |
| base_date | 8 bytes | 기준년월 | Base date (YYYYMMDD) |
| prdy_avls_scal | 9 bytes | 전일기준 시가총액 (억) | Previous market cap (100 million KRW) |
| grp_code | 3 bytes | 그룹사 코드 | Group company code |
| co_crdt_limt_over_yn | 1 byte | 회사신용한도초과여부 | Y/N |
| secu_lend_able_yn | 1 byte | 담보대출가능여부 | Y/N |
| stln_able_yn | 1 byte | 대주가능여부 | Y/N |

### KOSDAQ Master File Structure (ST_KSQ_CODE)

The KOSDAQ structure is very similar to KOSPI with the following key differences:

| Field Name | Size | Description | Notes |
|------------|------|-------------|-------|
| avls_scal_cls_code | 1 byte | 시가총액 규모 구분 | 0:제외, 1:KOSDAQ100, 2:KOSDAQmid300, 3:KOSDAQsmall |
| vntr_issu_yn | 1 byte | 벤처기업 여부 | Y/N (KOSDAQ specific) |
| invt_alrm_yn | 1 byte | 투자주의환기종목여부 | Y/N (KOSDAQ specific) |
| ksq150_nmix_yn | 1 byte | KOSDAQ150지수여부 | Y/N (KOSDAQ specific) |

**Note**: KOSDAQ does not include:
- `kospi200_apnt_cls_code`
- `kospi100_issu_yn`
- `kospi50_issu_yn`
- `kospi_issu_yn`
- `sprn_strr_nmix_issu_yn`
- `sri_nmix_yn`
- `krx_fnnc_svc_yn` (deleted field as of 2015-12-18)

## Reading Master Files

### Python Example

```python
import struct
from pathlib import Path

# Define KOSPI record structure (simplified example)
# Total record size: approximately 528 bytes
KOSPI_RECORD_FORMAT = {
    'mksc_shrn_iscd': (0, 9),      # Short code
    'stnd_iscd': (9, 12),          # Standard code
    'hts_kor_isnm': (21, 40),      # Korean name
    'scrt_grp_cls_code': (61, 2),  # Security group code
    'stck_sdpr': (170, 9),         # Base price
    'stck_lstn_date': (234, 8),    # Listing date
    'lstn_stcn': (242, 15),        # Listed shares
}

def read_kospi_masterfile(file_path: str):
    """Read and parse KOSPI master file."""
    stocks = []
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Determine record size by finding the pattern
    # Each record is approximately 528 bytes for KOSPI
    record_size = 528  # Adjust based on actual file structure
    
    for i in range(0, len(content), record_size):
        if i + record_size > len(content):
            break
            
        record = content[i:i+record_size]
        
        stock = {
            'short_code': record[0:9].decode('cp949', errors='ignore').strip(),
            'standard_code': record[9:21].decode('cp949', errors='ignore').strip(),
            'korean_name': record[21:61].decode('cp949', errors='ignore').strip(),
            'security_group': record[61:63].decode('cp949', errors='ignore').strip(),
        }
        
        stocks.append(stock)
    
    return stocks

# Usage
stocks = read_kospi_masterfile('backend/data/kospi_code.mst')
for stock in stocks[:5]:  # Print first 5 stocks
    print(f"{stock['short_code']}: {stock['korean_name']}")
```

### Encoding Notes

- The master files use **CP949** (EUC-KR extended) encoding for Korean text
- All text fields should be decoded using 'cp949' encoding
- Numeric fields are stored as ASCII strings and should be stripped and converted

## Common Use Cases

### 1. Stock Code Lookup

```python
def find_stock_by_name(name: str, masterfile_path: str):
    """Find stock code by Korean name."""
    stocks = read_kospi_masterfile(masterfile_path)
    matches = [s for s in stocks if name in s['korean_name']]
    return matches
```

### 2. Filter by Security Type

```python
def filter_by_security_type(security_type: str, stocks: list):
    """
    Filter stocks by security group code.
    
    Args:
        security_type: ST(주권), EF(ETF), EW(ELW), etc.
        stocks: List of stock dictionaries
    """
    return [s for s in stocks if s['security_group'] == security_type]
```

### 3. Get Index Constituents

```python
def get_kospi200_stocks(stocks: list):
    """Get all KOSPI200 constituent stocks."""
    # Parse kospi200_apnt_cls_code field (position varies)
    # Return stocks where kospi200_apnt_cls_code != '0'
    pass
```

### 4. Check Trading Status

```python
def get_tradable_stocks(stocks: list):
    """Get stocks that are currently tradable."""
    # Filter where:
    # - trht_yn (거래정지) == 'N'
    # - sltr_yn (정리매매) == 'N'
    # - mang_issu_yn (관리종목) == 'N'
    pass
```

## Data Updates

- Master files should be updated regularly (typically daily)
- Download from Korea Investment & Securities API
- Files are typically updated after market close
- Always validate file integrity before using

## Integration with KDevelopers API

The master files complement the KDevelopers OpenAPI:

1. **Initial Stock Discovery**: Use master files to get complete stock lists
2. **Real-time Data**: Use KDevelopers API for price quotes and trading data
3. **Stock Metadata**: Use master files for detailed stock classification and attributes
4. **Data Validation**: Cross-reference API responses with master file data

## Tips and Best Practices

1. **Caching**: Load master files once and cache in memory for faster lookups
2. **Indexing**: Create dictionaries indexed by stock code for O(1) lookups
3. **Validation**: Always validate field boundaries when parsing binary data
4. **Error Handling**: Use `errors='ignore'` when decoding to handle corrupted bytes
5. **Testing**: Verify parsing logic with known stocks before production use
6. **Updates**: Implement automated daily downloads of fresh master files
7. **Backup**: Keep historical master files for audit and debugging purposes

## File Size Reference

- KOSPI master file: ~1-2 MB (depending on number of listed stocks)
- KOSDAQ master file: ~2-3 MB (more listed companies)
- Record count: 2000-3000 records per file

## References

- [Korea Investment Open Trading API GitHub](https://github.com/koreainvestment/open-trading-api)
- [KOSPI Master File Structure](https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/%EC%A2%85%EB%AA%A9%EB%A7%88%EC%8A%A4%ED%84%B0%EC%A0%95%EB%B3%B4(%EC%BD%94%EC%8A%A4%ED%94%BC).h)
- [KOSDAQ Master File Structure](https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/%EC%A2%85%EB%AA%A9%EB%A7%88%EC%8A%A4%ED%84%B0%EC%A0%95%EB%B3%B4(%EC%BD%94%EC%8A%A4%EB%8B%A5).h)

## Troubleshooting

### Issue: Garbled Korean Text
- **Solution**: Ensure you're using 'cp949' encoding, not 'utf-8' or 'euc-kr'

### Issue: Incorrect Field Positions
- **Solution**: Verify record size by examining the actual binary file structure
- Use hex editors to inspect file format
- Check for record delimiters or padding bytes

### Issue: Missing or Extra Records
- **Solution**: Verify file integrity, re-download if necessary
- Check for file corruption during transfer

### Issue: Numeric Field Parsing Errors
- **Solution**: Strip whitespace before converting to numbers
- Handle empty strings as None or 0 values

## License and Attribution

The master file format is provided by Korea Investment & Securities.
Always comply with their API terms of service and usage guidelines.
