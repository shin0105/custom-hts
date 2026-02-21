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
  KoreanAccountResponse,
  KoreanValuationMetrics,
  KoreanEstimatePerform,
  KoreanBondMasterResponse,
  KoreanBondQuote,
  KoreanBondInfo,
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
   * Get valuation metrics (PER/PBR/EPS/BPS) for a Korean stock.
   */
  async getValuation(
    symbol: string,
    year?: number,
    quarter?: number,
    fsDivision: 'CFS' | 'OFS' = 'CFS'
  ): Promise<KoreanValuationMetrics> {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (quarter) params.append('quarter', quarter.toString());
    params.append('fs_div', fsDivision);

    const response = await axios.get<KoreanValuationMetrics>(
      `${API_BASE_URL}/korean/valuation/${symbol}?${params}`
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
    limit?: number,
    startDate?: string,
    endDate?: string
  ): Promise<KoreanCandleData[]> {
    const params = new URLSearchParams({
      period,
      adjust_price: adjustPrice.toString(),
    });
    if (limit !== undefined) {
      params.append('limit', limit.toString());
    }
    if (startDate) {
      params.append('start_date', startDate);
    }
    if (endDate) {
      params.append('end_date', endDate);
    }

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
    limit?: number,
    date?: string,
    timeStr?: string
  ): Promise<KoreanCandleData[]> {
    const params = new URLSearchParams({
      interval: interval.toString(),
    });
    if (limit !== undefined) {
      params.append('limit', limit.toString());
    }
    if (date) {
      params.append('date', date);
    }
    if (timeStr) {
      params.append('time_str', timeStr);
    }

    const response = await axios.get<KoreanCandleData[]>(
      `${API_BASE_URL}/korean/candle-minute/${symbol}?${params}`
    );
    return response.data;
  },

  /**
   * Get comprehensive financial statements from DART API.
   * Returns all financial line items including balance sheet, income statement, and cash flow.
   */
  async getAllFinancials(
    symbol: string,
    year?: number,
    quarter?: number,
    fsDivision: 'CFS' | 'OFS' = 'CFS'
  ): Promise<any> {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (quarter) params.append('quarter', quarter.toString());
    params.append('fs_div', fsDivision);

    const response = await axios.get(
      `${API_BASE_URL}/korean/financials/${symbol}/all?${params}`
    );
    return response.data;
  },

  /**
   * Get Korean account balance and positions.
   */
  async getAccountBalance(accountProductCode = '01'): Promise<KoreanAccountResponse> {
    const params = new URLSearchParams({ account_product_code: accountProductCode });
    const response = await axios.get<KoreanAccountResponse>(
      `${API_BASE_URL}/korean/account?${params}`
    );
    return response.data;
  },

  /**
   * Get estimated performance data for a Korean stock.
   */
  async getEstimatePerform(symbol: string): Promise<KoreanEstimatePerform> {
    const response = await axios.get<KoreanEstimatePerform>(
      `${API_BASE_URL}/korean/estimate-perform/${symbol}`
    );
    return response.data;
  },

  /**
   * Get domestic listed bond master rows.
   */
  async getBondMaster(params?: {
    query?: string;
    offset?: number;
    limit?: number;
    enrich?: boolean;
    includeQuotes?: boolean;
  }): Promise<KoreanBondMasterResponse> {
    const search = new URLSearchParams();
    if (params?.query) search.append('query', params.query);
    if (params?.offset !== undefined) search.append('offset', String(params.offset));
    if (params?.limit !== undefined) search.append('limit', String(params.limit));
    if (params?.enrich !== undefined) search.append('enrich', String(params.enrich));
    if (params?.includeQuotes !== undefined) {
      search.append('include_quotes', String(params.includeQuotes));
    }

    const response = await axios.get<KoreanBondMasterResponse>(
      `${API_BASE_URL}/korean/bonds/master?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic listed bond current quote.
   */
  async getBondPrice(pdno: string): Promise<KoreanBondQuote> {
    const response = await axios.get<KoreanBondQuote>(
      `${API_BASE_URL}/korean/bonds/${pdno}/price`
    );
    return response.data;
  },

  /**
   * Get domestic listed bond basic info via search-bond-info API
   * (장내채권 기본조회, CTPF1114R).
   */
  async getBondInfo(pdno: string): Promise<KoreanBondInfo> {
    const response = await axios.get<KoreanBondInfo>(
      `${API_BASE_URL}/korean/bonds/${encodeURIComponent(pdno)}/info`
    );
    return response.data;
  },

  /**
   * Get domestic listed bond daily prices (장내채권현재가(일별)).
   */
  async getBondDailyPrice(
    pdno: string,
    limit?: number
  ): Promise<KoreanCandleData[]> {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append('limit', String(limit));
    const query = params.toString();
    const response = await axios.get<KoreanCandleData[]>(
      `${API_BASE_URL}/korean/bonds/${encodeURIComponent(pdno)}/daily-price${
        query ? `?${query}` : ''
      }`
    );
    return response.data;
  },
};
