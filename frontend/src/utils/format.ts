/**
 * Utility functions for formatting data.
 */

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

/**
 * Get color for price change (red for negative, green for positive).
 */
export function getChangeColor(change: number): string {
  if (change > 0) return '#22c55e'; // green
  if (change < 0) return '#ef4444'; // red
  return '#6b7280'; // gray
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
