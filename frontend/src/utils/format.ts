/**
 * Utility functions for formatting data.
 */

/**
 * Market colour convention for price movement.
 *
 * Korean markets colour rises red (상승) and falls blue (하락), which is the
 * inverse of the US convention. Rendering KR data with US colours makes every
 * chart read backwards to a Korean user, so the convention travels with the
 * market rather than being hard-coded.
 */
export type MarketConvention = 'KR' | 'US';

export interface MarketColors {
  up: string;
  down: string;
  flat: string;
}

export const MARKET_COLORS: Record<MarketConvention, MarketColors> = {
  KR: {
    up: '#dc2626', // red — 상승
    down: '#2563eb', // blue — 하락
    flat: '#6b7280',
  },
  US: {
    up: '#16a34a', // green
    down: '#dc2626', // red
    flat: '#6b7280',
  },
};

/**
 * Resolve the colour convention that applies to a currency.
 */
export function conventionForCurrency(
  currency: 'USD' | 'KRW'
): MarketConvention {
  return currency === 'KRW' ? 'KR' : 'US';
}

/**
 * Get the colour palette for a market convention.
 */
export function getMarketColors(
  convention: MarketConvention = 'US'
): MarketColors {
  return MARKET_COLORS[convention];
}

/**
 * Format a number as currency.
 */
export function formatCurrency(
  amount: number,
  currency: 'USD' | 'KRW' = 'USD',
  decimals = 2
): string {
  if (currency === 'KRW') {
    return `₩${amount.toLocaleString('ko-KR', {
      maximumFractionDigits: 0,
    })}`;
  }
  return `$${amount.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format a number as a percentage.
 */
export function formatPercent(value: number, decimals = 2): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format a large number in abbreviated form (K, M, B).
 */
export function formatLargeNumber(num: number): string {
  if (num >= 1e9) {
    return `${(num / 1e9).toFixed(2)}B`;
  }
  if (num >= 1e6) {
    return `${(num / 1e6).toFixed(2)}M`;
  }
  if (num >= 1e3) {
    return `${(num / 1e3).toFixed(2)}K`;
  }
  return num.toFixed(2);
}

const JO = 1e12; // 조
const EOK = 1e8; // 억
const MAN = 1e4; // 만

/**
 * Format a KRW amount using Korean 조/억/만 units.
 *
 * DART reports raw won figures, so a revenue line arrives as
 * 279604799000000 — unreadable as digits. Korean readers parse this as
 * "279.6조" at a glance.
 */
export function formatKoreanUnits(
  value: number | null | undefined,
  decimals = 1
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  const sign = value < 0 ? '-' : '';
  const abs = Math.abs(value);

  if (abs >= JO) return `${sign}${(abs / JO).toFixed(decimals)}조`;
  if (abs >= EOK) return `${sign}${(abs / EOK).toFixed(decimals)}억`;
  if (abs >= MAN) return `${sign}${(abs / MAN).toFixed(decimals)}만`;
  return `${sign}${abs.toLocaleString('ko-KR', { maximumFractionDigits: 2 })}`;
}

/**
 * Format a KRW amount in Korean units with the exact figure alongside, for
 * places where the precise number still matters (tooltips, table cells).
 */
export function formatKoreanUnitsDetailed(
  value: number | null | undefined
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  if (Math.abs(value) < MAN) {
    return value.toLocaleString('ko-KR', { maximumFractionDigits: 2 });
  }
  return `${formatKoreanUnits(value)} (${value.toLocaleString('ko-KR')})`;
}

/**
 * Format a market-cap figure expressed in 억 KRW (stock master unit).
 */
export function formatMarketCapFrom100m(
  value: number | null | undefined
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return formatKoreanUnits(value * EOK);
}

/**
 * Get color for a price change under a market's colour convention.
 */
export function getChangeColor(
  change: number,
  convention: MarketConvention = 'US'
): string {
  const colors = getMarketColors(convention);
  if (change > 0) return colors.up;
  if (change < 0) return colors.down;
  return colors.flat;
}

/**
 * Format date string to readable format.
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format an ISO timestamp as a KST wall-clock time, for "as of" labels on
 * Korean market data.
 */
export function formatKstTimestamp(value: string | null | undefined): string {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}
