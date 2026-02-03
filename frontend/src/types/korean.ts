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
