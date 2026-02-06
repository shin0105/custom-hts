/**
 * API service for Korean market data.
 */

import axios from 'axios';
import type {
  KoreanStockQuote,
  KoreanFinancialStatement,
  KoreanCandleData,
  PeriodType,
  MinuteInterval,
} from '../types/korean';

const API_BASE_URL = '/api';

export const koreanMarketService = {
  /**
   * Get real-time quote for a Korean stock.
   */
  async getQuote(symbol: string): Promise<KoreanStockQuote> {
    const response = await axios.get<KoreanStockQuote>(
      `${API_BASE_URL}/korean/quote/${symbol}`
    );
    return response.data;
  },

  /**
   * Get financial statements for a Korean company.
   */
  async getFinancials(
    symbol: string,
    year?: number,
    quarter?: number,
    useCache = true
  ): Promise<KoreanFinancialStatement> {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (quarter) params.append('quarter', quarter.toString());
    params.append('use_cache', useCache.toString());

    const response = await axios.get<KoreanFinancialStatement>(
      `${API_BASE_URL}/korean/financials/${symbol}?${params}`
    );
    return response.data;
  },

  /**
   * Get daily/period candle data for a Korean stock.
   */
  async getDailyCandle(
    symbol: string,
    period: PeriodType = 'D',
    adjustPrice = true,
    limit = 100
  ): Promise<KoreanCandleData[]> {
    const params = new URLSearchParams({
      period,
      adjust_price: adjustPrice.toString(),
      limit: limit.toString(),
    });

    const response = await axios.get<KoreanCandleData[]>(
      `${API_BASE_URL}/korean/candle/${symbol}?${params}`
    );
    return response.data;
  },

  /**
   * Get minute candle data for a Korean stock.
   */
  async getMinuteCandle(
    symbol: string,
    interval: MinuteInterval = 1,
    limit = 100,
    date?: string
  ): Promise<KoreanCandleData[]> {
    const params = new URLSearchParams({
      interval: interval.toString(),
      limit: limit.toString(),
    });
    if (date) {
      params.append('date', date);
    }

    const response = await axios.get<KoreanCandleData[]>(
      `${API_BASE_URL}/korean/candle-minute/${symbol}?${params}`
    );
    return response.data;
  },
};
