/**
 * StockCard component for displaying stock quote information.
 */

import React from 'react';
import {
  conventionForCurrency,
  formatCurrency,
  formatKoreanUnits,
  formatKstTimestamp,
  formatLargeNumber,
  formatPercent,
  getChangeColor,
} from '../utils/format';

interface StockCardProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  currency: 'USD' | 'KRW';
  open?: number | null;
  high?: number | null;
  low?: number | null;
  previousClose?: number | null;
  volume?: number | null;
  marketCap?: number | null;
  sharesOutstanding?: number | null;
  timestamp?: string | null;
}

const labelStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#6b7280',
};

const valueStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  color: '#0f172a',
};

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent,
  currency,
  open,
  high,
  low,
  previousClose,
  volume,
  marketCap,
  sharesOutstanding,
  timestamp,
}) => {
  const convention = conventionForCurrency(currency);
  const changeColor = getChangeColor(change, convention);
  const isKrw = currency === 'KRW';

  const price = (value: number | null | undefined) =>
    value === null || value === undefined
      ? '-'
      : formatCurrency(value, currency);

  const bigNumber = (value: number | null | undefined) => {
    if (value === null || value === undefined) return '-';
    return isKrw ? formatKoreanUnits(value) : formatLargeNumber(value);
  };

  // Position of the current price inside the day's range, as a percentage.
  const hasRange =
    high !== null &&
    high !== undefined &&
    low !== null &&
    low !== undefined &&
    high > low;
  const rangePosition = hasRange
    ? ((currentPrice - (low as number)) / ((high as number) - (low as number))) *
      100
    : null;

  const stats: Array<{ label: string; value: string }> = [
    { label: 'Open', value: price(open) },
    { label: 'High', value: price(high) },
    { label: 'Low', value: price(low) },
    { label: 'Prev Close', value: price(previousClose) },
    {
      label: 'Volume',
      value:
        volume === null || volume === undefined
          ? '-'
          : volume.toLocaleString(isKrw ? 'ko-KR' : 'en-US'),
    },
  ];

  if (marketCap !== null && marketCap !== undefined) {
    stats.push({ label: 'Market Cap', value: bigNumber(marketCap) });
  }
  if (sharesOutstanding !== null && sharesOutstanding !== undefined) {
    stats.push({ label: 'Shares Out', value: bigNumber(sharesOutstanding) });
  }

  const hasStats = stats.some((stat) => stat.value !== '-');

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        backgroundColor: 'white',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px',
          marginBottom: '8px',
        }}
      >
        <div>
          <span
            style={{
              fontWeight: 'bold',
              fontSize: '18px',
              marginRight: '8px',
            }}
          >
            {symbol}
          </span>
          <span style={{ color: '#6b7280', fontSize: '14px' }}>{name}</span>
        </div>
        {timestamp && (
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>
            As of {isKrw ? formatKstTimestamp(timestamp) : timestamp} {isKrw && 'KST'}
          </span>
        )}
      </div>

      <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '4px' }}>
        {formatCurrency(currentPrice, currency)}
      </div>
      <div style={{ color: changeColor, fontSize: '16px' }}>
        {formatCurrency(change, currency)} ({formatPercent(changePercent)})
      </div>

      {hasRange && (
        <div style={{ marginTop: '14px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '12px',
              color: '#6b7280',
              marginBottom: '4px',
            }}
          >
            <span>{price(low)}</span>
            <span>Day range</span>
            <span>{price(high)}</span>
          </div>
          <div
            style={{
              position: 'relative',
              height: '6px',
              borderRadius: '999px',
              backgroundColor: '#e5e7eb',
            }}
            role="img"
            aria-label={`Day range from ${price(low)} to ${price(
              high
            )}, current ${price(currentPrice)}`}
          >
            <div
              style={{
                position: 'absolute',
                top: '-3px',
                left: `calc(${Math.min(
                  100,
                  Math.max(0, rangePosition ?? 0)
                )}% - 6px)`,
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: changeColor,
                border: '2px solid white',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}
            />
          </div>
        </div>
      )}

      {hasStats && (
        <div
          style={{
            marginTop: '16px',
            paddingTop: '12px',
            borderTop: '1px solid #f1f5f9',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
            gap: '12px',
          }}
        >
          {stats.map((stat) => (
            <div key={stat.label}>
              <div style={labelStyle}>{stat.label}</div>
              <div style={valueStyle}>{stat.value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
