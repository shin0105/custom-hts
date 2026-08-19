/**
 * TypeScript type definitions for Korean market data.
 */

export interface KoreanStockQuote {
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
  high?: number;
  low?: number;
  open?: number;
  previous_close?: number;
}

export interface KoreanFinancialStatement {
  symbol: string;
  company_name: string;
  year: number;
  quarter?: number;
  revenue?: number;
  operating_income?: number;
  net_income?: number;
  total_assets?: number;
  total_liabilities?: number;
  total_equity?: number;
  eps?: number;
  updated_at: string;
}

export interface KoreanCandleData {
  symbol: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change?: number;
  change_percent?: number;
}

export interface KoreanValuationMetrics {
  symbol: string;
  price: number;
  fiscal_year?: number;
  fiscal_quarter?: number;
  eps?: number;
  eps_12mf?: number;
  bps?: number;
  per?: number;
  per_12mf?: number;
  pbr?: number;
  eps_ttm?: number;
  bps_ttm?: number;
  per_ttm?: number;
  pbr_ttm?: number;
  ttm_quarters?: Array<{ year: number; quarter: number }>;
  estimate_12mf_labels?: string[];
  shares_outstanding?: number;
  market_cap?: number;
  notes?: string[];
  as_of: string;
}

/** One line item from the DART full financial statement response. */
export interface KoreanFinancialItem {
  sj_nm?: string;
  sj_div?: string;
  account_nm?: string;
  thstrm_amount?: string;
}

export interface KoreanAllFinancialsResponse {
  symbol: string;
  year: number;
  requested_year?: number;
  quarter?: number;
  fs_div: 'CFS' | 'OFS';
  count: number;
  data: KoreanFinancialItem[];
  note?: string;
}

export interface KoreanEstimatePerform {
  symbol: string;
  output1: Record<string, unknown>[];
  output2: Array<{
    metric: string;
    values: Array<string | number | null>;
    year_values: Record<string, string | number | null>;
  }>;
  output3: Array<{
    metric: string;
    values: Array<string | number | null>;
    year_values: Record<string, string | number | null>;
  }>;
  output4: string[];
  units?: Record<string, unknown>;
  unit_notes?: string;
}

export interface KoreanAccountBalance {
  account_number: string;
  total_evaluation: number;
  cash_balance: number;
  investment_amount: number;
  profit_loss: number;
  profit_loss_percent: number;
  timestamp: string;
}

export interface KoreanStockPosition {
  symbol: string;
  name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  evaluation_amount: number;
  profit_loss: number;
  profit_loss_percent: number;
}

export interface KoreanAccountResponse {
  balance: KoreanAccountBalance;
  positions: KoreanStockPosition[];
}

/** Response shape from KDevelopers search-bond-info API (장내채권 기본조회). */
export interface KoreanBondInfo {
  pdno: string;
  prdt_type_cd?: string | null;
  ksd_bond_item_name?: string | null;
  ksd_bond_item_eng_name?: string | null;
  bond_clsf_cd?: string | null;
  bond_clsf_kor_name?: string | null;
  issu_dt?: string | null;
  rvnu_dt?: string | null;
  rdpt_dt?: string | null;
  mdwy_rdpt_dt?: string | null;
  lstg_dt?: string | null;
  lstg_abol_dt?: string | null;
  iso_crcy_cd?: string | null;
  ksd_rcvg_bond_dsct_rt?: string | null;
  ksd_rcvg_bond_srfc_inrt?: string | null;
  ksd_tot_issu_amt?: string | null;
  int_caltm_mcnt?: string | null;
  bond_int_dfrm_mthd_cd?: string | null;
  int_dfrm_day_type_cd?: string | null;
  frst_int_dfrm_dt?: string | null;
  rgbf_int_dfrm_dt?: string | null;
  nxtm_int_dfrm_dt?: string | null;
  dpsi_psbl_yn?: string | null;
  sprx_psbl_yn?: string | null;
  qib_yn?: string | null;
  csbd_yn?: string | null;
  elec_scty_yn?: string | null;
  pclr_ptcr_text?: string | null;
  dshn_occr_yn?: string | null;
  expd_exts_yn?: string | null;
  [key: string]: unknown;
}

export interface KoreanBondQuote {
  pdno: string;
  name: string;
  current_price?: number | null;
  change?: number | null;
  change_percent?: number | null;
  volume?: number | null;
  high?: number | null;
  low?: number | null;
  open?: number | null;
  previous_close?: number | null;
  earning_rate?: number | null;
  best_ask?: number | null;
  best_bid?: number | null;
  middle_price?: number | null;
}

export interface KoreanBondValuation {
  pdno: string;
  name: string;
  as_of: string;
  raw_market_price?: number | null;
  market_price?: number | null;
  market_price_source?: string | null;
  theoretical_dirty_price?: number | null;
  accrued_interest?: number | null;
  theoretical_clean_price?: number | null;
  mispricing?: number | null;
  mispricing_percent?: number | null;
  annual_coupon_rate?: number | null;
  annual_yield_rate?: number | null;
  payment_interval_months?: number | null;
  remaining_periods?: number | null;
  face_value: number;
  redemption_ratio?: number | null;
  next_coupon_date?: string | null;
  maturity_date?: string | null;
  notes: string[];
}

export interface KoreanBondMasterItem {
  pdno: string;
  bond_type?: string | null;
  bond_class_code?: string | null;
  bond_interest_class_code?: string | null;
  name?: string | null;
  english_name?: string | null;
  bond_class_name?: string | null;
  issue_date?: string | null;
  maturity_date?: string | null;
  listed_date?: string | null;
  delisted_date?: string | null;
  currency?: string | null;
  surface_interest_rate?: number | null;
  total_issue_amount?: number | null;
  current_price?: number | null;
  change_percent?: number | null;
  volume?: number | null;
}

