/**
 * StockCard component for displaying stock quote information.
 */

import React from 'react';
import {
  formatCurrency,
  formatKrwCompact,
  formatKstTimestamp,
  formatLargeNumber,
  formatNumber,
  formatPercent,
} from '../utils/format';
import { useMarketColors } from '../theme/marketColorContext';
import type { ColorConvention } from '../utils/marketColors';
import { color, fontSize, fontWeight, radius, shadow, space, tabularNums } from '../theme/tokens';

interface StockCardProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  currency: 'USD' | 'KRW';
  /** Pins the up/down colors instead of following the user's preference. */
  colorConvention?: ColorConvention;
  /**
   * Session figures the quote endpoint already returns. Supplied where the
   * caller has them; omitted fields are simply not rendered.
   */
  open?: number | null;
  high?: number | null;
  low?: number | null;
  previousClose?: number | null;
  volume?: number | null;
  marketCap?: number | null;
  sharesOutstanding?: number | null;
  timestamp?: string | null;
}

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent,
  currency,
  colorConvention,
  open,
  high,
  low,
  previousClose,
  volume,
  marketCap,
  sharesOutstanding,
  timestamp,
}) => {
  const { colorForDirection, directionOf, glyphFor, labelFor } =
    useMarketColors(colorConvention);
  const direction = directionOf(undefined, change);
  const changeColor = colorForDirection(direction);
  const isKrw = currency === 'KRW';

  const price = (value: number | null | undefined) =>
    value === null || value === undefined ? '-' : formatCurrency(value, currency);

  const bigNumber = (value: number | null | undefined) => {
    if (value === null || value === undefined) return '-';
    return isKrw ? formatKrwCompact(value) : formatLargeNumber(value);
  };

  // Where the current price sits inside the day's range, as a percentage.
  const hasRange =
    high !== null &&
    high !== undefined &&
    low !== null &&
    low !== undefined &&
    high > low;
  const rangePosition = hasRange
    ? ((currentPrice - low) / (high - low)) * 100
    : 0;

  const stats: Array<{ label: string; value: string }> = [
    { label: '시가', value: price(open) },
    { label: '고가', value: price(high) },
    { label: '저가', value: price(low) },
    { label: '전일종가', value: price(previousClose) },
    {
      label: '거래량',
      value:
        volume === null || volume === undefined ? '-' : formatNumber(volume),
    },
  ];

  if (marketCap !== null && marketCap !== undefined) {
    stats.push({ label: '시가총액', value: bigNumber(marketCap) });
  }
  if (sharesOutstanding !== null && sharesOutstanding !== undefined) {
    stats.push({ label: '상장주식수', value: formatNumber(sharesOutstanding) });
  }

  const hasStats = stats.some((stat) => stat.value !== '-');

  return (
    <div
      style={{
        border: `1px solid ${color.border}`,
        borderRadius: radius.lg,
        padding: space.lg,
        backgroundColor: color.surface,
        boxShadow: shadow.panel,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: space.sm,
          marginBottom: space.sm,
          flexWrap: 'wrap',
        }}
      >
        <span style={{ fontWeight: fontWeight.bold, fontSize: fontSize.xl }}>
          {name || symbol}
        </span>
        <span
          className="hts-mono"
          style={{ color: color.inkDim, fontSize: fontSize.md }}
        >
          {symbol}
        </span>
        {timestamp && (
          <span
            style={{
              marginLeft: 'auto',
              fontSize: fontSize.sm,
              color: color.inkDim,
            }}
          >
            {isKrw ? `${formatKstTimestamp(timestamp)} KST` : timestamp} 기준
          </span>
        )}
      </div>
      <div
        style={{
          fontSize: '30px',
          fontWeight: fontWeight.bold,
          color: changeColor,
          lineHeight: 1.2,
          ...tabularNums,
        }}
      >
        {formatCurrency(currentPrice, currency)}
      </div>
      <div
        style={{
          color: changeColor,
          fontSize: fontSize.lg,
          marginTop: space.xs,
          ...tabularNums,
        }}
      >
        <span aria-hidden="true">{glyphFor(direction)}</span>{' '}
        {formatCurrency(Math.abs(change), currency)} ({formatPercent(changePercent)})
        {/* Direction is also stated in text so it does not rely on color alone. */}
        <span
          style={{
            marginLeft: space.sm,
            fontSize: fontSize.sm,
            color: color.inkDim,
          }}
        >
          {labelFor(direction)}
        </span>
      </div>

      {hasRange && (
        <div style={{ marginTop: space.lg }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: fontSize.sm,
              color: color.inkDim,
              marginBottom: space.xs,
              ...tabularNums,
            }}
          >
            <span>{price(low)}</span>
            <span>일중 범위</span>
            <span>{price(high)}</span>
          </div>
          <div
            style={{
              position: 'relative',
              height: '6px',
              borderRadius: radius.pill,
              backgroundColor: color.surfaceSunken,
            }}
            role="img"
            aria-label={`일중 범위 ${price(low)} ~ ${price(
              high
            )}, 현재가 ${price(currentPrice)}`}
          >
            <div
              style={{
                position: 'absolute',
                top: '-3px',
                left: `calc(${Math.min(100, Math.max(0, rangePosition))}% - 6px)`,
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: changeColor,
                border: `2px solid ${color.surface}`,
                boxShadow: shadow.panel,
              }}
            />
          </div>
        </div>
      )}

      {hasStats && (
        <div
          style={{
            marginTop: space.lg,
            paddingTop: space.md,
            borderTop: `1px solid ${color.borderSoft}`,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
            gap: space.md,
          }}
        >
          {stats.map((stat) => (
            <div key={stat.label} style={{ minWidth: 0 }}>
              <div style={{ fontSize: fontSize.sm, color: color.inkDim }}>
                {stat.label}
              </div>
              <div
                style={{
                  fontSize: fontSize.md,
                  fontWeight: fontWeight.semibold,
                  color: color.ink,
                  ...tabularNums,
                }}
              >
                {stat.value}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
