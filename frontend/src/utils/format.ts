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
 *
 * For Korean figures use `formatKrwCompact` instead — Korean amounts are read
 * in 만 / 억 / 조, not thousands and millions.
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

const JO = 1e12;
const EOK = 1e8;
const MAN = 1e4;

/**
 * Format a won amount the way it is read in Korean: 348조 2,000억.
 *
 * Only the two largest non-zero units are shown, which is how figures are
 * quoted in practice — 348조 2,000억, not 348조 2,000억 5,000만 3,210원.
 */
export function formatKrwCompact(
  value: number | null | undefined,
  options: { withSymbol?: boolean } = {}
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }

  const sign = value < 0 ? '-' : '';
  const abs = Math.abs(value);
  const prefix = options.withSymbol ? '₩' : '';

  if (abs < MAN) {
    return `${sign}${prefix}${Math.round(abs).toLocaleString('ko-KR')}원`;
  }

  const units: Array<{ size: number; suffix: string }> = [
    { size: JO, suffix: '조' },
    { size: EOK, suffix: '억' },
    { size: MAN, suffix: '만' },
  ];

  const parts: string[] = [];
  let remainder = abs;

  for (const { size, suffix } of units) {
    const amount = Math.floor(remainder / size);
    remainder -= amount * size;
    if (amount > 0) {
      parts.push(`${amount.toLocaleString('ko-KR')}${suffix}`);
    }
    if (parts.length === 2) break;
  }

  return `${sign}${prefix}${parts.join(' ')}`;
}

/**
 * Format a won amount in 억원, the unit financial statements are read in.
 * State the unit once in the panel header rather than repeating it per row.
 */
export function formatEokKrw(
  value: number | null | undefined,
  decimals = 0
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return (value / EOK).toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Plain grouped number in the Korean locale. */
export function formatNumber(
  value: number | null | undefined,
  decimals = 0
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return value.toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Percentage with an explicit sign, or `-` when the value is missing. */
export function formatSignedPercent(
  value: number | null | undefined,
  decimals = 2
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return formatPercent(value, decimals);
}

/**
 * Format a `YYYYMMDD` string as `YYYY-MM-DD`.
 */
export function formatYyyymmdd(value?: string | null): string {
  if (!value || value.length !== 8 || value === '00000000') return '-';
  return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
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
 * Format a market-cap figure that arrives in 억 KRW, the unit the stock
 * master files use.
 */
export function formatMarketCapFrom100m(
  value: number | null | undefined
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return formatKrwCompact(value * EOK);
}

/**
 * Format an ISO timestamp as KST wall-clock time, for the "as of" label on
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
