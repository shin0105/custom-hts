/**
 * API service for US market data.
 */

import axios from 'axios';
import type { USStockQuote, USFinancialStatement } from '../types/us';

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
};
