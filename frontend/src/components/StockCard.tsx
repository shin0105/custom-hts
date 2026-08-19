/**
 * StockCard component for displaying stock quote information.
 */

import React from 'react';
import { formatCurrency, formatPercent } from '../utils/format';
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
}

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent,
  currency,
  colorConvention,
}) => {
  const { colorForDirection, directionOf, glyphFor, labelFor } =
    useMarketColors(colorConvention);
  const direction = directionOf(undefined, change);
  const changeColor = colorForDirection(direction);

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
    </div>
  );
};
