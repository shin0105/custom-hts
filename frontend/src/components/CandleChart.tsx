/**
 * CandleChart component for displaying candlestick charts with volume.
 */

import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export interface CandleData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandleChartProps {
  data: CandleData[];
  currency?: 'USD' | 'KRW';
  height?: number;
}

// Custom tooltip
const CustomTooltip: React.FC<any> = ({ active, payload, currency = 'USD' }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const isPositive = data.close >= data.open;
  const change = data.close - data.open;
  const changePercent = data.open !== 0 ? ((change / data.open) * 100).toFixed(2) : '0.00';

  const formatPrice = (value: number) => {
    if (currency === 'KRW') {
      return `₩${value.toLocaleString()}`;
    }
    return `$${value.toFixed(2)}`;
  };

  const formatVolume = (value: number) => {
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(2)}M`;
    } else if (value >= 1_000) {
      return `${(value / 1_000).toFixed(2)}K`;
    }
    return value.toLocaleString();
  };

  return (
    <div
      style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '6px',
        padding: '12px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>{data.date}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Open: {formatPrice(data.open)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>High: {formatPrice(data.high)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Low: {formatPrice(data.low)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Close: {formatPrice(data.close)}</p>
      <p
        style={{
          margin: '4px 0',
          fontSize: '14px',
          color: isPositive ? '#10b981' : '#ef4444',
        }}
      >
        Change: {formatPrice(Math.abs(change))} ({isPositive ? '+' : '-'}
        {Math.abs(parseFloat(changePercent))}%)
      </p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Volume: {formatVolume(data.volume)}</p>
    </div>
  );
};

export const CandleChart: React.FC<CandleChartProps> = ({
  data,
  currency = 'USD',
  height = 500,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
        }}
      >
        <p style={{ color: '#6b7280' }}>No chart data available</p>
      </div>
    );
  }

  // Calculate price range for Y-axis domain
  const allPrices = data.flatMap((d) => [d.high, d.low]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const padding = (maxPrice - minPrice) * 0.1;

  // Calculate max volume for secondary Y-axis (unused but kept for potential future use)
  // const maxVolume = Math.max(...data.map((d) => d.volume));

  // Format date for display
  const formatDate = (dateStr: string) => {
    if (dateStr.length === 8) {
      // YYYYMMDD format
      return `${dateStr.slice(4, 6)}/${dateStr.slice(6, 8)}`;
    } else if (dateStr.length >= 12) {
      // YYYYMMDDHHMMSS format
      return `${dateStr.slice(8, 10)}:${dateStr.slice(10, 12)}`;
    }
    return dateStr;
  };

  // Prepare data with formatted dates
  const chartData = data.map((d) => ({
    ...d,
    displayDate: formatDate(d.date),
  }));

  const formatVolume = (value: number) => {
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(1)}M`;
    } else if (value >= 1_000) {
      return `${(value / 1_000).toFixed(1)}K`;
    }
    return value.toString();
  };

  return (
    <div style={{ width: '100%', backgroundColor: 'white', padding: '16px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
      <ResponsiveContainer width="100%" height={height - 100}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12 }}
            interval={Math.floor(data.length / 10) || 0}
          />
          <YAxis
            yAxisId="price"
            domain={[minPrice - padding, maxPrice + padding]}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) =>
              currency === 'KRW'
                ? `₩${value.toLocaleString()}`
                : `$${value.toFixed(2)}`
            }
          />
          <Tooltip content={<CustomTooltip currency={currency} />} />
          <Legend />
          
          {/* Close price line for candlestick effect */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Close"
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="high"
            stroke="#10b981"
            strokeWidth={1}
            dot={false}
            strokeDasharray="3 3"
            name="High"
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="low"
            stroke="#ef4444"
            strokeWidth={1}
            dot={false}
            strokeDasharray="3 3"
            name="Low"
          />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Volume chart below */}
      <ResponsiveContainer width="100%" height={100}>
        <ComposedChart
          data={chartData}
          margin={{ top: 0, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12 }}
            interval={Math.floor(data.length / 10) || 0}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={formatVolume}
          />
          <Tooltip
            formatter={(value: number) => [formatVolume(value), 'Volume']}
          />
          
          {/* Volume bars with color based on price change */}
          <Bar dataKey="volume" name="Volume">
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                opacity={0.6}
              />
            ))}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
