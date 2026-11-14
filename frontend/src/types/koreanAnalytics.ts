/**
 * Types for basis (futures vs underlying) and bond yield analytics.
 * Mirrors backend/src/models/korean_analytics.py.
 */

export type BasisUnderlyingKind = 'stock' | 'index';

export interface KoreanBasisUnderlying {
  code: string;
  name: string;
  kind: BasisUnderlyingKind;
  contract_count: number;
  front_symbol?: string | null;
}

export interface KoreanBasisContract {
  symbol: string;
  name?: string | null;
  expiry_month?: string | null;
  last_trade_date?: string | null;
  days_to_expiry?: number | null;
  price?: number | null;
  bid?: number | null;
  ask?: number | null;
  mid?: number | null;
  volume?: number | null;
  open_interest?: number | null;
  basis?: number | null;
  basis_percent?: number | null;
  mid_basis?: number | null;
  implied_rate?: number | null;
  theoretical_price?: number | null;
  theoretical_basis?: number | null;
  discrepancy_percent?: number | null;
  carry_rate?: number | null;
  broker_theoretical_price?: number | null;
  broker_basis?: number | null;
  broker_market_basis?: number | null;
  broker_discrepancy_rate?: number | null;
}

export interface KoreanBasisSnapshot {
  underlying_code: string;
  underlying_name: string;
  kind: BasisUnderlyingKind;
  as_of: string;
  spot?: number | null;
  spot_source?: 'futures_synced' | 'live_quote' | null;
  live_spot?: number | null;
  live_spot_change_percent?: number | null;
  spot_gap_percent?: number | null;
  rate?: number | null;
  rate_source: 'user' | 'broker';
  dividend: number;
  contracts: KoreanBasisContract[];
  notes: string[];
}

export interface KoreanBasisHistoryPoint {
  date: string;
  spot: number;
  futures: number;
  basis: number;
  basis_percent: number;
  implied_rate?: number | null;
  volume?: number | null;
}

export interface KoreanBasisStats {
  count: number;
  mean: number;
  std: number;
  min: number;
  max: number;
  latest: number;
  zscore?: number | null;
  percentile: number;
}

export interface KoreanBasisHistory {
  underlying_code: string;
  underlying_name: string;
  kind: BasisUnderlyingKind;
  symbol: string;
  contract_name?: string | null;
  points: KoreanBasisHistoryPoint[];
  stats?: KoreanBasisStats | null;
  notes: string[];
}

export type OptionParitySource = 'quote' | 'last' | 'wide_quote';

export interface KoreanOptionParityRow {
  strike: number;
  is_atm: boolean;
  call_symbol: string;
  put_symbol: string;
  call_last?: number | null;
  call_bid?: number | null;
  call_ask?: number | null;
  call_volume: number;
  put_last?: number | null;
  put_bid?: number | null;
  put_ask?: number | null;
  put_volume: number;
  synthetic?: number | null;
  source?: OptionParitySource | null;
  synthetic_bid?: number | null;
  synthetic_ask?: number | null;
  futures_gap?: number | null;
  futures_gap_percent?: number | null;
  spot_basis?: number | null;
  spot_basis_percent?: number | null;
  implied_rate?: number | null;
  conversion_edge?: number | null;
  reversal_edge?: number | null;
}

export interface KoreanOptionParitySummary {
  synthetic?: number | null;
  source?: OptionParitySource | null;
  strike_count: number;
  futures_gap?: number | null;
  futures_gap_percent?: number | null;
  spot_basis?: number | null;
  spot_basis_percent?: number | null;
  implied_rate?: number | null;
  conversion_edge?: number | null;
  conversion_strike?: number | null;
  reversal_edge?: number | null;
  reversal_strike?: number | null;
}

export interface KoreanOptionParity {
  underlying_code: string;
  underlying_name: string;
  kind: BasisUnderlyingKind;
  as_of: string;
  /** Empty when the underlying has no listed monthly options. */
  expiries: string[];
  expiry?: string | null;
  last_trade_date?: string | null;
  days_to_expiry?: number | null;
  spot?: number | null;
  spot_source?: 'futures_synced' | 'live_quote' | null;
  futures_symbol?: string | null;
  futures_name?: string | null;
  futures_price?: number | null;
  futures_last?: number | null;
  futures_bid?: number | null;
  futures_ask?: number | null;
  rate?: number | null;
  rate_source: 'user' | 'futures_carry' | 'none';
  summary?: KoreanOptionParitySummary | null;
  rows: KoreanOptionParityRow[];
  notes: string[];
}

export interface KoreanBondOrderbookLevel {
  level: number;
  ask_price?: number | null;
  ask_quantity?: number | null;
  ask_yield?: number | null;
  bid_price?: number | null;
  bid_quantity?: number | null;
  bid_yield?: number | null;
}

export interface KoreanBondAgencyValuation {
  agency: string;
  price?: number | null;
  yield_rate?: number | null;
  credit_rating?: string | null;
}

export interface KoreanBondScenario {
  shift_bp: number;
  yield_rate: number;
  price: number;
  price_change: number;
  price_change_percent: number;
}

export type BondReferenceSource =
  | 'last_trade'
  | 'quote_mid'
  | 'last_price'
  | 'agency';

export interface KoreanBondAnalytics {
  pdno: string;
  name: string;
  as_of: string;
  settlement_date: string;
  kind?: string | null;
  kind_label?: string | null;
  supported: boolean;
  unsupported_reason?: string | null;
  coupon_rate?: number | null;
  interval_months?: number | null;
  issue_date?: string | null;
  maturity_date?: string | null;
  remaining_years?: number | null;
  next_coupon_date?: string | null;
  last_price?: number | null;
  last_yield?: number | null;
  computed_yield?: number | null;
  traded_today: boolean;
  volume?: number | null;
  day_open_yield?: number | null;
  day_high_price_yield?: number | null;
  day_low_price_yield?: number | null;
  best_bid_price?: number | null;
  best_bid_yield?: number | null;
  best_ask_price?: number | null;
  best_ask_yield?: number | null;
  bid_ask_spread_bp?: number | null;
  levels: KoreanBondOrderbookLevel[];
  reference_yield?: number | null;
  reference_price?: number | null;
  reference_source?: BondReferenceSource | null;
  accrued_interest?: number | null;
  clean_price?: number | null;
  after_tax_yield?: number | null;
  tax_rate?: number | null;
  macaulay_duration?: number | null;
  modified_duration?: number | null;
  convexity?: number | null;
  dv01?: number | null;
  scenarios: KoreanBondScenario[];
  agency_date?: string | null;
  agency_yield?: number | null;
  agency_price?: number | null;
  agency_spread_bp?: number | null;
  agency_implied_price?: number | null;
  price_vs_agency?: number | null;
  agencies: KoreanBondAgencyValuation[];
  notes: string[];
}

export interface KoreanBondYieldPoint {
  date: string;
  close?: number | null;
  volume?: number | null;
  market_yield?: number | null;
  agency_yield?: number | null;
  agency_price?: number | null;
  spread_bp?: number | null;
}

export interface KoreanBondYieldHistory {
  pdno: string;
  name: string;
  points: KoreanBondYieldPoint[];
  traded_days: number;
  average_spread_bp?: number | null;
  latest_spread_bp?: number | null;
  notes: string[];
}
