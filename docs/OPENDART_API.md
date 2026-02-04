# OPENDART (DART) API Guide

This document summarizes the OPENDART (DART) endpoints used in this project for Korean company data and financial statements.

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Common Parameters](#common-parameters)
- [Common Error Codes](#common-error-codes)
- [Endpoints](#endpoints)
  - [Corp Code List](#corp-code-list)
  - [Company Information](#company-information)
  - [Multi-Company Major Accounts](#multi-company-major-accounts)
  - [Multi-Company Financial Indices](#multi-company-financial-indices)
- [References](#references)

## Overview
OPENDART provides corporate disclosure data for Korean listed and registered companies. Most endpoints require an 8-digit `corp_code` obtained from the corp code list endpoint.

## Authentication
All requests require an API key:
- Parameter name: `crtfc_key`
- Value: 40-character OPENDART API key
- Store locally as `DART_API_KEY` in `.env`

## Base URL
```
https://opendart.fss.or.kr/api
```

## Common Parameters
- `crtfc_key` (string, required): OPENDART API key
- `corp_code` (string, required): 8-digit corp code from the corp code list
- `bsns_year` (string, required): 4-digit fiscal year (e.g., 2023)
- `reprt_code` (string, required): report type
  - `11013`: Q1 report
  - `11012`: Semiannual report
  - `11014`: Q3 report
  - `11011`: Annual report

## Common Error Codes
All endpoints return a status code in the response (or in the XML file for the corp code list).

- `000`: Success
- `010`: Unregistered key
- `011`: Invalid key (temporarily disabled)
- `012`: Unauthorized IP
- `013`: No data found
- `014`: File not found
- `020`: Request limit exceeded
- `021`: Too many companies requested (max 100)
- `100`: Invalid parameter value
- `101`: Invalid access
- `800`: System maintenance
- `900`: Undefined error
- `901`: Key expired (contact opendart@fss.or.kr)

## Endpoints

### Corp Code List
Download the complete corp code list (ZIP containing XML).

- **Method**: GET
- **URL**: `https://opendart.fss.or.kr/api/corpCode.xml`
- **Response format**: ZIP (binary) with XML file

**Request parameters**
- `crtfc_key` (required)

**Response XML fields**
- `corp_code`: 8-digit corp code
- `corp_name`: official company name
- `corp_eng_name`: official English name
- `stock_code`: 6-digit stock code (listed companies only)
- `modify_date`: last modified date (YYYYMMDD)

**Example**
```bash
curl -o corpCode.zip "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key=${DART_API_KEY}"
```

### Company Information
Get detailed company profile by corp code.

- **Method**: GET
- **URL**: `https://opendart.fss.or.kr/api/company.json`
- **XML variant**: `https://opendart.fss.or.kr/api/company.xml`

**Request parameters**
- `crtfc_key` (required)
- `corp_code` (required)

**Response fields**
- `status`: result code (see [Common Error Codes](#common-error-codes))
- `message`: result message
- `corp_name`: official company name
- `corp_name_eng`: official English name
- `stock_name`: stock name (listed) or short name
- `stock_code`: 6-digit stock code
- `ceo_nm`: CEO name
- `corp_cls`: corporation class
  - `Y`: KOSPI
  - `K`: KOSDAQ
  - `N`: KONEX
  - `E`: Other
- `jurir_no`: corporate registration number
- `bizr_no`: business registration number
- `adres`: address
- `hm_url`: website URL
- `ir_url`: IR website URL
- `phn_no`: phone number
- `fax_no`: fax number
- `induty_code`: industry code
- `est_dt`: establishment date (YYYYMMDD)
- `acc_mt`: fiscal month (MM)

**Example**
```bash
curl "https://opendart.fss.or.kr/api/company.json?crtfc_key=${DART_API_KEY}&corp_code=00126380"
```

### Multi-Company Major Accounts
Fetch major account line items for multiple companies and reports.

- **Method**: GET
- **URL**: `https://opendart.fss.or.kr/api/fnlttMultiAcnt.json`
- **XML variant**: `https://opendart.fss.or.kr/api/fnlttMultiAcnt.xml`

**Request parameters**
- `crtfc_key` (required)
- `corp_code` (required): comma-separated corp codes (max 100)
- `bsns_year` (required): fiscal year (available from 2015+)
- `reprt_code` (required): report type

**Response fields (list)**
- `rcept_no`: receipt number (14 digits)
- `bsns_year`: fiscal year
- `stock_code`: 6-digit stock code
- `reprt_code`: report code
- `account_nm`: account name (e.g., Total Equity)
- `fs_div`: financial statement type (`OFS` or `CFS`)
- `fs_nm`: financial statement name
- `sj_div`: statement type (`BS` or `IS`)
- `sj_nm`: statement name
- `thstrm_nm`: current period name
- `thstrm_dt`: current period date
- `thstrm_amount`: current period amount
- `thstrm_add_amount`: current cumulative amount
- `frmtrm_nm`: prior period name
- `frmtrm_dt`: prior period date
- `frmtrm_amount`: prior period amount
- `frmtrm_add_amount`: prior cumulative amount
- `bfefrmtrm_nm`: two-periods-ago name (annual only)
- `bfefrmtrm_dt`: two-periods-ago date (annual only)
- `bfefrmtrm_amount`: two-periods-ago amount (annual only)
- `ord`: account sort order
- `currency`: currency unit

**Example**
```bash
curl "https://opendart.fss.or.kr/api/fnlttMultiAcnt.json?crtfc_key=${DART_API_KEY}&corp_code=00334624,00126380&bsns_year=2018&reprt_code=11011"
```

### Multi-Company Financial Indices
Fetch key financial indices (profitability, stability, growth, activity).

- **Method**: GET
- **URL**: `https://opendart.fss.or.kr/api/fnlttCmpnyIndx.json`
- **XML variant**: `https://opendart.fss.or.kr/api/fnlttCmpnyIndx.xml`

**Request parameters**
- `crtfc_key` (required)
- `corp_code` (required): comma-separated corp codes (max 100)
- `bsns_year` (required): fiscal year (available from 2023 Q3+)
- `reprt_code` (required): report type
- `idx_cl_code` (required): index category
  - `M210000`: profitability
  - `M220000`: stability
  - `M230000`: growth
  - `M240000`: activity

**Response fields (list)**
- `reprt_code`: report code
- `bsns_year`: fiscal year
- `corp_code`: corp code
- `stock_code`: 6-digit stock code
- `stlm_dt`: settlement date (YYYY-MM-DD)
- `idx_cl_code`: index category code
- `idx_cl_nm`: index category name
- `idx_code`: index code
- `idx_nm`: index name
- `idx_val`: index value

**Example**
```bash
curl "https://opendart.fss.or.kr/api/fnlttCmpnyIndx.json?crtfc_key=${DART_API_KEY}&corp_code=00164742,00159023&bsns_year=2023&reprt_code=11014&idx_cl_code=M210000"
```

## References
- Corp code list: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019018
- Company information: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002
- Multi-company major accounts: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019017
- Multi-company financial indices: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2022002
