/**
 * API service for basis and bond yield analytics.
 */

import axios from 'axios';
import type {
  KoreanBasisHistory,
  KoreanBasisSnapshot,
  KoreanBasisUnderlying,
  KoreanBondAnalytics,
  KoreanBondYieldHistory,
  KoreanOptionParity,
} from '../types/koreanAnalytics';

const API_BASE_URL = '/api';

export const koreanAnalyticsService = {
  /**
   * Stocks and indexes that have listed futures.
   */
  async getBasisUnderlyings(query?: string): Promise<KoreanBasisUnderlying[]> {
    const response = await axios.get<KoreanBasisUnderlying[]>(
      `${API_BASE_URL}/korean/basis/underlyings`,
      { params: query ? { query } : undefined }
    );
    return response.data;
  },

  /**
   * Spot against the nearest futures months. Leave `rate` out to use the
   * broker's theoretical price as fair value.
   */
  async getBasisSnapshot(
    underlying: string,
    params?: { rate?: number; dividend?: number; months?: number }
  ): Promise<KoreanBasisSnapshot> {
    const response = await axios.get<KoreanBasisSnapshot>(
      `${API_BASE_URL}/korean/basis/${encodeURIComponent(underlying)}`,
      { params }
    );
    return response.data;
  },

  /**
   * Daily basis of one contract (default: the front month).
   */
  async getBasisHistory(
    underlying: string,
    params?: { symbol?: string; days?: number }
  ): Promise<KoreanBasisHistory> {
    const response = await axios.get<KoreanBasisHistory>(
      `${API_BASE_URL}/korean/basis/${encodeURIComponent(underlying)}/history`,
      { params }
    );
    return response.data;
  },

  /**
   * Synthetic futures from put-call parity for one option month (default:
   * the nearest), against the futures of that month and spot.
   */
  async getOptionParity(
    underlying: string,
    params?: { expiry?: string; rate?: number; strikes?: number }
  ): Promise<KoreanOptionParity> {
    const response = await axios.get<KoreanOptionParity>(
      `${API_BASE_URL}/korean/basis/${encodeURIComponent(underlying)}/options`,
      { params }
    );
    return response.data;
  },

  /**
   * Yields at last/bid/ask, risk measures and pricing-agency spread.
   */
  async getBondAnalytics(pdno: string): Promise<KoreanBondAnalytics> {
    const response = await axios.get<KoreanBondAnalytics>(
      `${API_BASE_URL}/korean/bonds/${encodeURIComponent(pdno)}/analytics`
    );
    return response.data;
  },

  /**
   * Daily market yield against the pricing agencies' average yield.
   */
  async getBondYieldHistory(
    pdno: string,
    days?: number
  ): Promise<KoreanBondYieldHistory> {
    const response = await axios.get<KoreanBondYieldHistory>(
      `${API_BASE_URL}/korean/bonds/${encodeURIComponent(pdno)}/yield-history`,
      { params: days ? { days } : undefined }
    );
    return response.data;
  },
};
