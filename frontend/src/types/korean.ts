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

export type ChartInterval = 'daily' | 'minute';
export type MinuteInterval = 1 | 5 | 10 | 30 | 60;
export type PeriodType = 'D' | 'W' | 'M';
