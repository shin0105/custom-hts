/**
 * API service for US market data.
 */

import axios from 'axios';
import type {
  USStockQuote,
  USFinancialStatement,
  USCandleData,
  USPeriod,
  USInterval,
  USValuationMetrics,
} from '../types/us';

const API_BASE_URL = '/api';

export const usMarketService = {
  /**
   * Get real-time quote for a US stock.
   */
  async getQuote(symbol: string): Promise<USStockQuote> {
    const response = await axios.get<USStockQuote>(
      `${API_BASE_URL}/us/quote/${symbol}`
    );
    return response.data;
  },

  /**
   * Get financial statements for a US company.
   */
  async getFinancials(
    symbol: string,
    useCache = true
  ): Promise<USFinancialStatement[]> {
    const params = new URLSearchParams();
    params.append('use_cache', useCache.toString());

    const response = await axios.get<USFinancialStatement[]>(
      `${API_BASE_URL}/us/financials/${symbol}?${params}`
    );
    return response.data;
  },

  /**
   * Get historical candle data for a US stock.
   */
  async getHistoricalData(
    symbol: string,
    period: USPeriod = '1mo',
    interval: USInterval = '1d',
    start?: string,
    end?: string
  ): Promise<USCandleData[]> {
    const params = new URLSearchParams({
      period,
      interval,
    });
    if (start) params.append('start', start);
    if (end) params.append('end', end);

    const response = await axios.get<USCandleData[]>(
      `${API_BASE_URL}/us/candle/${symbol}?${params}`
    );
    return response.data;
  },

  /**
   * Get valuation metrics (PER/PBR/EPS/BPS) for a US stock.
   */
  async getValuation(symbol: string): Promise<USValuationMetrics> {
    const response = await axios.get<USValuationMetrics>(
      `${API_BASE_URL}/us/valuation/${symbol}`
    );
    return response.data;
  },
};
