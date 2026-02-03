/**
 * StockCard component for displaying stock quote information.
 */

import React from 'react';
import { formatCurrency, formatPercent, getChangeColor } from '../utils/format';

interface StockCardProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  currency: 'USD' | 'KRW';
}

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent,
  currency,
}) => {
  const changeColor = getChangeColor(change);

  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        backgroundColor: 'white',
      }}
    >
      <div style={{ marginBottom: '8px' }}>
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
      <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '4px' }}>
        {formatCurrency(currentPrice, currency)}
      </div>
      <div style={{ color: changeColor, fontSize: '16px' }}>
        {formatCurrency(change, currency)} ({formatPercent(changePercent)})
      </div>
    </div>
  );
};
