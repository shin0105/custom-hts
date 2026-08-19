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
  KoreanAllFinancialsResponse,
  KoreanBondMasterResponse,
  KoreanBondQuote,
  KoreanBondInfo,
  KoreanBondValuation,
  KoreanFuturesOptionsMasterResponse,
  KoreanFuturesOptionQuote,
  KoreanFuturesOptionOrderbook,
  KoreanFuturesOptionMinuteCandleResponse,
  KoreanFuturesOptionChainResponse,
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
  ): Promise<KoreanAllFinancialsResponse> {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (quarter) params.append('quarter', quarter.toString());
    params.append('fs_div', fsDivision);

    const response = await axios.get<KoreanAllFinancialsResponse>(
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
    bondType?: string;
    bondClassCode?: string;
    bondInterestClassCode?: string;
    listedDateFrom?: string;
    listedDateTo?: string;
    issueDateFrom?: string;
    issueDateTo?: string;
    maturityDateFrom?: string;
    maturityDateTo?: string;
    offset?: number;
    limit?: number;
    enrich?: boolean;
    includeQuotes?: boolean;
  }): Promise<KoreanBondMasterResponse> {
    const search = new URLSearchParams();
    if (params?.query) search.append('query', params.query);
    if (params?.bondType) search.append('type', params.bondType);
    if (params?.bondClassCode) search.append('bond_class_code', params.bondClassCode);
    if (params?.bondInterestClassCode) {
      search.append('bond_interest_class_code', params.bondInterestClassCode);
    }
    if (params?.listedDateFrom) search.append('listed_date_from', params.listedDateFrom);
    if (params?.listedDateTo) search.append('listed_date_to', params.listedDateTo);
    if (params?.issueDateFrom) search.append('issue_date_from', params.issueDateFrom);
    if (params?.issueDateTo) search.append('issue_date_to', params.issueDateTo);
    if (params?.maturityDateFrom) {
      search.append('maturity_date_from', params.maturityDateFrom);
    }
    if (params?.maturityDateTo) search.append('maturity_date_to', params.maturityDateTo);
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
   * Get domestic listed bond valuation using basic info + price data.
   */
  async getBondValuation(pdno: string): Promise<KoreanBondValuation> {
    const response = await axios.get<KoreanBondValuation>(
      `${API_BASE_URL}/korean/bonds/${encodeURIComponent(pdno)}/valuation`
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

  /**
   * Get domestic futures/options master rows.
   */
  async getFuturesOptionsMaster(params?: {
    market?: 'all' | 'index' | 'stock' | 'commodity';
    query?: string;
    infoType?: string;
    underlyingShortCode?: string;
    offset?: number;
    limit?: number;
    autoDownload?: boolean;
    forceDownload?: boolean;
  }): Promise<KoreanFuturesOptionsMasterResponse> {
    const search = new URLSearchParams();
    if (params?.market) search.append('market', params.market);
    if (params?.query) search.append('query', params.query);
    if (params?.infoType) search.append('info_type', params.infoType);
    if (params?.underlyingShortCode) {
      search.append('underlying_short_code', params.underlyingShortCode);
    }
    if (params?.offset !== undefined) search.append('offset', String(params.offset));
    if (params?.limit !== undefined) search.append('limit', String(params.limit));
    if (params?.autoDownload !== undefined) {
      search.append('auto_download', String(params.autoDownload));
    }
    if (params?.forceDownload !== undefined) {
      search.append('force_download', String(params.forceDownload));
    }

    const response = await axios.get<KoreanFuturesOptionsMasterResponse>(
      `${API_BASE_URL}/korean/futures-options/master?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic futures/options quote.
   */
  async getFuturesOptionQuote(params: {
    symbol: string;
    marketDivCode?: 'F' | 'O' | 'JF' | 'JO' | 'CF' | 'CM' | 'EU';
  }): Promise<KoreanFuturesOptionQuote> {
    const search = new URLSearchParams();
    search.append('symbol', params.symbol);
    if (params.marketDivCode) {
      search.append('market_div_code', params.marketDivCode);
    }
    const response = await axios.get<KoreanFuturesOptionQuote>(
      `${API_BASE_URL}/korean/futures-options/quote?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic futures/options 5-level orderbook.
   */
  async getFuturesOptionOrderbook(params: {
    symbol: string;
    marketDivCode?: 'F' | 'O' | 'JF' | 'JO' | 'CF' | 'CM' | 'EU';
  }): Promise<KoreanFuturesOptionOrderbook> {
    const search = new URLSearchParams();
    search.append('symbol', params.symbol);
    if (params.marketDivCode) {
      search.append('market_div_code', params.marketDivCode);
    }
    const response = await axios.get<KoreanFuturesOptionOrderbook>(
      `${API_BASE_URL}/korean/futures-options/orderbook?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic futures/options daily candles.
   */
  async getFuturesOptionDailyCandles(params: {
    symbol: string;
    marketDivCode?: 'F' | 'O' | 'JF' | 'JO' | 'CF' | 'CM' | 'EU';
    period?: 'D' | 'W' | 'M' | 'Y';
    limit?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<KoreanCandleData[]> {
    const search = new URLSearchParams();
    search.append('symbol', params.symbol);
    if (params.marketDivCode) {
      search.append('market_div_code', params.marketDivCode);
    }
    if (params.period) {
      search.append('period', params.period);
    }
    if (params.limit !== undefined) search.append('limit', String(params.limit));
    if (params.startDate) search.append('start_date', params.startDate);
    if (params.endDate) search.append('end_date', params.endDate);
    const response = await axios.get<KoreanCandleData[]>(
      `${API_BASE_URL}/korean/futures-options/daily-candles?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic futures/options minute candles.
   */
  async getFuturesOptionMinuteCandles(params: {
    symbol: string;
    marketDivCode?: 'F' | 'O' | 'JF' | 'JO' | 'CF' | 'CM' | 'EU';
    timeframeSec?: 30 | 60 | 3600;
    date?: string;
    time?: string;
    includePrevious?: boolean;
    includeFakeTick?: boolean;
    limit?: number;
  }): Promise<KoreanFuturesOptionMinuteCandleResponse> {
    const search = new URLSearchParams();
    search.append('symbol', params.symbol);
    search.append('timeframe_sec', String(params.timeframeSec ?? 60));
    if (params.marketDivCode) {
      search.append('market_div_code', params.marketDivCode);
    }
    if (params.date) search.append('date', params.date);
    if (params.time) search.append('time', params.time);
    if (params.includePrevious !== undefined) {
      search.append('include_previous', String(params.includePrevious));
    }
    if (params.includeFakeTick !== undefined) {
      search.append('include_fake_tick', String(params.includeFakeTick));
    }
    if (params.limit !== undefined) search.append('limit', String(params.limit));

    const response = await axios.get<KoreanFuturesOptionMinuteCandleResponse>(
      `${API_BASE_URL}/korean/futures-options/minute-candles?${search.toString()}`
    );
    return response.data;
  },

  /**
   * Get domestic futures/options option chain (call/put).
   */
  async getFuturesOptionChain(params: {
    expiry: string;
    marketClass?: '' | 'MKI' | 'KQI' | 'WKM' | 'WKI';
  }): Promise<KoreanFuturesOptionChainResponse> {
    const search = new URLSearchParams();
    search.append('expiry', params.expiry);
    if (params.marketClass !== undefined) {
      search.append('market_class', params.marketClass);
    }
    const response = await axios.get<KoreanFuturesOptionChainResponse>(
      `${API_BASE_URL}/korean/futures-options/option-chain?${search.toString()}`
    );
    return response.data;
  },
};
