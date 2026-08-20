/**
 * React Query hooks for Korean market data.
 *
 * Each panel on the Korean market page owns its own query, so a failure or a
 * refetch in one panel never blanks the others, and changing symbol fetches
 * each resource exactly once — the hand-rolled version loaded valuation,
 * financials and estimates twice per search (once eagerly, once from an effect
 * keyed on the arriving quote).
 */

import { useQuery } from '@tanstack/react-query';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  ChartInterval,
  KoreanAllFinancialsResponse,
  KoreanCandleData,
  KoreanEstimatePerform,
  KoreanStockQuote,
  KoreanValuationMetrics,
  MinuteInterval,
  PeriodType,
} from '../types/korean';

export interface FinancialParams {
  year: number;
  quarter?: number;
  fsDivision: 'CFS' | 'OFS';
}

export interface ChartParams {
  interval: ChartInterval;
  period: PeriodType;
  minuteInterval: MinuteInterval;
  date: string;
  time: string;
  startDate: string;
  endDate: string;
}

/** Today's date in KST as YYYYMMDD. */
export function todayInKst(): string {
  const now = new Date();
  const kst = new Date(now.getTime() + 9 * 60 * 60 * 1000);
  return kst.toISOString().split('T')[0].replace(/-/g, '');
}

export function useKoreanQuote(symbol: string, enabled: boolean) {
  return useQuery<KoreanStockQuote>({
    queryKey: ['korean', 'quote', symbol],
    queryFn: () => koreanMarketService.getQuote(symbol),
    enabled: enabled && symbol.trim() !== '',
  });
}

export function useKoreanValuation(
  symbol: string,
  params: FinancialParams,
  enabled: boolean
) {
  return useQuery<KoreanValuationMetrics>({
    queryKey: [
      'korean',
      'valuation',
      symbol,
      params.year,
      params.quarter ?? null,
      params.fsDivision,
    ],
    queryFn: () =>
      koreanMarketService.getValuation(
        symbol,
        params.year,
        params.quarter,
        params.fsDivision
      ),
    enabled: enabled && symbol.trim() !== '',
  });
}

export function useKoreanFinancials(
  symbol: string,
  params: FinancialParams,
  enabled: boolean
) {
  return useQuery<KoreanAllFinancialsResponse>({
    queryKey: [
      'korean',
      'financials',
      symbol,
      params.year,
      params.quarter ?? null,
      params.fsDivision,
    ],
    queryFn: () =>
      koreanMarketService.getAllFinancials(
        symbol,
        params.year,
        params.quarter,
        params.fsDivision
      ),
    enabled: enabled && symbol.trim() !== '',
  });
}

export function useKoreanEstimates(symbol: string, enabled: boolean) {
  return useQuery<KoreanEstimatePerform>({
    queryKey: ['korean', 'estimates', symbol],
    queryFn: () => koreanMarketService.getEstimatePerform(symbol),
    enabled: enabled && symbol.trim() !== '',
  });
}

export function useKoreanCandles(
  symbol: string,
  params: ChartParams,
  enabled: boolean
) {
  const effectiveDate = params.date || todayInKst();

  return useQuery<KoreanCandleData[]>({
    queryKey:
      params.interval === 'daily'
        ? [
            'korean',
            'candles',
            'daily',
            symbol,
            params.period,
            params.startDate,
            params.endDate,
          ]
        : [
            'korean',
            'candles',
            'minute',
            symbol,
            params.minuteInterval,
            effectiveDate,
            params.time,
          ],
    queryFn: () => {
      if (params.interval === 'daily') {
        return koreanMarketService.getDailyCandle(
          symbol,
          params.period,
          true,
          undefined,
          params.startDate || undefined,
          params.endDate || undefined
        );
      }
      return koreanMarketService.getMinuteCandle(
        symbol,
        params.minuteInterval,
        undefined,
        effectiveDate,
        params.time ? `${params.time.replace(':', '')}00` : undefined
      );
    },
    enabled: enabled && symbol.trim() !== '',
  });
}