export interface KoreanBondMasterResponse {
  source_file?: string | null;
  total_loaded: number;
  total_returned: number;
  offset: number;
  limit: number;
  query?: string | null;
  bond_type?: string | null;
  bond_class_code?: string | null;
  bond_interest_class_code?: string | null;
  listed_date_from?: string | null;
  listed_date_to?: string | null;
  issue_date_from?: string | null;
  issue_date_to?: string | null;
  maturity_date_from?: string | null;
  maturity_date_to?: string | null;
  available_bond_types?: Record<string, number>;
  available_bond_class_codes_by_type?: Record<string, Record<string, number>>;
  available_bond_interest_class_codes_by_type?: Record<string, Record<string, number>>;
  items: KoreanBondMasterItem[];
}

export interface KoreanFuturesOptionsMasterItem {
  market: 'index' | 'stock' | 'commodity';
  commodity_type?: string | null;
  info_type?: string | null;
  short_code?: string | null;
  standard_code?: string | null;
  name_kr?: string | null;
  atm_class_code?: string | null;
  strike_price?: string | null;
  month_class_code?: string | null;
  underlying_short_code?: string | null;
  underlying_name_kr?: string | null;
}

export interface KoreanFuturesOptionsMasterResponse {
  market: 'all' | 'index' | 'stock' | 'commodity';
  source_files?: Record<string, string | null>;
  total_loaded: number;
  total_returned: number;
  offset: number;
  limit: number;
  query?: string | null;
  info_type?: string | null;
  underlying_short_code?: string | null;
  available_markets?: Record<string, number>;
  available_info_types_by_market?: Record<string, Record<string, number>>;
  items: KoreanFuturesOptionsMasterItem[];
}

export interface KoreanFuturesOptionReferenceIndex {
  code?: string | null;
  name?: string | null;
  current_price?: number | null;
  change_sign?: string | null;
  change?: number | null;
  change_percent?: number | null;
}

export interface KoreanFuturesOptionQuote {
  symbol: string;
  market_div_code: string;
  name?: string | null;
  current_price?: number | null;
  change_sign?: string | null;
  change?: number | null;
  change_percent?: number | null;
  previous_close?: number | null;
  volume?: number | null;
  trading_value?: number | null;
  open_interest?: number | null;
  open_interest_change?: number | null;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  upper_limit?: number | null;
  lower_limit?: number | null;
  theoretical_price?: number | null;
  basis?: number | null;
  market_basis?: number | null;
  discrepancy_rate?: number | null;
  strike_price?: number | null;
  delta?: number | null;
  gamma?: number | null;
  theta?: number | null;
  vega?: number | null;
  rho?: number | null;
  historical_volatility?: number | null;
  implied_volatility?: number | null;
  last_trade_date?: string | null;
  remaining_days?: number | null;
  reference_indices?: KoreanFuturesOptionReferenceIndex[];
}

export interface KoreanFuturesOptionOrderbookLevel {
  level: number;
  ask_price?: number | null;
  ask_quantity?: number | null;
  ask_orders?: number | null;
  bid_price?: number | null;
  bid_quantity?: number | null;
  bid_orders?: number | null;
}

export interface KoreanFuturesOptionOrderbook {
  symbol: string;
  market_div_code: string;
  name?: string | null;
  current_price?: number | null;
  change_sign?: string | null;
  change?: number | null;
  change_percent?: number | null;
  previous_close?: number | null;
  volume?: number | null;
  as_of_time?: string | null;
  total_ask_quantity?: number | null;
  total_bid_quantity?: number | null;
  total_ask_orders?: number | null;
  total_bid_orders?: number | null;
  levels: KoreanFuturesOptionOrderbookLevel[];
}

export interface KoreanFuturesOptionMinuteCandle {
  symbol: string;
  market_div_code: string;
  date?: string | null;
  time?: string | null;
  timestamp?: string | null;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  close?: number | null;
  volume?: number | null;
  cumulative_trading_value?: number | null;
}

export interface KoreanFuturesOptionMinuteCandleResponse {
  symbol: string;
  market_div_code: string;
  timeframe_sec: number;
  date?: string | null;
  time?: string | null;
  name?: string | null;
  current_price?: number | null;
  change?: number | null;
  change_sign?: string | null;
  change_percent?: number | null;
  volume?: number | null;
  open_interest?: number | null;
  open_interest_change?: number | null;
  candles: KoreanFuturesOptionMinuteCandle[];
}

export type KoreanFuturesChartInterval = 'daily' | 'minute';

export interface KoreanFuturesOptionChainRow {
  option_code?: string | null;
  strike_price?: number | null;
  current_price?: number | null;
  change_sign?: string | null;
  change?: number | null;
  change_percent?: number | null;
  bid_price?: number | null;
  ask_price?: number | null;
  volume?: number | null;
  trading_value?: number | null;
  open_interest?: number | null;
  open_interest_change?: number | null;
  delta?: number | null;
  gamma?: number | null;
  theta?: number | null;
  vega?: number | null;
  rho?: number | null;
  implied_volatility?: number | null;
  historical_volatility?: number | null;
  theoretical_price?: number | null;
  intrinsic_value?: number | null;
  time_value?: number | null;
  moneyness?: string | null;
}

export interface KoreanFuturesOptionChainResponse {
  expiry: string;
  market_class: string;
  fetched_at: string;
  total_calls: number;
  total_puts: number;
  calls: KoreanFuturesOptionChainRow[];
  puts: KoreanFuturesOptionChainRow[];
}

export type ChartInterval = 'daily' | 'minute';
export type MinuteInterval = 1 | 5 | 10 | 30 | 60;
export type PeriodType = 'D' | 'W' | 'M';
