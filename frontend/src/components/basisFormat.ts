/**
 * Number formatting and table/card styles shared by the basis views.
 */

import type React from 'react';

export const card: React.CSSProperties = {
  backgroundColor: 'white',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '16px',
  marginTop: '16px',
};
export const th: React.CSSProperties = {
  padding: '8px 10px',
  textAlign: 'right',
  borderBottom: '1px solid #e5e7eb',
  fontWeight: 600,
  color: '#374151',
  whiteSpace: 'nowrap',
};
export const td: React.CSSProperties = {
  padding: '8px 10px',
  textAlign: 'right',
  borderBottom: '1px solid #f3f4f6',
  whiteSpace: 'nowrap',
  fontVariantNumeric: 'tabular-nums',
};

export const isNumber = (value?: number | null): value is number =>
  value !== null && value !== undefined && Number.isFinite(value);

/** Index levels carry two decimals; stock prices are whole won. */
export const priceDigits = (kind?: string) => (kind === 'index' ? 2 : 0);

export const formatPrice = (value: number | null | undefined, digits: number) =>
  isNumber(value)
    ? value.toLocaleString('ko-KR', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      })
    : '-';

/** Rounds first, so a value that displays as zero carries no sign. */
const roundTo = (value: number, digits: number) => Number(value.toFixed(digits)) || 0;

export const formatSigned = (value: number | null | undefined, digits: number) => {
  if (!isNumber(value)) return '-';
  const rounded = roundTo(value, digits);
  return `${rounded > 0 ? '+' : ''}${rounded.toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}`;
};

export const formatSignedPercent = (value: number | null | undefined, digits = 2) => {
  if (!isNumber(value)) return '-';
  const rounded = roundTo(value, digits);
  return `${rounded > 0 ? '+' : ''}${rounded.toFixed(digits)}%`;
};

export const formatCount = (value?: number | null) =>
  isNumber(value) ? value.toLocaleString('ko-KR') : '-';
