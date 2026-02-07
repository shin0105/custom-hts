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

export type ChartInterval = 'daily' | 'minute';
export type MinuteInterval = 1 | 5 | 10 | 30 | 60;
export type PeriodType = 'D' | 'W' | 'M';
