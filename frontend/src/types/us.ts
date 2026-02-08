/**
 * TypeScript type definitions for US market data.
 */

export interface USStockQuote {
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
  market_cap?: number;
}

export interface USFinancialStatement {
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
  pe_ratio?: number;
  updated_at: string;
}

export interface USCandleData {
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

export interface USValuationMetrics {
  symbol: string;
  price: number;
  eps?: number;
  bps?: number;
  per?: number;
  pbr?: number;
  eps_ttm?: number;
  bps_ttm?: number;
  per_ttm?: number;
  pbr_ttm?: number;
  shares_outstanding?: number;
  market_cap?: number;
  as_of: string;
}

export type USPeriod = '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y' | '10y' | 'ytd' | 'max';
export type USInterval = '1m' | '5m' | '15m' | '30m' | '60m' | '1d' | '1wk' | '1mo';
